from database import constants, crud, models, schemas
from errors import DatabaseError, ErrorCode
from sqlalchemy.orm import Session


async def get_chapters(
        db: Session,
        template_id: int,
        skip: int = constants.DEFAULT_SKIP,
        take: int = constants.DEFAULT_TAKE
):
    """**Returns all the chapters from a template that are in the database.**

    By calling this function you will get amount of chapters between skip and take from a specific template.

    Args:
        db(Connection): Connection with the database.
        template_id(int): The unique ID from the template.
        skip(int): Skips over a specified number of rows in the database.
        take(int): Returns the given number of rows from the database table.

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
    await crud.check_available_template(db, template_id)

    all_processes = db.query(models.Process).filter_by(template_id=template_id).offset(skip).limit(take).all()
    all_chapters = db.query(models.Chapter).filter_by(template_id=template_id).offset(skip).limit(take).all()
    processes = []
    new_processes = []
    for chapter in all_chapters:
        for entity in chapter.entities:
            if entity.entity_type == "process":
                processes.append(entity.process.id)

    for process in all_processes:
        if process.id not in processes:
            new_processes.append(process)
            processes.append(process.id)
    response = {"chapters": all_chapters, "processes": new_processes}
    return response


async def get_chapter(db: Session, template_id: int, chapter_id: int) -> models.Chapter:
    """**Returns the chapter from the database.**

    By calling this function you will get a specific chapter that referenced to you're given chapter_id and template_id.
    You get also the entities that are below the chapter. Entities are processes and notes.

    Args:
        db(Connection): Connection with the database.
        template_id(int): The unique ID from the template.
        chapter_id(int): The unique ID from the chapter.

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
    await crud.check_available_template(db, template_id)
    db_chapter = db.query(models.Chapter).filter_by(template_id=template_id, id=chapter_id).first()
    if not db_chapter:
        raise DatabaseError(error_code=ErrorCode.U0025, msg_args=(chapter_id, template_id), status_code=404)
    return db_chapter


async def create_chapter(db: Session, template_id: int, chapter: schemas.ChapterCreate) -> models.Chapter:
    """**Create a new chapter.**

    By calling this function, it will create a new chapter attached to a template with the provided template_id. All the
    required parameters are visible in the schema.

    Args:
        db(Connection): Connection with the database.
        template_id(int): The unique ID from the template.
        chapter(Request): Request for a pydantic schema with the chapter settings.

    Returns:
        A dict with the chapter settings.
        Example: {"name": "string", "order_id": 0, "last_completed": "string", "completed_mark": false, "id": 0}

    Raises:
        DatabaseError(404): This happens when their doesn't exist a template in the database with the provided
        template_id.
    """
    await crud.check_available_template(db, template_id)
    db_chapters = await get_chapters(db, template_id)

    chapter.order_id = len(db_chapters["chapters"])
    db_chapter: models.Chapter = chapter.orm_create(template_id=template_id)
    db.add(db_chapter)
    db.commit()
    db.refresh(db_chapter)
    return db_chapter


async def update_chapter(
        db: Session,
        template_id: int,
        chapter_id: int,
        chapter: schemas.ChapterUpdate
) -> models.Chapter:
    """**Update the chapter settings.**

    By calling this function you will update the settings for a chapter.

    Args:
        db(Connection): Connection with the database.
        template_id(int): The unique ID from the template.
        chapter_id(int): The unique ID from a chapter.
        chapter(Request): Request for a pydantic schema with the chapter settings.

    Returns:
        A dict with the new chapter settings.
        Example: {"name": "string", "order_id": 0, "last_completed": "string", "completed_mark": false, "id": 0}

    Raises:
        DatabaseError(404): This happens when their doesn't exist a template in the database with the provided
        template_id or the chapter doesn't exist with the provided chapter in total or in combination with the provided
        template_id.
    """
    db_chapter = await get_chapter(db, template_id, chapter_id)
    chapter.orm_update(db, db_chapter)
    db.commit()
    db.refresh(db_chapter)
    return db_chapter


async def delete_chapter(db: Session, template_id: int, chapter_id: int) -> models.Chapter:
    """**Deletes a chapter.**

    By calling this function a chapter will be deleted. The given chapter_id will tell you what chapter you want to
    delete. A chapter can not be deleted if there are still entities below the chapter. Entities are processes and
    notes.

    Args:
        db(Connection): Connection with the database.
        template_id(int): The unique ID from the template.
        chapter_id(int): The unique ID from a chapter.

    Returns:
        A dict with the new chapter settings.
        Example: {"name": "string", "order_id": 0, "last_completed": "string", "completed_mark": false, "id": 0}

    Raises:
        DatabaseError(404): This happens when their doesn't exist a template in the database with the provided
        template_id or the chapter doesn't exist with the provided chapter in total or in combination with the provided
        template_id. Also, if there are still entities existing below the chapter.
    """
    db_chapter = await get_chapter(db, template_id, chapter_id)
    if len(db_chapter.entities) > 0:
        raise DatabaseError(error_code=ErrorCode.U0026, msg_args=(db_chapter.name,))

    chapter_below_chapter = db.query(models.Chapter).filter_by(template_id=template_id).filter(
        models.Chapter.order_id > db_chapter.order_id).all()

    for chapter in chapter_below_chapter:
        chapter.order_id = chapter.order_id - 1
        new_chapter = schemas.ChapterGet.from_orm(chapter)
        await update_chapter(db, template_id, chapter.id, new_chapter)

    db.delete(db_chapter)
    db.commit()
    return db_chapter
