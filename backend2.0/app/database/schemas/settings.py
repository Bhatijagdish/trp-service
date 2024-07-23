# ProcessSettings, ConnectorSettings, RowSettingsParameter
from typing import List, Literal, Optional

from database import models, constants
from pydantic import PrivateAttr, constr, conint
from sqlalchemy_pydantic_orm import ORMBaseSchema


# Base, Create, Get, Update ProcessSettings
class ProcessSettingsBase(ORMBaseSchema):
    send_method: Literal["PUT", "POST", "DELETE", ""]
    inherit: bool

    _orm_model = PrivateAttr(models.ProcessSettings)


class ProcessSettingsCreate(ProcessSettingsBase):
    pass


class ProcessSettingsGet(ProcessSettingsBase):
    id: conint(gt=0)


class ProcessSettingsUpdate(ProcessSettingsBase):
    pass


# Base, Create, Get, Update RowFunctionParameter
# noinspection DuplicatedCode
class RowFunctionParameterBase(ORMBaseSchema):
    name: constr(min_length=1, max_length=constants.LENGTH_PARAMETER_NAME)
    input: str

    _orm_model = PrivateAttr(models.RowFunctionParameter)


class RowFunctionParameterCreate(RowFunctionParameterBase):
    pass


class RowFunctionParameterGet(RowFunctionParameterBase):
    id: conint(gt=0)


class RowFunctionParameterUpdate(RowFunctionParameterBase):
    id: Optional[conint(gt=0)]


# Base, Create, Get, Update ConnectorSettings
class ConnectorSettingsBase(ORMBaseSchema):
    rows_function: constr(min_length=1, max_length=constants.LENGTH_ROWS_FUNCTION_NAME)
    inherit: bool

    _orm_model = PrivateAttr(models.ConnectorSettings)


class ConnectorSettingsCreate(ConnectorSettingsBase):
    row_function_parameters: List[RowFunctionParameterCreate]


class ConnectorSettingsGet(ConnectorSettingsBase):
    id: conint(gt=0)
    row_function_parameters: Optional[List[RowFunctionParameterGet]]


class ConnectorSettingsUpdate(ConnectorSettingsBase):
    id: Optional[conint(gt=0)]
    row_function_parameters: List[RowFunctionParameterUpdate]
