from typing import List

from database import constants, crud, schemas
from database.database import db_connection
from fastapi import APIRouter, Depends
from pydantic import NonNegativeInt
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/global_variables", response_model=List[schemas.GlobalVariableColorGet])
async def get_global_variables(
        take_dynamic_vars: bool,
        skip: NonNegativeInt = constants.DEFAULT_SKIP,
        take: NonNegativeInt = constants.DEFAULT_TAKE,
        db: Session = Depends(db_connection),
):
    """**Request and returns all the global variables from the database.**

    This endpoint returns all the global variables that are located in the database.

    Args:
        take_dynamic_vars: Enables is you want to add the dynamic variables also to the list of variables.
        skip(int): Skips over a specified number of rows in the database.
        take(int): Returns the given number of rows from the database table.
        db(Request): Request for a connection with the database.

    Returns:
        A list with dictionaries with all the global variables.
        Example: [{"name": "Basis naam", "value": "Cas de Graaf", "id": 2},...]
    """
    return await crud.get_global_variables(db, take_dynamic_vars, skip, take)


@router.put("/global_variables", response_model=List[schemas.GlobalVariableGet])
async def update_global_variables(
        global_variable: List[schemas.GlobalVariableCreate], db: Session = Depends(db_connection)
):
    """**Updates, creates and deletes global variables.**

    This endpoint updates, creates and deletes the global variables.

    Args:
        global_variable(Request): Data used to update/create/delete global variables.
        db(Request): Request for a connection with the database.

    Returns:
        A list with dictionaries with the new created and/or updated global variables.
        Example: [{"name": "Basis naam", "value": "Cas de Graaf", "id": 2},...]
    """
    return await crud.update_global_variables(db, global_variable)


@router.get("/templates/{template_id}/template_variables", response_model=List[schemas.TemplateVariableColorGet])
async def get_template_variables(
        template_id: NonNegativeInt,
        include_global_variables: bool,
        include_all_variables: bool,
        skip: NonNegativeInt = constants.DEFAULT_SKIP,
        take: NonNegativeInt = constants.DEFAULT_TAKE,
        db: Session = Depends(db_connection),
):
    """**Request and returns all the template variables from the database.**

    This endpoint returns all the template variables that are located in the database.

    Args:
        template_id(int): The unique ID from the template.
        include_global_variables(bool): Enables is you want to add the global_variables also to the list of variables.
        include_all_variables(bool): Enables is you want to add the global and dynamic variables also to the list of variables.
        skip(int): Skips over a specified number of rows in the database.
        take(int): Returns the given number of rows from the database table.
        db(Request): Request for a connection with the database.

    Returns:
        A list with dictionaries with all the template variables.
        Example: [{"name": "Basis naam", "value": "Cas de Graaf", "id": 2},...]
    """
    return await crud.get_template_variables(
        db, template_id, include_global_variables, include_all_variables, skip, take)


@router.put("/templates/{template_id}/template_variables", response_model=List[schemas.TemplateVariableGet])
async def update_template_variables(
        template_id: NonNegativeInt,
        template_variable: List[schemas.TemplateVariableCreate],
        db: Session = Depends(db_connection),
):
    """**Updates, creates and deletes template variables.**

    This endpoint updates, creates and deletes the template variables.

    Args:
        template_id(int): The unique ID from the template.
        template_variable(Request): Data used to update/create/delete template variables.
        db(Request): Request for a connection with the database.

    Returns:
        A list with dictionaries with the new created and/or updated template variables.
        Example: [{"name": "Basis naam", "value": "Cas de Graaf", "id": 2},...]
    """
    return await crud.update_template_variables(db, template_id, template_variable)


@router.get(
    "/templates/{template_id}/processes/{process_id}/process_variables",
    response_model=List[schemas.ProcessVariableColorGet]
)
async def get_process_variables(
        template_id: NonNegativeInt,
        process_id: NonNegativeInt,
        take_all_variables: bool = True,
        skip: NonNegativeInt = constants.DEFAULT_SKIP,
        take: NonNegativeInt = constants.DEFAULT_TAKE,
        db: Session = Depends(db_connection),
):
    """**Request and returns all the process variables from the database.**

    This endpoint returns all the process variables that are located in the database.

    Args:
        template_id(int): The unique ID from the template.
        process_id(int): The unique ID from the process.
        take_all_variables(bool):
        skip(int): Skips over a specified number of rows in the database.
        take(int): Returns the given number of rows from the database table.
        db(Request): Request for a connection with the database.

    Returns:
        A list with dictionaries with all the process variables.
        Example: [{"name": "Basis naam", "value": "Cas de Graaf", "id": 2},...]
    """
    return await crud.get_process_variables(db, template_id, process_id, take_all_variables, skip, take)


@router.put(
    "/templates/{template_id}/processes/{process_id}/process_variables", response_model=List[schemas.ProcessVariableGet]
)
async def update_process_variables(
        template_id: NonNegativeInt,
        process_id: NonNegativeInt,
        process_variable: List[schemas.ProcessVariableCreate],
        db: Session = Depends(db_connection),
):
    """**Updates, creates and deletes global variables.**

    This endpoint updates, creates and deletes the global variables.

    Args:
        template_id(int): The unique ID from the template.
        process_id(int): The unique ID from the process.
        process_variable(Request): Data used to update/create/delete process variables.
        db(Request): Request for a connection with the database.

    Returns:
        A list with dictionaries with the new created and/or updated template variables.
        Example: [{"name": "Basis naam", "value": "Cas de Graaf", "id": 2},...]
    """
    return await crud.update_process_variables(db, template_id, process_id, process_variable)


@router.get("/templates/{template_id}/processes/{process_id}/dynamic_variables")
async def get_dynamic_variables(
        template_id: NonNegativeInt,
        process_id: NonNegativeInt,
        db: Session = Depends(db_connection)
):
    return await crud.get_dynamic_variables(db, template_id, process_id)
