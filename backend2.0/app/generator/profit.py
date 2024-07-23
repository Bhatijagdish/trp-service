import json

from loguru import logger

from database.crud import (
    get_global_variables,
    get_process_variables,
    get_template,
    get_template_variables,
    get_methods,
)
from database.database import DatabaseSession
from database.models import Template
from errors import GeneratorError, ProfitError, ErrorCode
from generator.functions.methods import Functions
from generator.functions.utils import compose_functions_metainfo
from generator.schemas.functions import FunctionsMetaInfo
from generator.schemas.input import ConfigurationDashboard, Source
from generator.utils import attr_find, attr_find_get
from generator.variables import Variables
from profit import connections
from profit.schemas import UpdateConnectorMetainfo

PROFIT_GET_SKIP = 0
PROFIT_GET_TAKE = 2000


class Fuel:
    template: Template
    variables: Variables
    functions_metainfo: FunctionsMetaInfo
    metainfo: UpdateConnectorMetainfo

    def __init__(self, db: DatabaseSession, template_id: int, process_id: int, configurations: ConfigurationDashboard):
        self._db = db
        self._template_id = template_id
        self._process_id = process_id
        self.configurations = configurations
        self.source_data = {}
        self.source_metainfo = {}

    async def _get_variables(self):
        db_global_variables = await get_global_variables(self._db, take_dynamic_vars=False)
        db_template_variables = await get_template_variables(self._db, self._template_id, False, False)
        db_process_variables = await get_process_variables(self._db, self._template_id, self._process_id, False)
        self.variables = Variables(db_global_variables, db_template_variables, db_process_variables)

    async def _get_function_metainfo(self):
        db_methods = await get_methods(self._db)
        self.functions_metainfo = compose_functions_metainfo(Functions, db_methods)

    async def _get_update_connector_metainfo(self):
        response = await connections.update_connector_metainfo(
            self.template.profit_endpoint, self.template.token, self.configurations.update_connector
        )
        self.metainfo = UpdateConnectorMetainfo.parse_obj(response)
        self.raw_metainfo = response

    async def _get_source_data(self, source: Source):
        if source.type_source == "GetConnector":
            get_connector = source.get_connector.name
            if get_connector not in self.source_data:
                params = {"skip": PROFIT_GET_SKIP, "take": PROFIT_GET_TAKE}
                get_connector_data = await connections.get_connector_data(
                    self.template.profit_endpoint, self.template.token, get_connector, params
                )
                try:
                    self.source_data[get_connector] = get_connector_data["rows"]
                    self.source_metainfo[get_connector] = await connections.get_connector_metainfo(
                        self.template.profit_endpoint, self.template.token, get_connector
                    )
                except KeyError:
                    logger.info(get_connector)
                    raise ProfitError(error_code=ErrorCode.P0013, msg_args=(get_connector,))

            source.name = get_connector
        elif source.type_source == "csv":
            source_name = source.csv_file.file_name
            meta_info = {}
            if source_name not in self.source_data:
                csv_data = json.loads(source.csv_file.file)
                # csv_data - 1, because last dict of list is empty.
                self.source_data[source_name] = csv_data[:-1]

                new_fields = []
                for key in csv_data[0].keys():
                    new_fields.append({"id": key, "label": key})
                meta_info["name"] = source_name
                meta_info["description"] = source_name
                meta_info["fields"] = new_fields
                self.source_metainfo[source_name] = meta_info
        else:
            raise GeneratorError(ErrorCode.F0001)

    async def _parse_sources(self):
        for data_source in self.configurations.data_sources:
            await self._get_source_data(data_source.source)
            if data_source.filter_source:
                await self._get_source_data(data_source.filter_source.source)

    async def _attach_data(self):
        for connector in self.configurations.connectors:
            connector.metainfo = attr_find(
                iterable=self.metainfo.connectors,
                find_attr="hierarchy",
                find_value=connector.hierarchy,
                error=GeneratorError(ErrorCode.B0005)
            )
            for field in connector.fields_:
                field.metainfo = attr_find(
                    iterable=connector.metainfo.fields_,
                    find_attr="fieldId",
                    find_value=field.field_code,
                    error=GeneratorError(ErrorCode.B0008)
                )
                for function in field.functions:
                    try:
                        function.metainfo = attr_find(
                            iterable=self.functions_metainfo.functions,
                            find_attr="method_id",
                            find_value=function.method_id,
                            error=GeneratorError(ErrorCode.B0009)
                        )
                    except GeneratorError:
                        logger.error(f"method_id {function.method_id} is not (yet) in the Functions class")  # TODO: rm

    async def compose(self):
        self.template = await get_template(self._db, self._template_id)
        await self._get_variables()
        await self._get_function_metainfo()
        await self._get_update_connector_metainfo()
        await self._parse_sources()
        await self._attach_data()
