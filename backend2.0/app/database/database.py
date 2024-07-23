import os
import time

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError, OperationalError, ProgrammingError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeMeta, Session, sessionmaker

DATABASE_CONNECTION_ATTEMPTS = 5
DATABASE_CONNECTION_TIMEOUT = 2

POSTGRES_HOST = os.getenv("POSTGRES_HOST", default="localhost")
POSTGRES_DB = os.getenv("POSTGRES_NAME", default="postgres")
POSTGRES_USER = os.getenv("POSTGRES_USER", default="postgres")
POSTGRES_PASS = os.getenv("POSTGRES_PASS", default="test")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", default=5432)
SQLALCHEMY_DATABASE_URL = \
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASS}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"


db_engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"connect_timeout": DATABASE_CONNECTION_TIMEOUT})
# # noinspection PyTypeChecker
Base: DeclarativeMeta = declarative_base(bind=db_engine)
DatabaseSession = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


def db_connection() -> Session:
    """This function creates a connection with the database."""
    db = DatabaseSession()
    try:
        yield db
    finally:
        db.close()


# noinspection PyUnresolvedReferences
async def initialize_db() -> None:
    """Connect with the database for the first time. This is with the startup of the server."""
    database_alive = False
    attempt = 1
    while not database_alive:
        try:
            try:
                Base.metadata.create_all()
            except (IntegrityError, ProgrammingError):
                pass
            database_alive = True
            logger.success(f"Database connection attempt {attempt} successful")
        except OperationalError:
            logger.info(f"Database connection attempt {attempt} failed (timeout 3 sec)")
            if attempt == DATABASE_CONNECTION_ATTEMPTS:
                raise ConnectionError("Cannot connect to database")
            attempt += 1
            time.sleep(DATABASE_CONNECTION_TIMEOUT)
