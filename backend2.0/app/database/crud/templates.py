from typing import List

from database import constants, crud, models, schemas
from errors import DatabaseError, ErrorCode
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

BIG_TAKE = 5000


async def check_available_template(db: Session, template_id: int):
    """**Checks if the asked templates is present in the database.**

    Args:
        db(Connection): Connection with the database.
        template_id(int): The unique ID from the template.

    Returns:
        A database models object with a unique id.
        Example: <database.models.core.Template object at 0x000001C605BDCF40>

    Raises:
        DatabaseError(404): This happens when the templated is not found in the database.
    """
    db_template = db.query(models.Template).filter_by(id=template_id).first()
    if not db_template:
        raise DatabaseError(error_code=ErrorCode.U0001, msg_args=(template_id,), status_code=404)
    return db_template


# API Requests
async def get_templates(
        db: Session, skip: int = constants.DEFAULT_SKIP, take: int = constants.DEFAULT_TAKE
) -> List[models.Template]:
    """**Returns all the templates from the database.**

    By calling this function you will get amount of templates between skip and take.

    Args:
        db(Connection): Connection with the database.
        skip(int): Skips over a specified number of rows in the database.
        take(int): Returns the given number of rows from the database table.

    Returns:
        A list with dictionaries with all the settings from the templates.
        Example: [{"profit_endpoint": 0, "inheritable": true, "token": "Afas_token", "name": "ERP", "id": 0},...]
    """
    return db.query(models.Template).offset(skip).limit(take).all()


async def create_template(db: Session, template: schemas.TemplateCreate) -> models.Template:
    """**Creates a new template.**

    By calling this function you will create a template. All the required parameters are visible in the schema.
    If you set the parameter "inheritable" to False you will get that all the processes from the Basis Template will be
    copied to you're new template.

    Args:
        db(Connection):  Connection with the database.
        template(Request): Request for a pydantic schema with the template settings.

    Returns:
        A dict with the template settings.
        Example: {"profit_endpoint": 0, "inheritable": true, "token": "Afas_token", "name": "ERP", "id": 0}

    Raises:
        HTTPException(400): This happens when there isn't a base template in the database, and you want to make a new
        template, or it happens when you want to create a base template when there is already one.
    """
    db_template: models.Template = template.orm_create()
    db.add(db_template)
    db.commit()
    if not db_template.demo_environment:
        db.refresh(db_template)
        return db_template
    try:
        db_base_template = db.query(models.Template).filter_by(inheritable=True).one()
    except NoResultFound:
        if not template.inheritable:
            raise DatabaseError(error_code=ErrorCode.U0003)
    else:
        if template.inheritable:
            raise DatabaseError(error_code=ErrorCode.U0004)

        db_chapters = await crud.get_chapters(db, db_base_template.id)

        for chapter in db_chapters["chapters"]:
            new_chapter = schemas.ChapterAndEntitiesCreate.from_orm(chapter)
            new_chapter.entities = []
            entities = await crud.get_chapter(db, db_base_template.id, chapter.id)
            for entity in entities.entities:
                new_entity = schemas.EntityProcessCreate.from_orm(entity)
                if new_entity.entity_type == "process":
                    if None in (new_entity.process.process_settings, new_entity.process.data_sources,
                                new_entity.process.connectors):
                        new_dashboard = schemas.ProcessGeneralCreate.from_orm(new_entity.process)
                        new_dashboard.last_exported = None
                        new_dashboard.percentage_exported = None
                        new_dashboard.amount_failed_groups = None
                        new_dashboard.amount_successful_groups = None
                        new_dashboard.template_id = db_template.id
                    else:
                        new_dashboard = schemas.ProcessDashboardCreate.from_orm(new_entity.process)
                        new_dashboard.last_exported = None
                        new_dashboard.percentage_exported = None
                        new_dashboard.amount_failed_groups = None
                        new_dashboard.amount_successful_groups = None
                        new_dashboard.process_settings.inherit = True
                        new_dashboard.template_id = db_template.id
                        for data_source in new_dashboard.data_sources:
                            data_source.inherit = False
                        for connector in new_dashboard.connectors:
                            connector.connector_settings.inherit = True
                            for field in connector.fields_:
                                field.inherit = True
                                field.custom_row_values = []

                    new_dashboard.inherits_process_id = entity.process.id
                    new_entity.process = new_dashboard
                else:
                    new_entity.note.last_completed = None
                    new_entity.note.completed_mark = False
                new_chapter.entities.append(new_entity)
            db_template.chapters.append(new_chapter.orm_create())

        for db_process in db_chapters["processes"]:
            if None in (db_process.process_settings, db_process.data_sources, db_process.connectors):
                inherited_process = schemas.ProcessGeneralCreate.from_orm(db_process)
                inherited_process.last_exported = None
                inherited_process.percentage_exported = None
                inherited_process.amount_failed_groups = None
                inherited_process.amount_successful_groups = None
            else:
                inherited_process = schemas.ProcessDashboardCreate.from_orm(db_process)
                inherited_process.last_exported = None
                inherited_process.percentage_exported = None
                inherited_process.amount_failed_groups = None
                inherited_process.amount_successful_groups = None
                inherited_process.process_settings.inherit = True
                for data_source in inherited_process.data_sources:
                    data_source.inherit = False
                for connector in inherited_process.connectors:
                    connector.connector_settings.inherit = True
                    for field in connector.fields_:
                        field.inherit = True
                        field.custom_row_values = []

            inherited_process.inherits_process_id = db_process.id
            db_template.processes.append(inherited_process.orm_create())

    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


async def get_template(db: Session, template_id: int) -> models.Template:
    """**Returns a specific template from the database.**

    By calling this function you will get a specific template that referenced to you given template_id.

    Args:
        db(Connection): Connection with te database.
        template_id(int): The unique ID from the template.

    Returns:
        A dict with the template settings.
        Example: {"profit_endpoint": 0, "inheritable": true, "token": "Afas_token", "name": "ERP", "id": 0}
    """
    return await check_available_template(db, template_id)


async def update_template(db: Session, template_id: int, template: schemas.TemplateUpdate) -> models.Template:
    """**Updates the template settings**

    By calling this function you will update the setting for a template.

    Args:
        db(Connection): Connection with the database.
        template_id(int): The unique ID from the template.
        template(Request): Request for a pydantic schema with the template settings.

    Returns:
        A dict with the new template settings.
        Example: {"profit_endpoint": 0, "inheritable": true, "token": "Afas_token", "name": "ERP", "id": 0}
    """
    db_template = await check_available_template(db, template_id)
    template.orm_update(db, db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


async def delete_template(db: Session, template_id: int) -> models.Template:
    """**Deletes a template.**

    By calling this function a template with the provided template_id will be removed from the database.

    Args:
        db(Connection): Connection with the database.
        template_id(int): The unique ID from the template.

    Returns:
        A dict with the deleted template settings.
        Example: {"profit_endpoint": 0, "inheritable": true, "token": "Afas_token", "name": "ERP", "id": 0}
    """
    db_template = await check_available_template(db, template_id)
    db.delete(db_template)
    db.commit()
    return db_template
