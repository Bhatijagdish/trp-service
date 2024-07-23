# Function, FunctionParameter, Method
from database.database import Base
from sqlalchemy import VARCHAR, Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from database import constants


class Function(Base):
    __tablename__ = "functions"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    field_id = Column(Integer, ForeignKey("fields.id"), nullable=False)
    method_id = Column(Integer, ForeignKey("methods.id"), nullable=False)
    order_id = Column(Integer, nullable=False)

    parameters = relationship("FunctionParameter", cascade="all, delete")


class FunctionParameter(Base):
    __tablename__ = "function_parameters"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    function_id = Column(Integer, ForeignKey("functions.id"), nullable=False)
    name = Column(VARCHAR(constants.LENGTH_PARAMETER_NAME), nullable=False)
    input = Column(Text, nullable=False)


class Method(Base):
    __tablename__ = "methods"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(VARCHAR(constants.LENGTH_METHOD_NAME), nullable=False, unique=True)
