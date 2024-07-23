from typing import List

from database import constants, crud, models, schemas, utils
from database.database import db_connection
from fastapi import APIRouter, Depends
from pydantic import NonNegativeInt, conint
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/sql", response_model=schemas.SqlGet)
def create_sql(sql: schemas.SqlCreate, db: Session = Depends(db_connection)):
    return crud.create_sql(sql, db)


@router.get("/sql/{sql_id}", response_model=schemas.SqlGet)
async def read_sql(sql_id: int, db: Session = Depends(db_connection)):
    return await crud.read_sql(sql_id, db)


@router.get("/sql", response_model=list[schemas.SqlGet])
async def read_all_sqls(db: Session = Depends(db_connection)):
    return await crud.read_all_sqls(db)


@router.put("/sql/{sql_id}", response_model=schemas.SqlGet)
async def update_sql(sql_id: int, sql: schemas.SqlUpdate, db: Session = Depends(db_connection)):
    return await crud.update_sql(sql_id, sql, db)


@router.post("/batch", response_model=schemas.BatchGet)
async def create_batch(batch: schemas.BatchCreate, db: Session = Depends(db_connection)):
    return await crud.create_batch(batch, db)


@router.get("/batch/{batch_id}", response_model=schemas.BatchGet)
async def read_batch(batch_id: int, db: Session = Depends(db_connection)):
    return await crud.read_batch(batch_id, db)


@router.get("/batch", response_model=list[schemas.BatchGet])
async def read_all_batches(db: Session = Depends(db_connection)):
    return await crud.read_all_batches(db)


@router.put("/batch/{batch_id}", response_model=schemas.BatchGet)
async def update_batch(batch_id: int, batch: schemas.BatchUpdate, db: Session = Depends(db_connection)):
    return await crud.update_batch(batch_id, batch, db)


@router.post("/sql-batch-entity", response_model=schemas.SqlBatchGet)
async def create_sql_batch_entity(sql_batch: schemas.SqlBatchCreate, db: Session = Depends(db_connection)):
    return await crud.create_sql_batch_entity(sql_batch, db)


@router.get("/sql_batch_template_entity", response_model=List[schemas.SqlBatchEntitiesGet])
async def get_sql_batchs(
        # skip: NonNegativeInt = constants.DEFAULT_SKIP,
        # take: NonNegativeInt = constants.DEFAULT_TAKE,
        db: Session = Depends(db_connection),
) -> List[models.SqlBatchEntity]:
    """**Requests and returns all the templates from the database.**

    This endpoint returns all the settings from all the templates that are located in the database.

    Args:
        skip(int): Skips over a specified number of rows in the database.
        take(int): Returns the given number of rows from the database table.
        db(Request): Request for a connection with the database.

    Returns:
        A list of dictionaries with all the settings from the templates.
        Example: [{"profit_endpoint": 0, "inheritable": true, "token": "Afas_token", "name": "Bouw", "id": 0},...]

    Raises:
        #ToDo
    """
    return await crud.get_all_sql_batch_entities(db)


@router.post("/sql_batch_template_entity", response_model=List[schemas.SqlBatchEntitiesGet])
async def create_sql_batch(sql_batch: schemas.SqlBatchCreate, db: Session = Depends(db_connection)):
    return await crud.create_sql_batch_entity(db, sql_batch)


# @router.post("/sql", response_model=List[schemas.SqlGet])
# async def get_sql(db: Session = Depends(db_connection)):
#     return await crud.get_sql(db)

#
# @router.post("/batch", response_model=List[schemas.BatchGet])
# async def get_batch(db: Session = Depends(db_connection)):
#     return await crud.get_batch(db)
#
#
# @router.post("/sql/{sql_id}", response_model=schemas.SqlGet)
# async def get_sql_id(sql_id: conint(gt=0), db: Session = Depends(db_connection)):
#     return await crud.get_sql_by_id(db, sql_id)
#
#
# @router.post("/batch/{batch_id}", response_model=schemas.BatchGet)
# async def get_batch_id(db: Session = Depends(db_connection)):
#     return await crud.get_batch(db)

#
# @router.get("/templates/{template_id}", response_model=schemas.TemplateGet)
# async def get_template(template_id: NonNegativeInt, db: Session = Depends(db_connection)) -> models.Template:
#     """**Requests and returns a template.**
#
#     This endpoint returns all the settings from a specific template.
#
#     Args:
#         template_id(int): The unique ID from the template.
#         db(Request): Request for a connection with the database.
#
#     Returns:
#         A dict with the template settings.
#         Example: {"profit_endpoint": 0, "inheritable": true, "token": "Afas_token", "name": "Bouw", "id": 0}
#
#     Raises:
#         #ToDo
#     """
#     return await crud.get_template(db, template_id)
#
#
# @router.put("/templates/{template_id}", response_model=schemas.TemplateGet)
# async def update_template(
#         template_id: NonNegativeInt, template: schemas.TemplateUpdate, db: Session = Depends(db_connection)
# ):
#     """**Updates the template settings.**
#
#     This endpoint updates the template settings. It replace the old settings with new settings.
#
#     Args:
#         template_id(int): The unique ID from the template.
#         template(Request): Post request JSON containing the new template settings.
#         db(Request): Request for a connection with the database.
#
#     Returns:
#         A dict with the new template settings.
#         Example: {"profit_endpoint": 0, "inheritable": true, "token": "Afas_token", "name": "Bouw", "id": 0}
#     """
#     if template.demo_environment:
#         await utils.check_profit_connection(template.profit_endpoint, template.token)
#     return await crud.update_template(db, template_id, template)
#
#
# @router.delete("/templates/{template_id}", response_model=schemas.TemplateGet)
# async def delete_template(template_id: NonNegativeInt, db: Session = Depends(db_connection)):
#     """**Deletes a template.**
#
#     This endpoint deletes all the settings and the template.
#
#     Args:
#          template_id(int): The unique ID from the template.
#          db(Request): Request for a connection with the database.
#
#     Returns:
#          A dict with the deleted template settings.
#          Example: {"profit_endpoint": 0, "inheritable": true, "token": "Afas_token", "name": "Bouw", "id": 0}
#
#     Raises:
#         #ToDo
#     """
#     return await crud.delete_template(db, template_id)
#
#
# @router.put("/templates/{template_id}/update_order_ids", response_model=List[schemas.ChapterAndEntity])
# async def update_order_ids(
#         template_id: NonNegativeInt,
#         type_update: str,
#         chapters: List[schemas.ChapterAndEntity],
#         db: Session = Depends(db_connection)
# ):
#     """****"""
#     return await crud.update_order_ids(db, template_id, type_update, chapters)
