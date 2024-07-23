# DataSource, FilterSource, Source, GetConnector, CSVFile, FieldFilterRow, FieldFilter
from database.database import Base
from sqlalchemy import VARCHAR, Boolean, Column, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship
from database import constants


class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    process_id = Column(Integer, ForeignKey("processes.id"), nullable=False)
    repeatable = Column(Boolean, nullable=False)
    inherit = Column(Boolean, nullable=True)
    custom_name = Column(VARCHAR(constants.LENGTH_CUSTOM_NAME), nullable=True)

    source = relationship("Source", cascade="all, delete", back_populates="data_source", uselist=False)
    filter_source = relationship("FilterSource", cascade="all, delete", back_populates="data_source", uselist=False)
    field_filter_rows = relationship("FieldFilterRow", cascade="all, delete")


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    data_source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=True)
    filter_source_id = Column(Integer, ForeignKey("filter_sources.id"), nullable=True)
    type_source = Column(VARCHAR(constants.LENGTH_TYPE_SOURCE), nullable=False)

    csv_file = relationship("CSVFile", cascade="all, delete", back_populates="source", uselist=False)
    data_source = relationship("DataSource", back_populates="source")
    filter_source = relationship("FilterSource", back_populates="source")
    get_connector = relationship("GetConnector", cascade="all, delete", back_populates="source", uselist=False)


class FilterSource(Base):
    __tablename__ = "filter_sources"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    data_source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False)
    filter_field = Column(VARCHAR(constants.LENGTH_FILTER_FIELD), nullable=False)

    data_source = relationship("DataSource", back_populates="filter_source")
    source = relationship("Source", cascade="all, delete", back_populates="filter_source", uselist=False)


class CSVFile(Base):
    __tablename__ = "csv_files"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    file_name = Column(VARCHAR(constants.LENGTH_CSV_FILE_NAME), nullable=False)
    file = Column(JSON, nullable=False)

    source = relationship("Source", back_populates="csv_file")

    # optional: cascade delete relation


class GetConnector(Base):
    __tablename__ = "get_connectors"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    name = Column(VARCHAR(constants.LENGTH_GETCONNECTOR_NAME), nullable=False)

    source = relationship("Source", back_populates="get_connector")


class FieldFilterRow(Base):
    __tablename__ = "field_filter_rows"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    data_source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False)
    field_id = Column(VARCHAR(constants.LENGTH_GETCONNECTOR_FIELD_ID), nullable=False)

    field_filters = relationship("FieldFilter", cascade="all, delete")


class FieldFilter(Base):
    __tablename__ = "field_filters"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    field_filter_row_id = Column(Integer, ForeignKey("field_filter_rows.id"), nullable=False)
    operator = Column(VARCHAR(constants.LENGTH_OPERATOR), nullable=False)
    input = Column(VARCHAR(constants.LENGTH_FIELD_FILTER_VALUE), nullable=False)
