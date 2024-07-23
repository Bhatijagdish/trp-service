# CustomRow
from database.database import Base
from sqlalchemy import Column, ForeignKey, Integer, Text


class CustomRowValue(Base):
    __tablename__ = "custom_row_values"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=False)
    row = Column(Integer, nullable=False)
    input = Column(Text, nullable=False)
