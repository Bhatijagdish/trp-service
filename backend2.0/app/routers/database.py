from database import crud
from database.database import db_connection
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/methods")
async def get_methods(db: Session = Depends(db_connection)):
    return await crud.get_methods(db)
