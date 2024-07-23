from typing import List

from database import constants, crud, models, schemas
from errors import DatabaseError, ErrorCode
from sqlalchemy.orm import Session


async def check_available_process_template(db: Session, template_id: int, process_id: int):
    """**Checks if the asked process is available in the provided template.**

    By calling this function you will check if the provided process exist in combination with the provided template.

    Args:
        db(Connection): Connection with the database.
        template_id(int): The unique ID from the template.
        process_id(int): The unique ID from a process.

    Returns:
        A database models object.
        Example: <database.models.core.Process object at 0x000001C605BDCF40>

    Raises:
        DatabaseError(404): This happens when the process is not found in combination with the provided template_id
        in the database.
    """
    await crud.check_available_template(db, template_id)
    db_process = db.query(models.Process).filter_by(template_id=template_id, id=process_id).first()
    if not db_process:
        raise DatabaseError(error_code=ErrorCode.U0003, msg_args=(process_id, template_id), status_code=404)
    return db_process


async def check_available_process(db: Session, process_id: int):
    """**Check if process exists in the database.**

    By calling this function you will check if the process exists in the database.

    Args:
        db(Connection): Connection with the database.
        process_id(int): The unique ID from a process.

    Returns:
        A database modals object.
        Example: <database.models.core.Process object at 0x000001C605BDCF40>

    Raises:
        DatabaseError(404): This happens when the process is not found.
    """
    db_process = db.query(models.Process).filter_by(id=process_id).first()
    if not db_process:
        raise DatabaseError(error_code=ErrorCode.U0002, msg_args=(process_id,), status_code=404)
    return db_process


async def get_processes(
        db: Session, template_id: int, skip: int = constants.DEFAULT_SKIP, take: int = constants.DEFAULT_TAKE
) -> List[models.Process]:
    """**Returns all the processes from a template that are in the database.**

    By calling this function you will get amount of processes between skip and take from a specific template.

    Args:
        db(Connection): Connection with the database.
        template_id(int): The unique ID from the template.
        skip(int): Skips over a specified number of rows in the database.
        take(int): Returns the given number of rows from the database table.

    Returns:
        A list with dictionaries with all the setting from the different processes.
        Example: [{"inherits_process_id": 0, "name": "Forecast", "description": "forecast", "inherit_settings": true,
                 "inherit_sources": true, "id": 0, "update_connector": "CmForecast"},...]
    """
    await crud.check_available_template(db, template_id)
    return db.query(models.Process).filter_by(template_id=template_id).offset(skip).limit(take).all()


async def get_process_general(db: Session, template_id: int, process_id: int) -> models.Process:
    """**Returns a specific process from the database.**

    By calling this function you will get a specific process that referenced to you given process_id and template_id.

    Args:
        db(Connection): Connection with the database.
        template_id(int): The unique ID from the template.
        process_id(int): The unique ID from the process.

    Returns:
        A dict with the process settings.
        Example: {"inherits_process_id": 0, "name": "Forecast", "description": "forecast", "inherit_settings": true,
                 "inherit_sources": true, "id": 0, "update_connector": "CmForecast"}
    """
    return await check_available_process_template(db, template_id, process_id)


async def update_process_general(
        db: Session, template_id: int, process_id: int, process: schemas.ProcessGeneralUpdate
) -> models.Process:
    """**Updates the process settings.**

    By calling this function you will update the settings for a process.

    Args:
        db(Connection): Connection with the database.
        template_id(int): The unique ID from the template.
        process_id(int): The unique ID from the process.
        process(Request): Request for a pydantic schema with the process settings.

    Returns:
        A dict with the new process settings.
        Example: {"inherits_process_id": 0, "name": "Forecast", "description": "forecast", "inherit_settings": true,
                 "inherit_sources": true, "id": 0, "update_connector": "CmForecast"}
    """
    db_process = await check_available_process_template(db, template_id, process_id)
    process.orm_update(db, db_process)
    db.commit()
    db.refresh(db_process)
    return db_process


# This function is by my knowledge not necessary anymore. Let's wait a little time before we remove this one.

# async def update_to_chapters(db: Session, template_id: int, chapter_id: int, process_id: int) -> schemas.EntityGet:
#     """**Sets an existing process in a chapter**
#
#     By calling this function a new entity is created with the new process. This new created entity is put below the
#     chapter with the provided chapter_id.
#
#     Args:
#         db(Connection): Connection with the database.
#         template_id(int): The unique ID from the template.
#         chapter_id(int): The unique ID from the chapter.
#         process_id(int): The unique ID from the process.
#
#
#     """
#     db_process = await check_available_process_template(db, template_id, process_id)
#     if db_process.entity_id is not None:
#         raise DatabaseError(error_code=ErrorCode.B0014)
#     schema_db_process = schemas.ProcessGeneralGet.from_orm(db_process)
#     db_chapter = await crud.get_chapter(db, template_id, chapter_id)
#     schema_db_chapter = schemas.ChapterAndEntity.from_orm(db_chapter)
#
#     new_entity_model = models.Entity(entity_type="process", order_id=len(schema_db_chapter.entities))
#     new_entity = schemas.EntityCreate.from_orm(new_entity_model)
#     db_new_entity = new_entity.orm_create(chapter_id=chapter_id)
#     db.add(db_new_entity)
#     db.commit()
#     db.refresh(db_new_entity)
#     schema_db_process.entity_id = db_new_entity.id
#     await update_process_general(db, template_id, process_id, schema_db_process)
#     return db_new_entity


async def delete_process(db: Session, template_id: int, process_id: int) -> models.Process:
    """**Deletes a process.**

    By calling this function a process will be deleted. The given process_id will tell you what process you want to
    delete.

    Args:
        db(Connection): Connection with the database.
        template_id(int): The unique ID from the template.
        process_id(int): The unique ID from the process.

    Returns:
        A dict with the deleted process settings.
        Example: {"inherits_process_id": 0, "name": "Forecast", "description": "forecast", "inherit_settings": true,
                 "inherit_sources": true, "id": 0, "update_connector": "CmForecast"}

    Raises:
        HTTPException(404): This happens when their doesn't exist a template in the database with the provided
        template_id or when their doesn't exist a process with the provided process_id under the template.
    """
    db_template = await crud.check_available_template(db, template_id)
    db_process = await check_available_process_template(db, template_id, process_id)
    if db_template.inheritable:
        inherited_processes = db.query(models.Process).filter_by(inherits_process_id=db_process.id).all()
        if inherited_processes:
            raise DatabaseError(error_code=ErrorCode.U0006)
    db.delete(db_process)
    db.commit()
    return db_process


async def get_process_dashboard(
        db: Session, template_id: int, process_id: int, inheritance: bool = True
) -> schemas.ProcessDashboardGet:
    """**Returns all the process configurations.**

    By calling this function you will get a specific process that referenced to you given process_id and template_id.
    You will get all the configurations for the fields.

    Args:
        db(Connection): Connection with the database.
        template_id(int): The unique ID from the template.
        process_id(int): The unique ID from the process.
        inheritance: If inheritance should be used.

    Returns:
        A dict with all the configurations.
        Example: {"update_connector": "string", "inherit_settings": false, "inherit_sources": false, "id": 0,
        "process_settings": {"rows_function": "string", "group_size": 0, "row_settings_parameters":
        [{"parameter_name": "string", "input": "string", "id": 0}]}, "data_sources": [{"get_connector": "string",
        "id": 0},...], "fields": [{"field_code": "string", "field_label": "string", "inherit": true, "grouped": true,
        "id": 0, "functions": [{"method_id": 0, "id": 0, "parameters": [{"parameter_name": "string", "input": "string",
        "id": 0}]},...], "custom_row_values": [{"row": 0, "input": "string", "id": 0}]},...]}
    """
    db_process = await check_available_process_template(db, template_id, process_id)
    process = schemas.ProcessDashboardGet.from_orm(db_process)

    if inheritance and process.inherits_process_id:
        db_base_process = await check_available_process(db, process.inherits_process_id)
        base_process = schemas.ProcessDashboardGet.from_orm(db_base_process)
        if process.process_settings:
            process.process_settings = base_process.process_settings
        for datasource in process.data_sources:
            if datasource.inherit:
                process.data_sources = base_process.data_sources
        for connector in process.connectors:
            connector.connector_settings.inherit = True
            for index, field in enumerate(connector.fields_):
                if field.inherit:
                    try:
                        for base_connector in base_process.connectors:
                            if base_connector.hierarchy == connector.hierarchy:
                                for base_field in base_connector.fields_:
                                    if base_field.field_code == field.field_code:
                                        base_field.id = field.id
                                        base_field.inherit = True
                                        field.functions = base_field.functions
                                        for other_connector in process.connectors:
                                            if other_connector == base_connector:
                                                other_connector.fields_[index] = base_field
                    except StopIteration:
                        field.inherit = False

    return process


async def update_process_dashboard(
        db: Session, template_id: int, process_id: int, process: schemas.ProcessDashboardUpdate
) -> schemas.ProcessDashboardGet:
    """**Updates the process configurations.**

    By calling this function you will update the settings for the fields and the whole process.

    Args:
        db(Connection): Connection with the database.
        template_id(int): The unique ID from the template.
        process_id(int): The unique ID from the process.
        process(Request): Request for a pydantic schema with the process configurations.

    Returns:
        A dict with the new process configurations.
        Example: {"update_connector": "string", "inherit_settings": false, "inherit_sources": false, "id": 0,
        "process_settings": {"rows_function": "string", "group_size": 0, "row_settings_parameters":
        [{"parameter_name": "string", "input": "string", "id": 0}]}, "data_sources": [{"get_connector": "string",
        "id": 0},...], "fields": [{"field_code": "string", "field_label": "string", "inherit": true, "grouped": true,
        "id": 0, "functions": [{"method_id": 0, "id": 0, "parameters": [{"parameter_name": "string", "input": "string",
        "id": 0}]},...], "custom_row_values": [{"row": 0, "input": "string", "id": 0}]},...]}
    """
    db_process = await check_available_process_template(db, template_id, process_id)
    process_old = schemas.ProcessDashboardGet.from_orm(db_process)

    if process_old.inherits_process_id:
        for connector in process.connectors:
            connector.connector_settings.inherit = True
            for field in connector.fields_:
                if field.inherit:
                    try:
                        for aa in process_old.connectors:
                            field_old = next(fld for fld in aa.fields_ if fld.id == field.id)
                            field.functions = field_old.functions

                    except StopIteration:
                        field.functions = []

    process.orm_update(db, db_process)
    db.commit()
    db.refresh(db_process)
    return schemas.ProcessDashboardGet.from_orm(db_process)
