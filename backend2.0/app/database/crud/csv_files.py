from typing import List

from database import constants, models, schemas
from errors import DatabaseError, ErrorCode
from sqlalchemy.orm import Session


async def check_available_csv_file(db, csv_id):
    """
    This function checks if the asked CSV file is present in de database.

    Args:
        db(Connection): Connection with the database.
        csv_id(int): The unique id from the csv-file.

    Returns:
        A database modal with the unique CSVFile object.
        Example: <database.models.data_sources.CSVFile object at 0x000001FC2A8BBE80>

    Raises:
        DatabaseError(404): This happens when their doesn't exist a csv file with the given csv_id.
    """
    db_csv_file = db.query(models.CSVFile).filter_by(id=csv_id).first()
    if not db_csv_file:
        raise DatabaseError(error_code=ErrorCode.U0007, msg_args=(csv_id,), status_code=404)
    return db_csv_file


async def get_csv_files(
        db: Session, skip: int = constants.DEFAULT_SKIP, take: int = constants.DEFAULT_TAKE
) -> List[models.CSVFile]:
    """**Retrieves all the csv_files from the database.**

    By calling this function you will get amount of csv_files between skip and take.

    Args:
        db(Connection): Connection with the database.
        skip(int): Skips over a specified number of rows in the database.
        take(int): Returns the given number of rows from the database table.

    Returns:
        A list with dictionaries with all the csv files.
        Example: [{"filename": "chooses", "file": "[{\"Word\":\"##DELETE\"}]", "id: 211},..]
    """
    return db.query(models.CSVFile).offset(skip).limit(take).all()


async def create_csv_file(db: Session, csv_file: schemas.CSVFileCreate) -> models.CSVFile:
    """**Creates a new csv_file.**

    Args:
        db(Connection): Connection with te database.
        csv_file(Request): Request for a pydantic schema with the csv_file settings.

    Returns:
        A dictionary with the created csv_file.
        Example: {"filename": "chooses", "file": "[{\"Word\":\"##DELETE\"}]", "id: 211}
    """
    db_csv_file: models.CSVFile = csv_file.orm_create()

    db.add(db_csv_file)
    db.commit()
    db.refresh(db_csv_file)
    return db_csv_file


async def get_csv_file(db: Session, csv_id: int) -> models.CSVFile:
    """**Returns a specific csv file from the database.**

    Args:
        db(Connection): Connection with the database.
        csv_id(int): The unique ID from a csv_file.

    Returns:
        A dictionary with the asked csv file.
        Example: {"filename": "chooses", "file": "[{\"Word\":\"##DELETE\"}]", "id: 211}
    """
    return await check_available_csv_file(db, csv_id)


async def update_csv_file(db: Session, csv_id: int, csv_file: schemas.CSVFileUpdate) -> models.CSVFile:
    """**Updates a specific csv file.**

    By calling this function you will update an existing csv file with the new data.

    Args:
        db(Connection): Connection with the database.
        csv_id(int): The unique ID from a csv_file.
        csv_file(Request): Request for a pydantic schema with the csv_file settings.

    Returns:
        A dictionary with the updated csv file.
        Example: {"filename": "chooses", "file": "[{\"Word\":\"##DELETE\"}]", "id: 211}
    """
    db_csv_file = await check_available_csv_file(db, csv_id)
    csv_file.orm_update(db, db_csv_file)
    db.commit()
    db.refresh(db_csv_file)
    return db_csv_file


async def delete_csv_file(db: Session, csv_id: int) -> models.CSVFile:
    """**Deletes a csv_file.**

    By calling this function a csv_file with the provided csv_id will be removed from the database.

    Args:
        db(Connection): Connection with te database.
        csv_id(int): The unique ID from a csv_file.

    Returns:
        A dictionary with the deleted csv file.
        Example: {"filename": "chooses", "file": "[{\"Word\":\"##DELETE\"}]", "id: 211}
    """
    db_csv_file = await check_available_csv_file(db, csv_id)
    db.delete(db_csv_file)
    db.commit()
    return db_csv_file
