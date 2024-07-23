from database import constants, crud, schemas
from database.database import db_connection
from fastapi import APIRouter, Depends
from pydantic import NonNegativeInt
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/templates/{template_id}/chapters", response_model=schemas.ChapterAndEntityAndProcess)
async def get_chapters(
        template_id: NonNegativeInt,
        skip: NonNegativeInt = constants.DEFAULT_SKIP,
        take: NonNegativeInt = constants.DEFAULT_TAKE,
        db: Session = Depends(db_connection)
):
    """**Requests and returns all the chapters from a template.**

    This endpoint returns all te chapters and the notes and processes below that chapter.

    Args:
        template_id(int): The unique ID from the template.
        skip(int): Skips over a specified number of rows in the database.
        take(int): Returns the given number of rows from the database table.
        db(Request): Request for a connection with the database.

    Returns:
        A list with dictionaries with all the chapters and de notes and processes below.
        Example: [{"name": "Numero uno", "order_id": 0, "last_completed": "", "completed_mark": false, "entities":
                 [{"entity_type": "process", "order_id": 0, "process": {"update_connector": "CmForecast",
                 "inherits_process_id": null, "entity_id": 2, "name": "kijken of het lukt", "description": "werkt dit",
                 "order_number": 0, "last_exported": "string", "percentage_exported": 0, "amount_successful_groups": 0,
                 "amount_failed_groups": 0, "id": 180}, "note": null, "id": 2 },...]},...]

    Raises:
        DatabaseError(404): This happens when their doesn't exist a template in the database with the provided
        template_id.
    """
    return await crud.get_chapters(db, template_id, skip, take)


@router.get("/templates/{template_id}/chapters/{chapter_id}", response_model=schemas.ChapterAndEntity)
async def get_chapter(template_id: NonNegativeInt, chapter_id: NonNegativeInt, db: Session = Depends(db_connection)):
    """**Requests and returns a chapter.**

    This endpoint returns a specific chapter with all the notes and processes below that chapter.

    Args:
        template_id(int): The unique ID from the template.
        chapter_id(int): The unique ID from the chapter.
        db(Request): Request for a connection with the database.

    Returns:
        A dict with the chapter and all the notes and processes below that chapter.
        Example: {"name": "Numero uno", "order_id": 0, "last_completed": "", "completed_mark": false, "entities":
                 [{"entity_type": "process", "order_id": 0, "process": {"update_connector": "CmForecast",
                 "inherits_process_id": null, "entity_id": 2, "name": "kijken of het lukt", "description": "werkt dit",
                 "order_number": 0, "last_exported": "string", "percentage_exported": 0, "amount_successful_groups": 0,
                 "amount_failed_groups": 0, "id": 180}, "note": null, "id": 2 },...]}

    Raises:
        DatabaseError(404): This happens when their doesn't exist a template in the database with the provided
        template_id or the chapter doesn't exist with the provided chapter in total or in combination with the provided
        template_id.
    """
    return await crud.get_chapter(db, template_id, chapter_id)


@router.post("/templates/{template_id}/chapters", response_model=schemas.ChapterGet)
async def create_chapter(
        template_id: NonNegativeInt,
        chapter: schemas.ChapterCreate,
        db: Session = Depends(db_connection)
):
    """**Creates a chapter.**

    This endpoint creates a new chapter and returns the created chapter.

    Args:
        template_id(int): The unique ID from the template.
        chapter(Request): Post request JSON containing the chapter settings.
        db(Request): Request for a connection with the database.

    Returns:
        A dict with the chapter settings.
        Example: {"name": "string", "order_id": 0, "last_completed": "string", "completed_mark": false, "id": 0}

    Raises:
        DatabaseError(404): This happens when their doesn't exist a template in the database with the provided
        template_id.
    """
    return await crud.create_chapter(db, template_id, chapter)


@router.put("/templates/{template_id}/chapters/{chapter_id}", response_model=schemas.ChapterGet)
async def update_chapter(
        template_id: NonNegativeInt,
        chapter_id: NonNegativeInt,
        chapter: schemas.ChapterUpdate,
        db: Session = Depends(db_connection)
):
    """**Updates the chapter settings.**

    This endpoint updates the chapter settings. It replaces the old settings with the new settings.

    Args:
        template_id(int): The unique ID from the template.
        chapter_id(int): The unique ID from the chapter.
        chapter(Request): Post request JSON containing the chapter settings.
        db(Request): Request for a connection with the database.

    Returns:
        A dict with the new chapter settings.
        Example: {"name": "string", "order_id": 0, "last_completed": "string", "completed_mark": false, "id": 0}

    Raises:
        DatabaseError(404): This happens when their doesn't exist a template in the database with the provided
        template_id or the chapter doesn't exist with the provided chapter in total or in combination with the provided
        template_id.
    """
    return await crud.update_chapter(db, template_id, chapter_id, chapter)


@router.delete("/templates/{template_id}/chapters/{chapter_id}", response_model=schemas.ChapterGet)
async def delete_chapter(
        template_id: NonNegativeInt,
        chapter_id: NonNegativeInt,
        db: Session = Depends(db_connection)
):
    """**Delete a chapter.**

    This endpoint deletes all the settings and the chapter.

    Args:
        template_id(int): The unique ID from the template.
        chapter_id(int): The unique ID from the chapter.
        db(Request): Request for a connection with the database.

    Returns:
        A dict with the deleted chapter settings.
        Example: {"name": "string", "order_id": 0, "last_completed": "string", "completed_mark": false, "id": 0}

    Raises:
        DatabaseError(404): This happens when their doesn't exist a template in the database with the provided
        template_id or the chapter doesn't exist with the provided chapter in total or in combination with the provided
        template_id. Also, if there are still entities existing below the chapter.
    """
    return await crud.delete_chapter(db, template_id, chapter_id)
