# Template, Process, Connector, Field

from typing import List, Optional

from database import models, constants
from database.schemas import custom_rows, data_sources, functions, settings, notes
from pydantic import Field as SchemaField
from pydantic import PrivateAttr, constr, conint, confloat
from sqlalchemy_pydantic_orm import ORMBaseSchema


# Base, Create, Get, Update Field
class FieldBase(ORMBaseSchema):
    field_code: constr(min_length=1, max_length=constants.LENGTH_FIELD_CODE)
    inherit: bool

    _orm_model = PrivateAttr(models.Field)


class FieldCreate(FieldBase):
    functions: List[functions.FunctionCreate]
    custom_row_values: List[custom_rows.CustomRowValueCreate]


class FieldGet(FieldBase):
    id: conint(gt=0)
    functions: List[functions.FunctionGet]
    custom_row_values: List[custom_rows.CustomRowValueGet]


class FieldUpdate(FieldBase):
    id: Optional[conint(gt=0)]
    functions: List[functions.FunctionUpdate]
    custom_row_values: List[custom_rows.CustomRowValueUpdate]


# Base, Create, Get, Update Connector
class ConnectorBase(ORMBaseSchema):
    name: constr(min_length=1, max_length=constants.LENGTH_UPDATECONNECTOR_NAME)
    hierarchy: constr(min_length=1)

    _orm_model = PrivateAttr(models.Connector)


class ConnectorCreate(ConnectorBase):
    connector_settings: Optional[settings.ConnectorSettingsCreate]
    fields_: Optional[List[FieldCreate]] = SchemaField(..., alias="fields")


class ConnectorGet(ConnectorBase):
    id: conint(gt=0)
    connector_settings: Optional[settings.ConnectorSettingsGet]
    fields_: Optional[List[FieldGet]] = SchemaField(..., alias="fields")


class ConnectorUpdate(ConnectorBase):
    id: Optional[conint(gt=0)]
    connector_settings: Optional[settings.ConnectorSettingsUpdate]
    fields_: Optional[List[FieldUpdate]] = SchemaField(..., alias="fields")


# Base, Create, Get, Update Process
class ProcessBase(ORMBaseSchema):
    _orm_model = PrivateAttr(models.Process)


class ProcessGeneralBase(ProcessBase):
    update_connector: constr(min_length=1, max_length=constants.LENGTH_UPDATECONNECTOR_NAME)
    inherits_process_id: Optional[conint(gt=0)]
    entity_id: Optional[conint(ge=0)]
    name: constr(min_length=1, max_length=constants.LENGTH_PROCESS_NAME)
    description: constr(min_length=0)
    order_number: Optional[conint(ge=0)]
    last_exported: Optional[constr(min_length=0, max_length=constants.LENGTH_LAST_GENERATED)]
    percentage_exported: Optional[confloat(ge=0)]
    amount_successful_groups: Optional[conint(ge=0)]
    amount_failed_groups: Optional[conint(ge=0)]


class ProcessGeneralCreate(ProcessGeneralBase):
    template_id: Optional[conint(ge=0)]


class ProcessGeneralGet(ProcessGeneralBase):
    id: conint(gt=0)


class ProcessGeneralUpdate(ProcessGeneralBase):
    id: Optional[conint(gt=0)]
    template_id: Optional[conint(gt=0)]


class ProcessDashboardBase(ProcessBase):
    pass


class ProcessDashboardCreate(ProcessDashboardBase):
    update_connector: constr(min_length=1, max_length=constants.LENGTH_UPDATECONNECTOR_NAME)
    inherits_process_id: Optional[conint(gt=0)]
    name: constr(min_length=1, max_length=constants.LENGTH_PROCESS_NAME)
    description: constr(min_length=0)
    order_number: conint(ge=0)
    last_exported: Optional[constr(min_length=0, max_length=constants.LENGTH_LAST_GENERATED)]
    percentage_exported: Optional[confloat(ge=0)]
    amount_successful_groups: Optional[conint(ge=0)]
    amount_failed_groups: Optional[conint(ge=0)]
    template_id: Optional[conint(ge=0)]
    process_settings: Optional[settings.ProcessSettingsCreate]
    data_sources: List[data_sources.DataSourceCreate]
    connectors: List[ConnectorCreate]


class ProcessDashboardGet(ProcessDashboardBase):
    id: conint(gt=0)
    inherits_process_id: Optional[conint(gt=0)]
    process_settings: Optional[settings.ProcessSettingsGet]
    data_sources: Optional[List[data_sources.DataSourceGet]]
    connectors: Optional[List[ConnectorGet]]


class ProcessDashboardUpdate(ProcessDashboardBase):
    id: Optional[conint(gt=0)]
    process_settings: settings.ProcessSettingsUpdate
    data_sources: List[data_sources.DataSourceUpdate]
    connectors: List[ConnectorUpdate]


# Base, Create, Get, Update Entity
class EntityBase(ORMBaseSchema):
    entity_type: constr(min_length=1, max_length=constants.LENGTH_ENTITY_TYPE)
    order_id: conint(ge=0)

    _orm_model = PrivateAttr(models.Entity)


class EntityCreate(EntityBase):
    process: Optional[ProcessGeneralCreate]
    note: Optional[notes.NoteCreate]


class EntityProcessCreate(EntityBase):
    process: Optional[ProcessDashboardCreate]
    note: Optional[notes.NoteCreate]


class EntityGet(EntityBase):
    process: Optional[ProcessGeneralGet]
    note: Optional[notes.NoteGet]
    id: conint(gt=0)


class EntityUpdate(EntityBase):
    id: Optional[conint(gt=0)]
    process: Optional[ProcessGeneralUpdate]
    note: Optional[notes.NoteUpdate]


class MoveEntityToChapter(EntityBase):
    chapter_id: conint(gt=0)
    process: Optional[ProcessGeneralUpdate]
    note: Optional[notes.NoteUpdate]


# Base, Create, Get, Update Chapter
class ChapterBase(ORMBaseSchema):
    name: constr(min_length=1, max_length=constants.LENGTH_CHAPTER_NAME)
    order_id: conint(ge=0)
    last_completed: Optional[constr(min_length=0, max_length=constants.LENGTH_LAST_GENERATED)]
    completed_mark: bool = False

    _orm_model = PrivateAttr(models.Chapter)


class ChapterAndEntity(ChapterBase):
    id: conint(gt=0)
    entities: Optional[List[EntityGet]]


class ChapterAndEntityAndProcess(ProcessBase):
    chapters: Optional[List[ChapterAndEntity]]
    processes: Optional[List[ProcessGeneralGet]]


class ChapterCreate(ChapterBase):
    pass


class ChapterAndEntitiesCreate(ChapterBase):
    entities: Optional[List[EntityProcessCreate]]


class ChapterGet(ChapterBase):
    id: conint(gt=0)


class ChapterUpdate(ChapterBase):
    id: Optional[conint(gt=0)]


# Base, Create, Get, Update Template
class TemplateBase(ORMBaseSchema):
    profit_endpoint: constr(min_length=1)
    token: Optional[constr(min_length=1)]
    name: constr(min_length=1, max_length=constants.LENGTH_TEMPLATE_NAME)
    template_number: Optional[conint(gt=0)]
    demo_environment: bool

    _orm_model = PrivateAttr(models.Template)


class TemplateCreate(TemplateBase):
    inheritable: bool


class TemplateGet(TemplateBase):
    id: conint(gt=0)
    inheritable: bool


class TemplateUpdate(TemplateBase):
    id: Optional[conint(gt=0)]


class SqlBase(ORMBaseSchema):
    name: constr(min_length=1, max_length=constants.LENGTH_SQL_NAME)
    statement: constr()

    _orm_modal = PrivateAttr(models.Sql)


class SqlGet(SqlBase):
    id: conint(gt=0)


class SqlUpdate(SqlBase):
    id: conint(gt=0)


class SqlCreate(SqlBase):
    pass


class BatchBase(ORMBaseSchema):
    name: constr(min_length=1, max_length=constants.LENGTH_BATCH_NAME)
    statement: constr()

    _orm_modal = PrivateAttr(models.Batch)


class BatchGet(BatchBase):
    id: conint(gt=0)


class BatchUpdate(BatchBase):
    id: conint(gt=0)


class BatchCreate(BatchBase):
    pass


class SqlBatchBase(ORMBaseSchema):
    sql: Optional[conint(gt=0)]
    batch: Optional[conint(gt=0)]
    type: constr(min_length=1, max_length=constants.LENGTH_SQL_BATCH_ENTITY_TYPE)
    template: conint(gt=0)
    order_number: conint(ge=0)

    _orm_modal = PrivateAttr(models.SqlBatchEntity)


class SqlBatchUpdate(SqlBatchBase):
    id: Optional[conint(gt=0)]


class SqlBatchGet(SqlBatchBase):
    sql: Optional[conint(gt=0)]
    batch: Optional[conint(gt=0)]
    template: Optional[conint(gt=0)]
    id: Optional[conint(gt=0)]


class SqlBatchCreate(SqlBatchBase):
    sql: Optional[SqlCreate]
    batch: Optional[BatchCreate]
    type: constr(min_length=1, max_length=constants.LENGTH_SQL_BATCH_ENTITY_TYPE)
    template: List[conint(gt=0)]


class SqlBatchEntitiesGet(SqlBatchBase):
    sql: Optional[List[SqlBase]]
    batch: Optional[List[BatchBase]]
    template: List[conint(gt=0)]
