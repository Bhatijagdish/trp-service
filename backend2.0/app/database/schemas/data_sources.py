# DataSource, Source, FilterSource, GetConnector, CSVFile, FieldFilterRow, FieldFilter
from typing import List, Optional

from database import models, constants
from pydantic import PrivateAttr, constr, conint
from sqlalchemy_pydantic_orm import ORMBaseSchema


# Base, Create, Get, Update FieldFilter
class FieldFilterBase(ORMBaseSchema):
    operator: constr(min_length=1, max_length=constants.LENGTH_OPERATOR)
    input: constr(min_length=1, max_length=constants.LENGTH_FIELD_FILTER_VALUE)

    _orm_model = PrivateAttr(models.FieldFilter)


class FieldFilterCreate(FieldFilterBase):
    pass


class FieldFilterGet(FieldFilterBase):
    id: conint(gt=0)


class FieldFilterUpdate(FieldFilterBase):
    id: Optional[conint(gt=0)]


# Base, Create, Get, Update FieldFilterRow
class FieldFilterRowBase(ORMBaseSchema):
    field_id: constr(min_length=1, max_length=constants.LENGTH_GETCONNECTOR_FIELD_ID)

    _orm_model = PrivateAttr(models.FieldFilterRow)


class FieldFilterRowCreate(FieldFilterRowBase):
    field_filters: List[FieldFilterCreate]


class FieldFilterRowGet(FieldFilterRowBase):
    id: conint(gt=0)
    field_filters: List[FieldFilterGet]


class FieldFilterRowUpdate(FieldFilterRowBase):
    id: Optional[conint(gt=0)]
    field_filters: List[FieldFilterUpdate]


# Base, Create, Get, Update GetConnector
class GetConnectorBase(ORMBaseSchema):
    name: constr(min_length=1, max_length=constants.LENGTH_GETCONNECTOR_NAME)

    _orm_model = PrivateAttr(models.GetConnector)


# noinspection DuplicatedCode
class GetConnectorCreate(GetConnectorBase):
    pass


class GetConnectorGet(GetConnectorBase):
    id: conint(gt=0)


class GetConnectorUpdate(GetConnectorBase):
    id: Optional[conint(gt=0)]


# Base, Create, Get, Update CSVFile
class CSVFileBase(ORMBaseSchema):
    file_name: constr(min_length=1, max_length=constants.LENGTH_CSV_FILE_NAME)
    file: str

    _orm_model = PrivateAttr(models.CSVFile)


class CSVFileCreate(CSVFileBase):
    pass


class CSVFileGet(CSVFileBase):
    id: conint(gt=0)


class CSVFileUpdate(CSVFileBase):
    id: Optional[conint(gt=0)]


# Base, Create, Get, Update Source
class SourceBase(ORMBaseSchema):
    type_source: constr(min_length=1, max_length=constants.LENGTH_TYPE_SOURCE)

    _orm_model = PrivateAttr(models.Source)


class SourceCreate(SourceBase):
    filter_source_id: Optional[conint(gt=0)]
    csv_file: Optional[CSVFileCreate]
    get_connector: Optional[GetConnectorCreate]


class SourceGet(SourceBase):
    id: conint(gt=0)
    csv_file: Optional[CSVFileGet]
    get_connector: Optional[GetConnectorGet]


class SourceUpdate(SourceBase):
    id: Optional[conint(gt=0)]
    filter_source_id: Optional[conint(gt=0)]
    csv_file: Optional[CSVFileUpdate]
    get_connector: Optional[GetConnectorUpdate]


# Base, Create, Get, Update FilterSource
class FilterSourceBase(ORMBaseSchema):
    filter_field: constr(min_length=1, max_length=constants.LENGTH_FILTER_FIELD)

    _orm_model = PrivateAttr(models.FilterSource)


class FilterSourceCreate(FilterSourceBase):
    source: SourceCreate


class FilterSourceGet(FilterSourceBase):
    id: conint(gt=0)
    source: SourceGet


class FilterSourceUpdate(FilterSourceBase):
    id: Optional[conint(gt=0)]
    source: SourceUpdate


# Base, Create, Get, Update DataSource
class DataSourceBase(ORMBaseSchema):
    repeatable: bool
    inherit: bool = None
    custom_name: Optional[constr(min_length=0, max_length=constants.LENGTH_CUSTOM_NAME)]

    _orm_model = PrivateAttr(models.DataSource)


class DataSourceCreate(DataSourceBase):
    source: SourceCreate
    filter_source: Optional[FilterSourceCreate]
    field_filter_rows: Optional[List[FieldFilterRowCreate]]


class DataSourceGet(DataSourceBase):
    id: conint(gt=0)
    source: SourceGet
    filter_source: Optional[FilterSourceGet]
    field_filter_rows: Optional[List[FieldFilterRowGet]]


class DataSourceUpdate(DataSourceBase):
    id: Optional[conint(gt=0)]
    source: SourceUpdate
    filter_source: Optional[FilterSourceUpdate]
    field_filter_rows: Optional[List[FieldFilterRowUpdate]]
