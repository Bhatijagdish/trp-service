from typing import List

from database import crud, schemas
from errors import DatabaseError, ErrorCode
from sqlalchemy.orm import Session


async def update_order_ids(db: Session, template_id: int, type_update, chapters: List[schemas.ChapterAndEntity]):
    """**Updates the order of chapters or entities.**

    By calling this function you will be redirected on demand of type_update. There are two possibility, chapters or
    entities.

    Args:
        db(Connection): Connection with the database.
        template_id(int): The unique ID from the template.
        type_update(str): A string with the two possibilities, entities or chapters.
        chapters(Request): Request for a pydantic schema with the chapter settings.

    Returns:
        A list with all the chapters and entities.
        Example: [ChapterAndEntity(..),...]

    Raises:
        DatabaseError(400): This happens when there is no value passed with the variable type_update.
    """
    if type_update == "chapters":
        for chapter in chapters:
            new_chapter = schemas.ChapterUpdate.from_orm(chapter)
            await crud.update_chapter(db, template_id, chapter.id, new_chapter)
    elif type_update == "entities":
        for chapter in chapters:
            for entity in chapter.entities:
                await crud.update_entity(db, template_id, chapter.id, entity.id, entity)
    else:
        raise DatabaseError(error_code=ErrorCode.F0006)
    return chapters
