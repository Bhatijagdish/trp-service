# Template, Process, Connector, Field
from database.database import Base
from sqlalchemy import VARCHAR, Boolean, Column, ForeignKey, Integer, Text, Float
from sqlalchemy.orm import relationship, backref
from database import constants


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    profit_endpoint = Column(Text, nullable=False)
    token = Column(Text, nullable=True)
    name = Column(VARCHAR(constants.LENGTH_TEMPLATE_NAME), nullable=False)
    inheritable = Column(Boolean, nullable=False)
    template_number = Column(Integer, nullable=True)
    demo_environment = Column(Boolean, nullable=False)

    processes = relationship("Process", cascade="all, delete")
    chapters = relationship("Chapter", cascade="all, delete")
    template_variables = relationship("TemplateVariable", cascade="all, delete")
    template_entity = relationship("SqlBatchEntity", cascade="all, delete")


class Sql(Base):
    __tablename__ = "sql_table"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(VARCHAR(constants.LENGTH_SQL_NAME), unique=True, nullable=False)
    statement = Column(Text, nullable=False)

    sql_entity = relationship("SqlBatchEntity", back_populates='sql', cascade="all, delete")


class Batch(Base):
    __tablename__ = "batch_table"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(VARCHAR(constants.LENGTH_BATCH_NAME), unique=True, nullable=False)
    statement = Column(Text, nullable=False)

    batch_entity = relationship("SqlBatchEntity", back_populates='batch', cascade="all, delete")


class SqlBatchEntity(Base):
    __tablename__ = "sql_batch_entity_table"

    id = Column(Integer, primary_key=True, nullable=False)
    sql = Column(Integer, ForeignKey("sql_table.id"), nullable=True)
    batch = Column(Integer, ForeignKey("batch_table.id"), nullable=True)
    template = Column(Integer, ForeignKey("templates.id"), nullable=False)
    type = Column(VARCHAR(constants.LENGTH_SQL_BATCH_ENTITY_TYPE), nullable=False)
    order_number = Column(Integer, nullable=False)



class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=True)
    name = Column(VARCHAR(constants.LENGTH_CHAPTER_NAME), nullable=False)
    order_id = Column(Integer, nullable=False)
    last_completed = Column(VARCHAR(constants.LENGTH_LAST_GENERATED), nullable=True)
    completed_mark = Column(Boolean, nullable=False)

    entities = relationship("Entity", cascade="all, delete")


class Entity(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False)
    entity_type = Column(VARCHAR(constants.LENGTH_ENTITY_TYPE), nullable=False)
    order_id = Column(Integer, nullable=False)

    process = relationship("Process", cascade="all, delete", back_populates="entity", uselist=False)
    note = relationship("Note", cascade="all, delete", back_populates="entity", uselist=False)


class Process(Base):
    __tablename__ = "processes"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=True)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=True)
    inherits_process_id = Column(Integer, ForeignKey("processes.id"), nullable=True)
    update_connector = Column(VARCHAR(constants.LENGTH_UPDATECONNECTOR_NAME), nullable=False)
    name = Column(VARCHAR(constants.LENGTH_PROCESS_NAME), nullable=False)
    description = Column(Text, nullable=False)
    order_number = Column(Integer, nullable=False)
    last_exported = Column(VARCHAR(constants.LENGTH_LAST_GENERATED), nullable=True)
    percentage_exported = Column(Float, nullable=True)
    amount_successful_groups = Column(Integer, nullable=True)
    amount_failed_groups = Column(Integer, nullable=True)

    process_settings = relationship("ProcessSettings", cascade="all, delete", back_populates="process", uselist=False)
    entity = relationship("Entity", back_populates="process")
    data_sources = relationship("DataSource", cascade="all, delete")
    connectors = relationship("Connector", cascade="all, delete")
    process_variables = relationship("ProcessVariable", cascade="all, delete")


class Connector(Base):
    __tablename__ = "connectors"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    process_id = Column(Integer, ForeignKey("processes.id"), nullable=False)
    name = Column(VARCHAR(constants.LENGTH_UPDATECONNECTOR_NAME), nullable=False)
    hierarchy = Column(Text, nullable=False)

    connector_settings = relationship(
        "ConnectorSettings", cascade="all, delete", back_populates="connector", uselist=False
    )
    fields = relationship("Field", cascade="all, delete")


class Field(Base):
    __tablename__ = "fields"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    connector_id = Column(Integer, ForeignKey("connectors.id"), nullable=False)
    field_code = Column(VARCHAR(constants.LENGTH_FIELD_CODE), nullable=False)
    inherit = Column(Boolean, nullable=False)

    functions = relationship("Function", cascade="all, delete")
    custom_row_values = relationship("CustomRowValue", cascade="all, delete")


if __name__ == "__main__":
    pass
