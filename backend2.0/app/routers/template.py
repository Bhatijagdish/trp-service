from typing import List

from database import constants, crud, models, schemas, utils
from database.database import db_connection
from fastapi import APIRouter, Depends
from pydantic import NonNegativeInt
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/templates", response_model=List[schemas.TemplateGet])
async def get_templates(
        skip: NonNegativeInt = constants.DEFAULT_SKIP,
        take: NonNegativeInt = constants.DEFAULT_TAKE,
        db: Session = Depends(db_connection),
) -> List[models.Template]:
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
    return await crud.get_templates(db, skip, take)


@router.post("/templates", response_model=schemas.TemplateGet)
async def create_template(template: schemas.TemplateCreate, db: Session = Depends(db_connection)):
    """**Creates a new template.**

    This endpoint creates a new template en returns the created template.

    Args:
        template(Request): Post request JSON containing the template settings.
        db(Request): Request for a connection with the database.

    Returns:
        A dict with the template settings.
        Example: {"profit_endpoint": 0, "inheritable": true, "token": "Afas_token", "name": "Bouw", "id": 0}

    Raises:
        #ToDo
    """
    if template.demo_environment:
         await utils.check_profit_connection(template.profit_endpoint, template.token)
    return await crud.create_template(db, template)


@router.get("/templates/{template_id}", response_model=schemas.TemplateGet)
async def get_template(template_id: NonNegativeInt, db: Session = Depends(db_connection)) -> models.Template:
    """**Requests and returns a template.**

    This endpoint returns all the settings from a specific template.

    Args:
        template_id(int): The unique ID from the template.
        db(Request): Request for a connection with the database.

    Returns:
        A dict with the template settings.
        Example: {"profit_endpoint": 0, "inheritable": true, "token": "Afas_token", "name": "Bouw", "id": 0}

    Raises:
        #ToDo
    """
    return await crud.get_template(db, template_id)


@router.put("/templates/{template_id}", response_model=schemas.TemplateGet)
async def update_template(
        template_id: NonNegativeInt, template: schemas.TemplateUpdate, db: Session = Depends(db_connection)
):
    """**Updates the template settings.**

    This endpoint updates the template settings. It replace the old settings with new settings.

    Args:
        template_id(int): The unique ID from the template.
        template(Request): Post request JSON containing the new template settings.
        db(Request): Request for a connection with the database.

    Returns:
        A dict with the new template settings.
        Example: {"profit_endpoint": 0, "inheritable": true, "token": "Afas_token", "name": "Bouw", "id": 0}
    """
    if template.demo_environment:
        await utils.check_profit_connection(template.profit_endpoint, template.token)
    return await crud.update_template(db, template_id, template)


@router.delete("/templates/{template_id}", response_model=schemas.TemplateGet)
async def delete_template(template_id: NonNegativeInt, db: Session = Depends(db_connection)):
    """**Deletes a template.**

    This endpoint deletes all the settings and the template.

    Args:
         template_id(int): The unique ID from the template.
         db(Request): Request for a connection with the database.

    Returns:
         A dict with the deleted template settings.
         Example: {"profit_endpoint": 0, "inheritable": true, "token": "Afas_token", "name": "Bouw", "id": 0}

    Raises:
        #ToDo
    """
    return await crud.delete_template(db, template_id)


@router.put("/templates/{template_id}/update_order_ids", response_model=List[schemas.ChapterAndEntity])
async def update_order_ids(
        template_id: NonNegativeInt,
        type_update: str,
        chapters: List[schemas.ChapterAndEntity],
        db: Session = Depends(db_connection)
):
    """****"""
    return await crud.update_order_ids(db, template_id, type_update, chapters)
