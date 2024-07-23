from typing import Optional, List

from pydantic import BaseModel, Field as SchemaField


class UpdateConnectorFieldValue(BaseModel):
    id: str
    description: str


class UpdateConnectorField(BaseModel):
    fieldId: str
    primaryKey: bool
    dataType: str
    label: str
    mandatory: bool
    length: int
    decimals: int
    decimalFieldId: str
    notzero: bool
    controlType: int
    values: Optional[List[UpdateConnectorFieldValue]]


class ConnectorMetainfo(BaseModel):
    name: str
    hierarchy: str
    fields_: List[UpdateConnectorField] = SchemaField(..., alias="fields")


class UpdateConnectorMetainfo(BaseModel):
    id: str
    description: str
    name: str
    connectors: List[ConnectorMetainfo]
