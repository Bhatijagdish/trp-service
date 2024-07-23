from typing import List

from database import constants, crud, models, schemas
from generator import variables
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound  # noqa: F401


def sort_all_vars(dynamic_vars, global_vars, template_vars, process_vars):
    """**Sorts all kinds of variables.**

    By calling this function the sorting of variables wil happen. There is a hierarchy which variable is more dominant.
    From most important to the least: process_vars, template_vars, global_vars, dynamic_vars.

    Args:
        dynamic_vars(dict): A dictionary with the dynamic variables.
        global_vars(list): A list with the global variables.
        template_vars(list): A list with the template variables.
        process_vars(list): A list with the process variables.

    Returns:
        A list with dictionaries with all the variables.
        Example: [{"name": "Basis naam", "value": "Cas de Graaf", "id": 2},...]
    """
    all_variables = []
    variable_names = []
    if process_vars:
        for variable in process_vars:
            if variable.name not in variable_names:
                all_variables.append(
                    {"id": variable.id, "name": variable.name, "input": variable.input, "color": "#1A1F24"})
                variable_names.append(variable.name)

    if template_vars:
        for variable in template_vars:
            if variable.name not in variable_names:
                all_variables.append(
                    {"id": variable.id, "name": variable.name, "input": variable.input, "color": "#0078d7"})
                variable_names.append(variable.name)

    if global_vars:
        for variable in global_vars:
            if variable.name not in variable_names:
                all_variables.append(
                    {"id": variable.id, "name": variable.name, "input": variable.input, "color": "#d2003a"})
                variable_names.append(variable.name)

    if dynamic_vars != {}:
        for name, value in dynamic_vars.items():
            if name not in variable_names:
                all_variables.append({"id": 0, "name": name, "input": value, "color": "#F59F39"})
                variable_names.append(name)
    return all_variables


async def get_global_variables(
        db: Session,
        take_dynamic_vars: bool,
        skip: int = constants.DEFAULT_SKIP,
        take: int = constants.DEFAULT_TAKE
) -> List[models.GlobalVariable]:
    """**Retrieves all the global variables from the database.**

    By calling this function you will get amount of global variables between skip and take.

    Args:
        take_dynamic_vars(bool): Enables is you want to add the dynamic_variables also to the list of variables.
        db(Connection): Connection with the database.
        skip(int): Skips over a specified number of rows in the database.
        take(int): Returns the given number of rows from the database table.

    Returns:
        A list with dictionaries with all the global variables.
        Example: [{"name": "Basis naam", "value": "Cas de Graaf", "id": 2},...]
    """
    global_vars = db.query(models.GlobalVariable).offset(skip).limit(take).all()
    if take_dynamic_vars:
        method = variables.Variables(global_vars, [], [])
        dynamic_vars = method.create_dynamic_variables()
        all_variables: list = sort_all_vars(dynamic_vars, global_vars, [], [])
        return all_variables
    return global_vars


async def update_global_variables(
        db: Session, global_variable: List[schemas.GlobalVariableCreate]
) -> List[models.GlobalVariable]:
    """**Update a global variable.**

    By calling this function you get a list of dictionaries with variables. Then we look if there are identical
    names for the variables. Then we update the variables. If there is a variable that doesn't exist already in the
    database, it will be created. At the end we remove the variables from the database that doesn't exist in the list
    of dictionaries.

    Args:
        db(Connection): Connection with the database.
        global_variable(Request): Request for a pydantic schema with the global_variable settings.

    Returns:
        A list with dictionaries with the new created and updated global variables.
        Example: [{"name": "Basis naam", "value": "Cas de Graaf", "id": 2},...]
    """

    db_global_variable = await get_global_variables(db, False)
    variable_names = [var_name.name for var_name in db_global_variable]
    new_variables = []

    for variable in global_variable:
        if variable.name in variable_names:
            db_variable = db.query(models.GlobalVariable).filter_by(name=variable.name).first()
            variable.orm_update(db, db_variable)
            new_variables.append(db_variable)
        else:
            new_variable = variable.orm_create()
            db.add(new_variable)
            new_variables.append(new_variable)

    for db_variable in db_global_variable:
        if db_variable not in new_variables:
            db.delete(db_variable)

    db.commit()
    return new_variables


async def get_template_variables(
        db: Session,
        template_id: int,
        include_global_variables: bool,
        include_all_variables: bool,
        skip: int = constants.DEFAULT_SKIP,
        take: int = constants.DEFAULT_TAKE
) -> List[models.TemplateVariable]:
    """**Retrieves all the template variables from the database**

    By calling this function you will get amount of template variables between skip and take from a specific template.
    If you set the parameter take_global_variables to True you will get a list with all the variables from the specific
    template and global_variables. Their will be no duplicates.

    Args:
        db(Connection): Connection with the database.
        template_id(int): The unique ID from the template.
        include_global_variables(bool): Enables is you want to add the global_variables also to the list of variables.
        include_all_variables(bool): Enables is you want to add the global and dynamic variables also to the list
                                     of variables.
        skip(int): Skips over a specified number of rows in the database.
        take(int): Returns the given number of rows from the database table.

    Returns:
        A list with dictionaries with all the template variables.
        Example: [{"name": "Month", "value": "January", "id": 2},...]
    """

    template_variables = (
        db.query(models.TemplateVariable).filter_by(template_id=template_id).offset(skip).limit(take).all()
    )
    global_variables = await get_global_variables(db, False)

    if include_all_variables:
        method = variables.Variables(global_variables, template_variables, [])
        dynamic_vars = method.create_dynamic_variables()
        all_variables: list = sort_all_vars(dynamic_vars, global_variables, template_variables, [])
        return all_variables
    if include_global_variables:
        variable_names = [var.name for var in template_variables]
        for variable in global_variables:
            if variable.name not in variable_names:
                template_variables.append(variable)
                variable_names.append(variable.name)

    return template_variables


async def update_template_variables(
        db: Session, template_id: int, template_variable: List[schemas.TemplateVariableCreate]
) -> List[models.TemplateVariable]:
    """**Update a template variable.**

    By calling this function you get a list of dictionaries with variables. Then we look if there are identical
    names for the variables. Then we update the variables. If there is a variable that doesn't exist already in the
    database, it will be created. At the end we remove the variables from the database that doesn't exist in the list
    of dictionaries.

    Args:
        db(Connection): Connection with the database.
        template_id(int): The unique ID from the template.
        template_variable(Request): Request for a pydantic schema with the template_variable settings.

    Returns:
        A list with dictionaries with the new created and updated template variables.
        Example: [{"name": "Basis naam", "value": "Cas de Graaf", "id": 2},...]
    """
    db_template_variables = await get_template_variables(db, template_id, False, False)
    variable_names = [variable.name for variable in db_template_variables]
    new_variables = []

    for variable in template_variable:
        if variable.name in variable_names:
            db_variable = (
                db.query(models.TemplateVariable).filter_by(template_id=template_id, name=variable.name).first()
            )
            variable.orm_update(db, db_variable)
            new_variables.append(db_variable)
        else:
            new_variable = variable.orm_create(template_id=template_id)
            db.add(new_variable)
            new_variables.append(new_variable)

    for db_variable in db_template_variables:
        if db_variable not in new_variables:
            db.delete(db_variable)

    db.commit()
    return new_variables


async def get_process_variables(
        db: Session,
        template_id: int,
        process_id: int,
        take_all_variables: bool,
        skip: int = constants.DEFAULT_SKIP,
        take: int = constants.DEFAULT_TAKE,
) -> List[models.ProcessVariable]:
    """**Retrieves all the process variables from the database.**

    By calling this function you will get amount of process variables between skip and take from a specific process.

    Args:
        db(Connection): Connection with the database.
        template_id(int): The unique ID from the template
        process_id(int): The unique ID from the process.
        take_all_variables(bool):
        skip(int): Skips over a specified number of rows in the database.
        take(int): Returns the given number of rows from the database table.

    Returns:
        A list with dictionaries with all the process variables.
        Example: [{"name": "Year", "value": "2026", "id": 2},...]
    """
    process_variables = db.query(models.ProcessVariable).filter_by(process_id=process_id).offset(skip).limit(take).all()

    if take_all_variables:
        dynamic_vars = await get_dynamic_variables(db, template_id, process_id)
        template_vars = await get_template_variables(db, template_id, False, False)
        global_variables = await get_global_variables(db, False)
        all_variables: list = sort_all_vars(dynamic_vars, global_variables, template_vars, process_variables)
        return all_variables
    return process_variables


async def update_process_variables(
        db: Session, template_id: int, process_id: int, process_variable: List[schemas.ProcessVariableCreate]
) -> List[models.ProcessVariable]:
    """**Update a process variable.**

    By calling this function you get a list of dictionaries with variables. Then we look if there are identical
    names for the variables. Then we update the variables. If there is a variable that doesn't exist already in the
    database, it will be created. At the end we remove the variables from the database that doesn't exist in the list
    of dictionaries.

    Args:
        db(Connection): Connection with the database.
        template_id(int): The unique ID from a template
        process_id(int): The unique ID from the process.
        process_variable(Request): Request for a pydantic schema with the process_variable settings.

    Returns:
        A list with dictionaries with the new created and updated process variables.
        Example: [{"name": "Basis naam", "value": "Cas de Graaf", "id": 2},...]
    """

    db_process_variables = await get_process_variables(db, template_id, process_id, False)
    variable_names = [variable.name for variable in db_process_variables]
    new_variables = []

    for variable in process_variable:
        if variable.name in variable_names:
            db_variable = db.query(models.ProcessVariable).filter_by(process_id=process_id, name=variable.name).first()
            variable.orm_update(db, db_variable)
            new_variables.append(db_variable)
        else:
            new_variable = variable.orm_create(process_id=process_id)
            db.add(new_variable)
            new_variables.append(new_variable)

    for db_variable in db_process_variables:
        if db_variable not in new_variables:
            db.delete(db_variable)

    db.commit()
    return new_variables


async def get_dynamic_variables(db: Session, template_id: int, process_id: int):
    """**Returns a dictionary with the variables.**

    By calling this function it will retrieve all the existing global variables, the current template variables and
    the current process variables. Those variables will be used to create the dynamic variables.

    Args:
        db(Connection): Connection with the database.
        template_id(int): The unique ID from a template
        process_id(int): The unique ID from the process.

    Returns:
        A dictionary with the dynamic variables.
        Example: {"datum": "2022-10-04", "year": "2022", "month": "10",...}
    """
    template_vars = await crud.get_template_variables(db, template_id, True, False)
    process_vars = await get_process_variables(db, template_id, process_id, False)
    method = variables.Variables([], template_vars, process_vars)
    dynamic_vars = method.create_dynamic_variables()

    return dynamic_vars
