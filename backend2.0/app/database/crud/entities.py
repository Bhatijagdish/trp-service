from typing import List
from database import crud, models, schemas
from routers.profit import update_connector_meta_info
from errors import DatabaseError, ErrorCode
from sqlalchemy.orm import Session


async def get_entity(db: Session, template_id: int, chapter_id: int, entity_id: int):
    """**Returns a specific entity.**

    By calling this function you will get a specific entity that is related to the given chapter_id and entity_id.

    Args:
        db(Connection): Connection with the database.
        template_id(int): The unique ID from the template.
        chapter_id(int): The unique ID from a chapter.
        entity_id(int): The unique ID from an entity.

    Returns:
        A dictionary with the entity.
        Example: {"entity_type": "process", "order_id": 0, "process": {"update_connector": "PtProject",
                 "inherits_process_id": null, "entity_id": 875, "name": "Project made", "description": "",
                 "order_number": 0, "last_exported": "22-08-2022 11:13:43", "percentage_exported": 0,
                 "amount_successful_groups": 0, "amount_failed_groups": 3, "id": 876}, "note": null, "id": 875}

    Raises:
        DatabaseError(400): This happens when a combination with the templated_id, chapter_id and entity_id is not right
         and no entity can be found.
    """
    await crud.get_chapter(db, template_id, chapter_id)
    db_entity = db.query(models.Entity).filter_by(id=entity_id, chapter_id=chapter_id).first()
    if not db_entity:
        raise DatabaseError(error_code=ErrorCode.U0027, msg_args=(entity_id, template_id))
    return db_entity


async def create_entity(
        db: Session,
        template_id: int,
        chapter_id: int,
        entity: schemas.EntityCreate
) -> schemas.EntityGet:
    """**Creates a new entity and in the same time a new process or note.**

    By calling this function a new entity is created and that also includes the creation of a new process or note.

    Args:
        db(Connection): Connection with the database.
        template_id(int): The unique ID from the template.
        chapter_id(int): The unique ID from a chapter.
        entity(Request): Request for a pydantic schema with the required entity settings.

    Returns:
        A dictionary with the new created entity.
        Example: {"entity_type": "process", "order_id": 0, "process": {"update_connector": "PtProject",
                 "inherits_process_id": null, "entity_id": 875, "name": "Project made", "description": "",
                 "order_number": 0, "last_exported": "22-08-2022 11:13:43", "percentage_exported": 0,
                 "amount_successful_groups": 0, "amount_failed_groups": 3, "id": 876}, "note": null, "id": 875}
    Raises:
        DatabaseError(400): This happens when there is not a specific type of entity give. This means that always
        the setting for a new process of for a new note has te be available.
    """
    if entity.process is None and entity.note is None:
        raise DatabaseError(error_code=ErrorCode.F0004)
    if entity.process is not None and entity.note is not None:
        raise DatabaseError(error_code=ErrorCode.F0005)
    db_template = await crud.check_available_template(db, template_id)
    db_chapter = await crud.get_chapter(db, template_id, chapter_id)
    entity_order_id = len(db_chapter.entities)
    if entity.entity_type == "process":
        entity.process.template_id = template_id
        if entity.process.inherits_process_id:
            db_base_process = await crud.check_available_process(db, entity.process.inherits_process_id)
            if None in (db_base_process.data_sources, db_base_process.connectors):
                db_new_process = entity.process.orm_create()
                db_new_process.template_id = template_id
                db_new_process.last_exported = None
                db_new_process.percentage_exported = None
                db_new_process.amount_failed_groups = None
                db_new_process.amount_successful_groups = None
            else:
                new_process = schemas.ProcessDashboardCreate.from_orm(db_base_process)
                new_process.inherits_process_id = db_base_process.id
                new_process.template_id = template_id
                new_process.name = entity.process.name
                new_process.description = entity.process.description
                try:
                    new_process.process_settings.inherit = True
                except AttributeError:
                    pass
                new_process.last_exported = None
                new_process.percentage_exported = None
                new_process.amount_failed_groups = None
                new_process.amount_successful_groups = None
                for data_source in new_process.data_sources:
                    data_source.inherit = False
                for connector in new_process.connectors:
                    connector.connector_settings.inherit = True
                    for field in connector.fields_:
                        field.inherit = True
                        field.custom_row_values = []

                db_new_process = new_process.orm_create()
            entity.process = db_new_process
        else:
            db_new_process = entity.process.orm_create()
            connectors = await update_connector_meta_info(connector=db_new_process.update_connector,
                                                          template=db_template)
            connector_name = connectors["connectors"][0]["name"]
            parameter_min = models.RowFunctionParameter(name="minimale_waarde", input="1")
            parameter_max = models.RowFunctionParameter(name="maximale_waarde", input="1")
            function = models.ConnectorSettings(
                rows_function="random_waarde", inherit=False, row_function_parameters=[parameter_min, parameter_max]
            )

            db_new_process.connectors.append(
                models.Connector(name=connector_name, hierarchy=connector_name, connector_settings=function)
            )
            entity.process = db_new_process

    entity.order_id = entity_order_id
    db_new_entity = entity.orm_create(chapter_id=chapter_id)
    db.add(db_new_entity)
    db.commit()
    db.refresh(db_new_entity)

    return db_new_entity


async def update_entity(
        db: Session, template_id: int, chapter_id: int, entity_id: int, entity: schemas.EntityUpdate
) -> schemas.EntityGet:
    """**Updates the entity settings.**

    By calling this function you will update the settings of an entity.

    Args:
        db(Connection): Connection with the database.
        template_id(int): The unique ID from the template.
        chapter_id(int): The unique ID from a chapter.
        entity_id(int): The unique ID from an entity.
        entity(Request): Request for a pydantic schema with the required entity settings.

    Returns:
        A dictionary with the updated setting of an entity.
        Example: {"entity_type": "process", "order_id": 0, "process": {"update_connector": "PtProject",
                 "inherits_process_id": null, "entity_id": 875, "name": "Project made", "description": "",
                 "order_number": 0, "last_exported": "22-08-2022 11:13:43", "percentage_exported": 0,
                 "amount_successful_groups": 0, "amount_failed_groups": 3, "id": 876}, "note": null, "id": 875}
    """
    await crud.get_chapter(db, template_id, chapter_id)
    db_entity = await get_entity(db, template_id, chapter_id, entity_id)
    entity.orm_update(db, db_entity)
    db.commit()
    db.refresh(db_entity)
    return db_entity


async def update_entities(
        db: Session,
        template_id: int,
        chapter_id: int,
        entities: List[schemas.EntityUpdate]
):
    for entity in entities:
        new_entity = schemas.EntityUpdate.from_orm(entity)
        await update_entity(db, template_id, chapter_id, entity.id, new_entity)
    return entities


async def move_entity_to_chapter(
        db: Session,
        template_id: int,
        chapter_id: int,
        entity_id: int,
        entity: schemas.MoveEntityToChapter
):
    """**Moves an entity to a different chapter.**

    By calling this function an entity is moved from one chapter to another.

    Args:
        db(Connection): Connection with the database.
        template_id(int): The unique ID from the template.
        chapter_id(int): The unique ID from a chapter.
        entity_id(int): The unique ID from an entity.
        entity(Request): Request for a pydantic schema with the required entity settings.

    Returns:
        Returns:
        A dictionary with the moved entity.
        Example: {"entity_type": "process", "order_id": 0, "process": {"update_connector": "PtProject",
                 "inherits_process_id": null, "entity_id": 875, "name": "Project made", "description": "",
                 "order_number": 0, "last_exported": "22-08-2022 11:13:43", "percentage_exported": 0,
                 "amount_successful_groups": 0, "amount_failed_groups": 3, "id": 876}, "note": null, "id": 875}
    """
    db_entity = await get_entity(db, template_id, chapter_id, entity_id)
    db_new_chapter = await crud.get_chapter(db, template_id, entity.chapter_id)
    entities_below_entity = db.query(models.Entity).filter_by(chapter_id=chapter_id).filter(
        models.Entity.order_id > db_entity.order_id).all()
    for ent in entities_below_entity:
        ent.order_id = ent.order_id - 1
        new_entity = schemas.EntityGet.from_orm(ent)
        await update_entity(db, template_id, ent.chapter_id, ent.id, new_entity)

    entity.order_id = len(db_new_chapter.entities)
    entity.orm_update(db, db_entity)
    db.commit()
    db.refresh(db_entity)
    return db_entity


async def delete_entity(db: Session, template_id: int, chapter_id: int, entity_id: int) -> schemas.EntityGet:
    """**Deletes a process or note.**

    By calling this function a process or note will be deleted. The given entity_id will tell you what process or note
    you want to delete.

    Args:
        db(Connection): Connection with the database.
        template_id(int): The unique ID from the template.
        chapter_id(int): The unique ID from the chapter.
        entity_id(int): The unique ID from the entity.

    Returns:
        A dict with the deleted settings.
        Example: {"entity_type": "process", "order_id": 0, "process": {"update_connector": "PtProject",
                 "inherits_process_id": null, "entity_id": 875, "name": "Project made", "description": "",
                 "order_number": 0, "last_exported": "22-08-2022 11:13:43", "percentage_exported": 0,
                 "amount_successful_groups": 0, "amount_failed_groups": 3, "id": 876}, "note": null, "id": 875}

    """
    db_template = await crud.check_available_template(db, template_id)
    db_entity = await get_entity(db, template_id, chapter_id, entity_id)
    if not db_entity:
        raise DatabaseError(error_code=ErrorCode.U0027, msg_args=(entity_id, template_id))

    if db_entity.entity_type == "process":
        if db_template.inheritable:
            inherited_processes = db.query(models.Process).filter_by(inherits_process_id=db_entity.process.id).all()
            if inherited_processes:
                raise DatabaseError(error_code=ErrorCode.U0006)
    entities_below_db_entity = db.query(models.Entity).filter_by(chapter_id=chapter_id).filter(
        models.Entity.order_id > db_entity.order_id).all()

    for entity in entities_below_db_entity:
        entity.order_id = entity.order_id - 1
        new_entity = schemas.EntityGet.from_orm(entity)
        await update_entity(db, template_id, chapter_id, entity.id, new_entity)

    db.delete(db_entity)
    db.commit()
    return db_entity
