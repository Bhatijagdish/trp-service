from typing import List

from database import constants, crud, schemas
from database.database import db_connection
from routers.chapter import update_chapter
from fastapi import APIRouter, Depends
from pydantic import NonNegativeInt
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/templates/{template_id}/chapters/{chapter_id}/entity/{entity_id}", response_model=schemas.EntityGet)
async def get_entity(
        template_id: NonNegativeInt,
        chapter_id: NonNegativeInt,
        entity_id: NonNegativeInt,
        db: Session = Depends(db_connection)
) -> schemas.EntityGet:
    """**Requests and returns an entity**

    This endpoint returns a specific entity with the settings.

    Args:
        template_id(int): The unique ID from the template.
        chapter_id(int): The unique ID from the chapter.
        entity_id(int): The unique ID from the entity
        db(Request): Request for a connection with the database.

    Returns:
        A dict with the entity.
        Example: {"entity_type": "process", "order_id": 0, "process": {"update_connector": "CmForecast",
                 "inherits_process_id": null, "entity_id": 2, "name": "kijken of het lukt", "description": "werkt dit",
                 "order_number": 0, "last_exported": "string", "percentage_exported": 0, "amount_successful_groups": 0,
                 "amount_failed_groups": 0, "id": 180}, "note": null, "id": 2 }

    Raises:
        DatabaseError(422): This happens when their doesn't exist an entity in the database with the provided entity_id.
    """
    return await crud.get_entity(db, template_id, chapter_id, entity_id)


@router.post("/templates/{template_id}/chapters/{chapter_id}/entity", response_model=schemas.EntityGet)
async def create_entity(
        template_id: NonNegativeInt,
        chapter_id: NonNegativeInt,
        entity: schemas.EntityCreate,
        db: Session = Depends(db_connection)
) -> schemas.EntityGet:
    """**Creates a new process or note.**

    This endpoint creates a new process or note. First it creates a entity where the kind of entity and order_id is
    stored.

    Args:
        template_id(int): The unique ID from the template.
        chapter_id(int): The unique ID from the chapter.
        entity(Request): Post request JSON containing the entity settings.
        db(Request): Request for a connection with the database.

    Returns:
        A dict with the entity settings.
        Example: {"entity_type": "process", "order_id": 0, "process": {"update_connector": "CmForecast",
                 "inherits_process_id": null, "entity_id": 2, "name": "kijken of het lukt", "description": "werkt dit",
                 "order_number": 0, "last_exported": "string", "percentage_exported": 0, "amount_successful_groups": 0,
                 "amount_failed_groups": 0, "id": 180}, "note": null, "id": 2 }

    Raises:
        DatabaseError(422): This happens when no note or process is given in the JSON or both are given. The error can
        also occur when the chapter doesn't exist in the database with the provided chapter_id.
    """
    return await crud.create_entity(db, template_id, chapter_id, entity)


@router.delete("/templates/{template_id}/chapters/{chapter_id}/entity/{entity_id}", response_model=schemas.EntityGet)
async def delete_entity(
        template_id: NonNegativeInt,
        chapter_id: NonNegativeInt,
        entity_id: NonNegativeInt,
        db: Session = Depends(db_connection)
) -> schemas.EntityGet:
    """**Deletes a process or note.**

    This endpoint deletes all the settings of a process or note and the process and note itself.

    Args:
        template_id(int): The unique ID from the template.
        chapter_id(int): The unique ID from the chapter.
        entity_id(int): The unique ID from the entity.
        db(Request): Request for a connection with the database.

    Returns:
        A dict with the entity settings.
        Example: {"entity_type": "process", "order_id": 0, "process": {"update_connector": "CmForecast",
                 "inherits_process_id": null, "entity_id": 2, "name": "kijken of het lukt", "description": "werkt dit",
                 "order_number": 0, "last_exported": "string", "percentage_exported": 0, "amount_successful_groups": 0,
                 "amount_failed_groups": 0, "id": 180}, "note": null, "id": 2 }

    Raises:
        DatabaseError(422): This happens when their doesn't exist an entity in the database with the provided entity_id.
    """
    return await crud.delete_entity(db, template_id, chapter_id, entity_id)


@router.put("/templates/{template_id}/chapters/{chapter_id}/entity/{entity_id}", response_model=schemas.EntityGet)
async def update_entity(
        template_id: NonNegativeInt,
        chapter_id: NonNegativeInt,
        entity_id: NonNegativeInt,
        entity: schemas.EntityUpdate,
        db: Session = Depends(db_connection),
):
    """**Updates the entity settings.**

    This endpoint updates the entity settings. It replaces the old settings with the new settings.

    Args:
        template_id(int): The unique ID from the template.
        chapter_id(int): The unique ID from the chapter.
        entity_id(int): The unique ID from an entity.
        entity(Request): Post request JSON containing the entity settings.
        db(Request): Request for a connection with the database.

    Returns:
        A dict with the new entity settings.
        Example: {"entity_type": "process", "order_id": 0, "process": {"update_connector": "CmForecast",
                 "inherits_process_id": null, "entity_id": 2, "name": "kijken of het lukt", "description": "werkt dit",
                 "order_number": 0, "last_exported": "string", "percentage_exported": 0, "amount_successful_groups": 0,
                 "amount_failed_groups": 0, "id": 180}, "note": null, "id": 2 }

    Raises:
        DatabaseError(422): This happens when their doesn't exist an entity in the database with the provided entity_id.
    """
    return await crud.update_entity(db, template_id, chapter_id, entity_id, entity)


@router.put("/templates/{template_id}/chapters/{chapter_id}/entity", response_model=List[schemas.EntityGet])
async def update_entities(
        template_id: NonNegativeInt,
        chapter_id: NonNegativeInt,
        entities: List[schemas.EntityUpdate],
        db: Session = Depends(db_connection),
):
    """****
    # houden, om alle notities te updaten als de knop template refreshen wordt geklikt.
    """
    return await crud.update_entities(db, template_id, chapter_id, entities)


@router.put("/templates/{template_id}/chapters/{chapter_id}/entity/{entity_id}/move_entity",
            response_model=schemas.MoveEntityToChapter)
async def move_entity_to_chapter(
        template_id: NonNegativeInt,
        chapter_id: NonNegativeInt,
        entity_id: NonNegativeInt,
        entity: schemas.MoveEntityToChapter,
        db: Session = Depends(db_connection),
):
    return await crud.move_entity_to_chapter(db, template_id, chapter_id, entity_id, entity)


@router.get("/templates/{template_id}/processes", response_model=List[schemas.ProcessGeneralGet], deprecated=True)
async def get_processes(
        template_id: NonNegativeInt,
        skip: NonNegativeInt = constants.DEFAULT_SKIP,
        take: NonNegativeInt = constants.DEFAULT_TAKE,
        db: Session = Depends(db_connection),
):
    """**Requests and returns all the processes from a template.**

    This endpoint returns all the settings and from the different processes.

    Args:
        template_id(int): The unique ID from the template.
        skip(int): Skips over a specified number of rows in the database.
        take(int): Returns the given number of rows from the database table.
        db(Request): Request for a connection with the database.

    Returns:
        A list with dictionaries with all the settings from the different processes.
        Example: [{"inherits_process_id": 0, "name": "Forecast", "description": "forecast", "inherit_settings": true,
                 "inherit_sources": true, "id": 0, "update_connector": "CmForecast"},...]
    """
    return await crud.get_processes(db, template_id, skip, take)


# This function is by my knowledge not necessary anymore. Let's wait a little time before we remove this one.

# @router.post("/templates/{template_id}/processes", response_model=schemas.ProcessGeneralGet, deprecated=True)
# async def create_process(
#         template_id: NonNegativeInt, process: schemas.ProcessGeneralCreate, db: Session = Depends(db_connection)
# ):
#     """**Creates a new process.**
#
#     This endpoint creates a new process and returns the created process.
#
#     Args:
#         template_id(int): The unique ID from the template.
#         process(Request): Post request JSON containing the process settings.
#         db(Request): Request for a connection with the database.
#
#     Returns:
#         A dict with the process settings.
#         Example: {"inherits_process_id": 0, "name": "Forecast", "description": "forecast", "inherit_settings": true,
#                  "inherit_sources": true, "id": 0, "update_connector": "CmForecast"}
#     """
#     return await crud.create_process(db, template_id, process)


@router.get("/templates/{template_id}/processes/{process_id}", response_model=schemas.ProcessGeneralGet)
async def get_process_general(
        template_id: NonNegativeInt, process_id: NonNegativeInt, db: Session = Depends(db_connection)
):
    """**Requests and returns a process.**

    This endpoint returns all te settings from a specific process.

    Args:
        template_id(int): The unique ID from the template.
        process_id(int): The unique ID from the process.
        db(Request): Request for a connection with the database.

    Returns:
        A dict with the process settings.
        Example: {"inherits_process_id": 0, "name": "Forecast", "description": "forecast", "inherit_settings": true,
                 "inherit_sources": true, "id": 0, "update_connector": "CmForecast"}

    Raises:
        #ToDo
    """
    return await crud.get_process_general(db, template_id, process_id)


@router.post("/templates/{template_id}/chapters/{chapter_id}/{process_id}", response_model=schemas.EntityGet,
             deprecated=True)
async def update_process_to_chapter(template_id, chapter_id, process_id, db: Session = Depends(db_connection)):
    """**Sets an existing process in a chapter..**

    This endpoint moves a process to an entity to support the new dashboard.

    Args:
        template_id(int): The unique ID from the template.
        chapter_id(int): The unique ID from the chapter.
        process_id(int): The unique ID from the process.
        db(Request): Request for a connection with the database.

    Returns:
        A dict with the created Entity.
        Example: {"entity_type": "process", "order_id": 0, "process": {"update_connector": "CmForecast",
                 "inherits_process_id": null, "entity_id": 2, "name": "kijken of het lukt", "description": "werkt dit",
                 "order_number": 0, "last_exported": "string", "percentage_exported": 0, "amount_successful_groups": 0,
                 "amount_failed_groups": 0, "id": 180}, "note": null, "id": 2 }
    """
    return await crud.update_to_chapters(db, template_id, chapter_id, process_id)


@router.put("/templates/{template_id}/processes/{process_id}", response_model=schemas.ProcessGeneralGet)
async def update_process_general(
        template_id: NonNegativeInt,
        process_id: NonNegativeInt,
        process: schemas.ProcessGeneralUpdate,
        db: Session = Depends(db_connection),
):
    """**Updates the process settings.**

    This endpoint updates the process settings. It replaces the old settings with the new settings.

    Args:
        template_id(int): The unique ID from the template.
        process_id(int): The unique ID from the process.
        process(Request): Post request JSON containing the new process settings.
        db(Request): Request for a connection with the database.

    Returns:
        A dict with the new process settings.
        Example: {"inherits_process_id": 0, "name": "Forecast", "description": "forecast", "inherit_settings": true,
                 "inherit_sources": true, "id": 0, "update_connector": "CmForecast"}
    """
    return await crud.update_process_general(db, template_id, process_id, process)


@router.delete("/templates/{template_id}/processes/{process_id}", response_model=schemas.ProcessGeneralGet)
async def delete_process(template_id: NonNegativeInt, process_id: NonNegativeInt, db: Session = Depends(db_connection)):
    """**Delete a process.**

    This endpoint deletes all the settings and the process.

    Args:
        template_id(int): The unique ID from the template.
        process_id(int): The unique ID from the process.
        db(Request): Request for a connection with the database.

    Returns:
        A dict with the deleted process settings.
        Example: {"inherits_process_id": 0, "name": "Forecast", "description": "forecast", "inherit_settings": true,
                 "inherit_sources": true, "id": 0, "update_connector": "CmForecast"}
    """
    return await crud.delete_process(db, template_id, process_id)


@router.get("/templates/{template_id}/processes/{process_id}/dashboard", response_model=schemas.ProcessDashboardGet)
async def get_process_dashboard(
        template_id: NonNegativeInt,
        process_id: NonNegativeInt,
        inheritance: bool = True,
        db: Session = Depends(db_connection),
):
    """**Requests and returns a process configurations**

    This endpoint returns all the configurations from a specific process.

    Args:
        template_id (int): The unique ID from the template.
        process_id (int): The unique ID from the process.
        inheritance (bool): If inheritance should be used.
        db(Request): Request for a connection with the database.

    Returns:
        A dict with with all the configurations.
        Example: {"update_connector": "string", "inherit_settings": false, "inherit_sources": false, "id": 0,
        "process_settings": {"rows_function": "string", "group_size": 0, "row_settings_parameters":
        [{"parameter_name": "string", "input": "string", "id": 0}]}, "data_sources": [{"get_connector": "string",
        "id": 0},...], "fields": [{"field_code": "string", "field_label": "string", "inherit": true, "grouped": true,
        "id": 0, "functions": [{"method_id": 0, "id": 0, "parameters": [{"parameter_name": "string", "input": "string",
        "id": 0}]},...], "custom_row_values": [{"row": 0, "input": "string", "id": 0}]},...]}
    """
    return await crud.get_process_dashboard(db, template_id, process_id, inheritance)


#


@router.put("/templates/{template_id}/processes/{process_id}/dashboard", response_model=schemas.ProcessDashboardGet)
async def update_process_dashboard(
        template_id: NonNegativeInt,
        process_id: NonNegativeInt,
        data: schemas.ProcessDashboardUpdate,
        db: Session = Depends(db_connection),
):
    """**Updates the process configurations.**

    This endpoint updates the process configurations. It replace the old configurations with the new configurations.

    Args:
        template_id(int): The unique ID from the template.
        process_id(int): The unique ID from the process.
        data(Request): Data used to update the process.
        db(Request): Request for a connection with the database.

    Returns:
        A dict with the new process configurations.
        Example: {"update_connector": "string", "inherit_settings": false, "inherit_sources": false, "id": 0,
        "process_settings": {"rows_function": "string", "group_size": 0, "row_settings_parameters":
        [{"parameter_name": "string", "input": "string", "id": 0}]}, "data_sources": [{"get_connector": "string",
        "id": 0},...], "fields": [{"field_code": "string", "field_label": "string", "inherit": true, "grouped": true,
        "id": 0, "functions": [{"method_id": 0, "id": 0, "parameters": [{"parameter_name": "string", "input": "string",
        "id": 0}]},...], "custom_row_values": [{"row": 0, "input": "string", "id": 0}]},...]}
    """
    return await crud.update_process_dashboard(db, template_id, process_id, data)
