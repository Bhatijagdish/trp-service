from typing import Optional

from database import models, constants
from pydantic import PrivateAttr, constr, conint
from sqlalchemy_pydantic_orm import ORMBaseSchema


# Base, Create, Get, Update Note
class NoteBase(ORMBaseSchema):
    name: constr(min_length=1, max_length=constants.LENGTH_NOTE_NAME)
    description: Optional[constr(min_length=0)]
    last_completed: Optional[constr(min_length=0, max_length=constants.LENGTH_LAST_GENERATED)]
    completed_mark: bool = False

    _orm_model = PrivateAttr(models.Note)


class NoteCreate(NoteBase):
    pass


class NoteGet(NoteBase):
    id: conint(gt=0)


class NoteUpdate(NoteBase):
    id: Optional[conint(gt=0)]
