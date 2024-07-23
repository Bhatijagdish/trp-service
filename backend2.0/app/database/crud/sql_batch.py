from typing import List
from database import constants, crud, models, schemas
from errors import DatabaseError, ErrorCode
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from pydantic import constr, conint
from fastapi import HTTPException

def create_sql(sql: schemas.SqlCreate, db: Session):
    db_sql = models.Sql(**sql.dict())
    db.add(db_sql)
    db.commit()
    db.refresh(db_sql)
    return db_sql


async def read_sql(sql_id: int, db: Session):
    db_sql = db.query(models.Sql).filter(models.Sql.id == sql_id).first()
    if db_sql is None:
        raise HTTPException(status_code=404, detail="SQL not found")
    return db_sql


async def read_all_sqls(db: Session):
    db_sqls = db.query(models.Sql).all()
    return db_sqls


async def update_sql(sql_id: int, sql: schemas.SqlUpdate, db: Session):
    db_sql = db.query(models.Sql).filter(models.Sql.id == sql_id).first()
    if db_sql is None:
        raise HTTPException(status_code=404, detail="SQL not found")
    db_sql.name = sql.name
    db_sql.statement = sql.statement
    db.commit()
    db.refresh(db_sql)
    return db_sql


async def create_batch(batch: schemas.BatchCreate, db: Session):
    db_batch = models.Batch(name=batch.name, statement=batch.statement)
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    return db_batch


async def read_batch(batch_id: int, db: Session):
    db_batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if db_batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    return db_batch


async def read_all_batches(db: Session):
    db_batches = db.query(models.Batch).all()
    return db_batches


async def update_batch(batch_id: int, batch: schemas.BatchUpdate, db: Session):
    db_batch = db.query(models.Batch).filter(models.Batch.id == batch_id).first()
    if db_batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    db_batch.name = batch.name
    db_batch.statement = batch.statement
    db.commit()
    db.refresh(db_batch)
    return db_batch


async def create_sql_batch_entity(sql_batch: schemas.SqlBatchCreate, db: Session):
    return_entities = []
    if sql_batch.sql and sql_batch.batch:
        raise HTTPException(status_code=400, detail="Either sql or batch should be provided, not both")

    if not sql_batch.sql and not sql_batch.batch:
        raise HTTPException(status_code=400, detail="Either sql or batch s  hould be provided")

    if sql_batch.sql:
        db_sql = schemas.SqlBase(name=sql_batch.sql.name, statement=sql_batch.sql.statement)
        db_sql = db_sql.orm_create()
        db.add(db_sql)
        db.flush()
        sql_batch.sql = db_sql.id
        sql_batch.type = 'sql'
    elif sql_batch.batch:
        db_batch = schemas.BatchBase(name=sql_batch.batch.name, statement=sql_batch.batch.statement)
        db_batch = db_batch.orm_create()
        db.add(db_batch)
        db.flush()
        sql_batch.batch = db_batch.id
        sql_batch.type = 'batch'
    for template_id in sql_batch.template:
        sql_batch.template = template_id
        new_order = len(db.query(models.SqlBatchEntity).filter_by(models.SqlBatchEntity.template == template_id).all())
        sql_batch.order_number = new_order
        print(sql_batch)
        # db_sql_batch_template_entity = models.SqlBatchEntity(**sql_batch.dict())
        db_sql_batch_template_entity = sql_batch.orm_create()
        db.add(db_sql_batch_template_entity)
        db.commit()
        db.refresh(db_sql_batch_template_entity)

        if db_sql_batch_template_entity.sql:
            db_sql_batch_template_entity.sql = db_sql
        else:
            db_sql_batch_template_entity.batch = db_batch
        return_entities.append(db_sql_batch_template_entity)
    return return_entities





async def get_sql_batch_entity(db: Session, sql_batch_entity_id: int) -> models.SqlBatchEntity:
    sql_batch_entity = db.query(models.SqlBatchEntity).filter(models.SqlBatchEntity.id == sql_batch_entity_id).first()
    if not sql_batch_entity:
        raise HTTPException(status_code=404, detail="SqlBatchEntity not found")
    return sql_batch_entity


async def check_available_sql_batch_entities(db: Session, sql_id: conint(gt=0) = None, template_id: conint(gt=0) = None,
                                             batch_id: conint(gt=0) = None):
    """**Checks if the asked templates is present in the database.**

    Args:
        batch_id:
        template_id:
        sql_id:
        sql_batch_id:
        db(Connection): Connection with the database.

    Returns:
        A database models object with a unique id.
        Example: <database.models.core.Template object at 0x000001C605BDCF40>

    Raises:
        DatabaseError(404): This happens when the templated is not found in the database.
    """
    db_sql_batch_entity = []
    if sql_id:
        db_sql_batch_entity = db.query(models.SqlBatch).filter_by(sql=sql_id).all()
    elif batch_id:
        db_sql_batch_entity = db.query(models.SqlBatch).filter_by(batch=batch_id).all()
    elif template_id:
        db_sql_batch_entity = db.query(models.SqlBatch).filter_by(template=template_id).all()
    elif sql_id and template_id:
        db_sql_batch_entity = db.query(models.SqlBatch).filter_by(sql=sql_id, template=template_id).all()
    elif batch_id and template_id:
        db_sql_batch_entity = db.query(models.SqlBatch).filter_by(batch=batch_id, template=template_id).all()
    if not db_sql_batch_entity:
        raise DatabaseError(error_code=ErrorCode.U0001, status_code=404)
    return db_sql_batch_entity


# API Requests
async def get_all_sql_batch_entities(db: Session) -> List[models.SqlBatchEntity]:
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

    return db.query(models.SqlBatchEntity).all()


async def create_sql_batch_entity(db: Session, sql_batch: schemas.SqlBatchCreate):
    """**Creates a new template.**

    By calling this function you will create a template. All the required parameters are visible in the schema.
    If you set the parameter "inheritable" to False you will get that all the processes from the Basis Template will be
    copied to you're new template.

    Args:
        sql_batch:
        db(Connection):  Connection with the database.

    Returns:
        A dict with the template settings.
        Example: {"profit_endpoint": 0, "inheritable": true, "token": "Afas_token", "name": "ERP", "id": 0}

    Raises:
        HTTPException(400): This happens when there isn't a base template in the database, and you want to make a new
        template, or it happens when you want to create a base template when there is already one.
    """
    return_data = []
    for template_id in sql_batch.template:
        if sql_batch.type == 'sql':
            sql_data = await create_sql(db, sql_batch.sql)
            sql_batch.sql = sql_data.id
            sql_batch.batch = None
        else:
            batch_data = await create_batch(db, sql_batch.batch)
            sql_batch.batch = batch_data.id
            sql_batch.sql = None
        sql_batch.template = template_id
        new_order = len(db.query(models.SqlBatchEntity).filter_by(template=template_id).all())
        sql_batch.order_number = new_order
        db_sql_batch_entity = sql_batch.orm_create()
        db.add(db_sql_batch_entity)
        db.commit()
        db.refresh(db_sql_batch_entity)
        return_data.append(db_sql_batch_entity)
    return return_data


async def create_sql(db: Session, sql: schemas.SqlCreate):
    db_sql = sql.orm_create()
    db.add(db_sql)
    db.commit()
    db.refresh(db_sql)
    return db_sql

async def create_batch(db: Session, batch: schemas.BatchCreate):
    db_batch = batch.orm_create()
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    return db_batch

async def get_sql_batch(db: Session, sql_batch_id: int) -> models.Template:
    """**Returns a specific template from the database.**

    By calling this function you will get a specific template that referenced to you given template_id.

    Args:
        db(Connection): Connection with te database.
        template_id(int): The unique ID from the template.

    Returns:
        A dict with the template settings.
        Example: {"profit_endpoint": 0, "inheritable": true, "token": "Afas_token", "name": "ERP", "id": 0}
    """
    return await check_available_sql_batch(db, sql_batch_id)


async def update_sql_batchs(db: Session, sql_batch_id: int, template: schemas.TemplateUpdate) -> models.Template:
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
    db_template = await check_available_sql_batch(db, sql_batch_id)
    template.orm_update(db, db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


async def delete_sql_batchs(db: Session, sql_batch_id: int) -> models.Template:
    """**Deletes a template.**

    By calling this function a template with the provided template_id will be removed from the database.

    Args:
        db(Connection): Connection with the database.
        template_id(int): The unique ID from the template.

    Returns:
        A dict with the deleted template settings.
        Example: {"profit_endpoint": 0, "inheritable": true, "token": "Afas_token", "name": "ERP", "id": 0}
    """
    db_template = await check_available_template(db, sql_batch_id)
    db.delete(db_template)
    db.commit()
    return db_template
