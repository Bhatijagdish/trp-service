# GlobalVariable, TemplateVariable, ProcessVariable
from database.database import Base
from sqlalchemy import VARCHAR, Column, ForeignKey, Integer
from database import constants


class GlobalVariable(Base):
    __tablename__ = "global_variables"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(VARCHAR(constants.LENGTH_VARIABLE_NAME), nullable=False, unique=True)
    input = Column(VARCHAR(constants.LENGTH_VARIABLE_NAME), nullable=False)


class TemplateVariable(Base):
    __tablename__ = "template_variables"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=False)
    name = Column(VARCHAR(constants.LENGTH_VARIABLE_NAME), nullable=False)
    input = Column(VARCHAR(constants.LENGTH_VARIABLE_NAME), nullable=False)


class ProcessVariable(Base):
    __tablename__ = "process_variables"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    process_id = Column(Integer, ForeignKey("processes.id"), nullable=False)
    name = Column(VARCHAR(constants.LENGTH_VARIABLE_NAME), nullable=False)
    input = Column(VARCHAR(constants.LENGTH_VARIABLE_NAME), nullable=False)
