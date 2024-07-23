# GlobalVariable, TemplateVariable, ProcessVariable
from typing import Optional

from database import models, constants
from pydantic import PrivateAttr, constr, conint
from sqlalchemy_pydantic_orm import ORMBaseSchema


# Base, Create, Get, Update GlobalVariable
# noinspection DuplicatedCode
class GlobalVariableBase(ORMBaseSchema):
    name: constr(min_length=1, max_length=constants.LENGTH_VARIABLE_NAME)
    input: constr(min_length=0, max_length=constants.LENGTH_VARIABLE_NAME)

    _orm_model = PrivateAttr(models.GlobalVariable)


class GlobalVariableCreate(GlobalVariableBase):
    pass


class GlobalVariableGet(GlobalVariableBase):
    id: conint(ge=0)


class GlobalVariableColorGet(GlobalVariableBase):
    id: conint(ge=0)
    color: Optional[constr(min_length=0, max_length=constants.LENGTH_HEX_COLOR)]


class GlobalVariableUpdate(GlobalVariableBase):
    id: Optional[conint(ge=0)]


# Base, Create, Get, Update TemplateVariable
# noinspection DuplicatedCode
class TemplateVariableBase(ORMBaseSchema):
    name: constr(min_length=1, max_length=constants.LENGTH_VARIABLE_NAME)
    input: constr(min_length=0, max_length=constants.LENGTH_VARIABLE_NAME)

    _orm_model = PrivateAttr(models.TemplateVariable)


class TemplateVariableCreate(TemplateVariableBase):
    pass


class TemplateVariableGet(TemplateVariableBase):
    id: conint(ge=0)


class TemplateVariableColorGet(TemplateVariableBase):
    id: conint(ge=0)
    color: Optional[constr(min_length=0, max_length=constants.LENGTH_HEX_COLOR)]


class TemplateVariableUpdate(TemplateVariableBase):
    id: Optional[conint(ge=0)]


# Base, Create, Get, Update TemplateVariable
# noinspection DuplicatedCode
class ProcessVariableBase(ORMBaseSchema):
    name: constr(min_length=1, max_length=constants.LENGTH_VARIABLE_NAME)
    input: constr(min_length=0, max_length=constants.LENGTH_VARIABLE_NAME)

    _orm_model = PrivateAttr(models.ProcessVariable)


class ProcessVariableCreate(ProcessVariableBase):
    pass


class ProcessVariableGet(ProcessVariableBase):
    id: conint(ge=0)


class ProcessVariableColorGet(ProcessVariableBase):
    id: conint(ge=0)
    color: Optional[constr(min_length=0, max_length=constants.LENGTH_HEX_COLOR)]


class ProcessVariableUpdate(ProcessVariableBase):
    id: Optional[conint(ge=0)]
