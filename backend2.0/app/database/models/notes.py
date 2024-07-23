from database.database import Base
from sqlalchemy import VARCHAR, Boolean, Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from database import constants


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=True)
    name = Column(VARCHAR(constants.LENGTH_NOTE_NAME), nullable=False)
    description = Column(Text, nullable=True)
    last_completed = Column(VARCHAR(constants.LENGTH_LAST_GENERATED), nullable=True)
    completed_mark = Column(Boolean, nullable=False)

    entity = relationship("Entity", back_populates="note")
