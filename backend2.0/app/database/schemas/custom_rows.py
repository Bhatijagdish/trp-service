# CustomRowValue
from typing import Optional

from database import models
from pydantic import PrivateAttr, constr, conint
from sqlalchemy_pydantic_orm import ORMBaseSchema


# Base, Create, Get, Update CustomRowValue
class CustomRowValueBase(ORMBaseSchema):
    row: conint(ge=0)
    input: constr(min_length=0)

    _orm_model = PrivateAttr(models.CustomRowValue)


class CustomRowValueCreate(CustomRowValueBase):
    pass


class CustomRowValueGet(CustomRowValueBase):
    id: conint(gt=0)


class CustomRowValueUpdate(CustomRowValueBase):
    id: Optional[conint(gt=0)]
