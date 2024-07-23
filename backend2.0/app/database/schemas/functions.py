# Function, FunctionParameter, Method
from typing import List, Optional

from database import models, constants
from pydantic import PrivateAttr, constr, conint
from sqlalchemy_pydantic_orm import ORMBaseSchema


# Base, Create, Get, Update FunctionParameter
class FunctionParameterBase(ORMBaseSchema):
    name: constr(min_length=1, max_length=constants.LENGTH_PARAMETER_NAME)
    input: constr(min_length=0)

    _orm_model = PrivateAttr(models.FunctionParameter)


class FunctionParameterCreate(FunctionParameterBase):
    pass


class FunctionParameterGet(FunctionParameterBase):
    id: conint(gt=0)


class FunctionParameterUpdate(FunctionParameterBase):
    id: Optional[conint(gt=0)]


# Base, Create, Get, Method
class MethodBase(ORMBaseSchema):
    name: constr(min_length=1, max_length=constants.LENGTH_METHOD_NAME)

    _orm_model = PrivateAttr(models.Method)


# Base, Create, Get, Update Function
class FunctionBase(ORMBaseSchema):
    method_id: conint(gt=0)
    order_id: conint(ge=0)

    _orm_model = PrivateAttr(models.Function)


class FunctionCreate(FunctionBase):
    parameters: List[FunctionParameterCreate]


class FunctionGet(FunctionBase):
    id: conint(gt=0)
    parameters: List[FunctionParameterGet]


class FunctionUpdate(FunctionBase):
    id: Optional[conint(gt=0)]
    parameters: List[FunctionParameterUpdate]


class MethodCreate(MethodBase):
    pass


class MethodGet(MethodBase):
    id: conint(gt=0)


class MethodUpdate(MethodBase):
    id: Optional[conint(gt=0)]
