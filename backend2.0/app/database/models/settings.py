# ProcessSettings, ConnectorSettings, RowSettingsParameter
from database.database import Base
from sqlalchemy import VARCHAR, Boolean, Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from database import constants


class ProcessSettings(Base):
    __tablename__ = "process_settings"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    process_id = Column(Integer, ForeignKey("processes.id"), nullable=False)
    send_method = Column(VARCHAR(constants.LENGTH_SEND_METHOD_NAME), nullable=False)
    inherit = Column(Boolean, nullable=False)

    process = relationship("Process", back_populates="process_settings")


class ConnectorSettings(Base):
    __tablename__ = "connector_settings"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    connector_id = Column(Integer, ForeignKey("connectors.id"), nullable=False)
    rows_function = Column(VARCHAR(constants.LENGTH_ROWS_FUNCTION_NAME), nullable=False)
    inherit = Column(Boolean, nullable=False)

    connector = relationship("Connector", back_populates="connector_settings")
    row_function_parameters = relationship("RowFunctionParameter", cascade="all, delete")


class RowFunctionParameter(Base):
    __tablename__ = "row_function_parameters"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    settings_id = Column(Integer, ForeignKey("connector_settings.id"), nullable=False)
    name = Column(VARCHAR(constants.LENGTH_PARAMETER_NAME), nullable=False)
    input = Column(Text, nullable=False)
