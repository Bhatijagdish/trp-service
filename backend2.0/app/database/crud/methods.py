from typing import List

from database import models, schemas
from sqlalchemy.orm import Session


async def get_methods(db: Session) -> List[models.Method]:
    """**Returns all the methods from the database.**

    By calling this function you will retrieve all the methods and id's that are in the database.

    Args:
        db(Connection): Connection with the database.

    Returns:
        A list with dictionaries with all the methods and id's.
        Example: [{"name": "bron_waarde", "id": 1 },...]
    """
    return db.query(models.Method).all()


def create_method(db: Session, method: schemas.MethodCreate) -> models.Method:
    """**Ads a new created method to the database.**

    If a new function is written, this function adds that function to the database.

    Args:
        db(Connection): Connection with the database.
        method(Request): Request for a pydantic schema with the required settings.

    Returns:
        A database object with a unique id with the new created method.

    """
    db_method = method.orm_create()
    db.add(db_method)
    db.commit()
    db.refresh(db_method)
    return db_method
