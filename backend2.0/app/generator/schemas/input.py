from typing import Literal, List, Optional, Union

from pydantic import BaseModel, Field as SchemaField

from generator.schemas.functions import FunctionMetaInfo
from profit.schemas import ConnectorMetainfo, UpdateConnectorField


class BaseSchema(BaseModel):
    pass


class ProcessSettings(BaseSchema):
    inherit: bool
    send_method: Literal["GET", "POST", "PUT", "DELETE", ""]


class GetConnector(BaseSchema):
    name: str


class CSVFile(BaseSchema):
    file_name: str
    file: str


class Source(BaseSchema):
    type_source: Literal["csv", "GetConnector"]
    csv_file: Optional[CSVFile]
    get_connector: Optional[GetConnector]

    name: Optional[str]  # Gets set in `Fuel._get_source_data()`


class FilterSource(BaseSchema):
    filter_field: str
    source: Source


class FieldFilter(BaseSchema):
    operator: str
    input: str


class FieldFilterRow(BaseSchema):
    field_id: str
    field_filters: List[FieldFilter]


class DataSource(BaseSchema):
    inherit: bool = None
    repeatable: bool
    source: Source
    filter_source: Optional[FilterSource]
    field_filter_rows: List[FieldFilterRow] = []

    name: Optional[str]  # Gets set in `Engine.apply_source_filtering


class RowFunctionParameter(BaseSchema):
    name: str
    input: str


class ConnectorSettings(BaseSchema):
    inherit: bool
    rows_function: str
    row_function_parameters: List[RowFunctionParameter]


class Parameter(BaseSchema):
    name: str = None
    input: str


class Function(BaseSchema):
    method_id: int
    order_id: int
    parameters: List[Parameter]

    metainfo: Optional[FunctionMetaInfo]  # Gets set in `Fuel._attach_data()`


class CustomRowValue(BaseSchema):
    row: int
    input: str


class Field(BaseSchema):
    field_code: str
    inherit: bool
    functions: List[Function]
    custom_row_values: List[CustomRowValue] = []

    metainfo: Optional[UpdateConnectorField]  # Gets set in `Fuel._attach_data()`


class Connector(BaseSchema):
    name: str
    hierarchy: str
    connector_settings: ConnectorSettings
    fields_: List[Field] = SchemaField(..., alias="fields")

    metainfo: Optional[ConnectorMetainfo]  # Gets set in `Fuel._attach_data()`


class ConfigurationDashboard(BaseSchema):
    update_connector: str
    process_settings: ProcessSettings
    data_sources: List[DataSource]
    connectors: List[Connector]
