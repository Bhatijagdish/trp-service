from aiohttp import ClientConnectorError, ContentTypeError, InvalidURL
from loguru import logger

from errors import ErrorCode, ProfitError
from profit import connections
from typing import Dict, List
import json

from database.models.core import Template
from database.models.data_sources import DataSource


async def check_profit_connection(endpoint: str, environment_token: str):
    """**Checks the connection with profit.**

    The function checks if it is possible to make connection with profit with the combination of the endpoint and
    environment_token.

    Args:
        endpoint(str): The server to connect to of profit.
        environment_token(str): The special token that is specific assigned to a server of profit.

    Returns:
        A boolean if the connection is valid.
        Example: True

    Raises:
        ProfitError(400): This happens when the combination of the endpoint and environment_token is not valid.
    """
    try:
        await connections.get_profit_version(endpoint, environment_token)
        return True
    except (InvalidURL, ClientConnectorError, ContentTypeError) as e:
        logger.error(e)
        raise ProfitError(error_code=ErrorCode.P0001)


async def get_filter_field_ids(endpoint, token, source_name, filter_source_name, filter_field_label):
    """**Returns the possible filter-sources and filter fields.**

    By calling this function a selection will be made if there is a possibility to get_connectors based on the same
    fields.

    Args:
        endpoint(str): The server to connect to of profit.
        token(str): The special token that is specific assigned to a server of profit.
        source_name(str): The name of a specific get_connector.
        filter_source_name(str): The name of the filter get_connector.
        filter_field_label(str): The name of the field on which the filtering is based.

    Returns:
        The specific field on which the filtering is possible.
        Example: Verkooprelatie
    """
    source_metainfo = await connections.get_connector_metainfo(endpoint, token, source_name)
    filter_source_metainfo = await connections.get_connector_metainfo(endpoint, token, filter_source_name)
    source_filter_field = next(
        fld["id"] for fld in source_metainfo["fields"] if fld["label"] == filter_field_label
    )
    filter_source_filter_field = next(
        fld["id"] for fld in filter_source_metainfo["fields"] if fld["label"] == filter_field_label
    )
    return source_filter_field, filter_source_filter_field


async def filtering(source_values, filter_values):
    """Returns the values on which the filtering is possible."""
    filtered_values = set()
    for item in source_values:
        if item not in filter_values:
            filtered_values.add(item)
    return filtered_values


async def get_source_length(
        template: Template,
        all_sources: List[DataSource],
        data_source: DataSource
) -> Dict[str, int]:
    """**Returns the amount of rows that are available from the selected get_connectors.**

    By calling this function the amount of rows will be loaded and calculated. This is a difficult process, because
    there is a lot of different kinds of filtering.

    Args:
        template(Modal): The database modal of the specific template.
        all_sources(list): All the sources that are selected in the current process.
        data_source(str): A get_connector from which the rows must be calculated.

    Returns:
        A dictionary with the source and the calculated length.
        Example: {'source': 'DemoData_Active_Forecast_met__status_ve', 'length': 0}

    Raises:
        ProfitError(404): This happens when a get_connector is selected but that get_connector is not available anymore
        in the profit environment.
    """
    length_source = {}
    if data_source.source.type_source == "GetConnector":
        source_name = data_source.source.get_connector.name
        source_data = await connections.get_connector_data(
            template.profit_endpoint, template.token, source_name, {"skip": 0, "take": 10000}
        )
        try:
            source_rows = source_data["rows"]
        except KeyError:
            raise ProfitError(error_code=ErrorCode.P0013, msg_args=(source_name,))
        if filter_source := data_source.filter_source:
            if filter_source.source.type_source == "GetConnector":
                filter_source_name = filter_source.source.get_connector.name
                filter_source_data = await connections.get_connector_data(
                    template.profit_endpoint, template.token, filter_source_name,
                    {"skip": 0, "take": 10000}
                )
                filter_source_rows = filter_source_data["rows"]
                source_filter_field, filter_source_filter_field = await get_filter_field_ids(
                    template.profit_endpoint,
                    template.token,
                    source_name,
                    filter_source_name,
                    filter_source.filter_field
                )
                source_values = set(row[source_filter_field] for row in source_rows)
                filter_values = set(row[filter_source_filter_field] for row in filter_source_rows)

            else:
                source_filter_field = filter_source.filter_field
                filter_source_name = filter_source.source.csv_file.file_name
                filter_source_data = []
                for source in all_sources:
                    if source.source.type_source == "csv" and source.source.csv_file.file_name == filter_source_name:
                        filter_source_data = json.loads(source.source.csv_file.file)
                source_values = set(row[source_filter_field] for row in source_rows)
                filter_values = set(row[source_filter_field] for row in filter_source_data[:-1])

            filtered_values = await filtering(source_values, filter_values)

            source_rows = [row for row in source_rows if row[source_filter_field] in filtered_values]
            source_name += f" - {filter_source_name}"
            length_source["source"] = source_name
            length_source["length"] = len(source_rows)
        else:
            length_source["source"] = source_name
            length_source["length"] = len(source_rows)
    else:
        source_name = data_source.source.csv_file.file_name
        source_rows = json.loads(data_source.source.csv_file.file)
        if filter_source := data_source.filter_source:
            filter_field = filter_source.filter_field
            if filter_source.source.type_source == "GetConnector":
                filter_source_name = filter_source.source.get_connector.name
                filter_source_data = await connections.get_connector_data(
                    template.profit_endpoint, template.token, filter_source_name,
                    {"skip": 0, "take": 10000}
                )
                filter_source_rows = filter_source_data["rows"]
                source_values = set(row[filter_field] for row in source_rows)
                filter_values = set(row[filter_field] for row in filter_source_rows)
                pass
            else:
                filter_source_name = filter_source.source.csv_file.file_name
                filter_source_data = []
                for source in all_sources:
                    if source.source.type_source == "csv" and source.source.csv_file.file_name == filter_source_name:
                        filter_source_data = json.loads(source.source.csv_file.file)
                source_values = set(row[filter_field] for row in source_rows[:-1])
                filter_values = set(row[filter_field] for row in filter_source_data[:-1])

            filtered_values = await filtering(source_values, filter_values)

            source_rows = [row for row in source_rows if row[filter_field] in filtered_values]
            source_name += f" - {filter_source_name}"
            length_source["source"] = source_name
            length_source["length"] = len(source_rows)
        else:
            length_source["source"] = source_name
            length_source["length"] = len(source_rows[:-1])
    return length_source
