from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel


class Connector(BaseModel):
    Element: List[Element]


class Element(BaseModel):
    Fields: Dict[str, str]
    Objects: List[Dict[str, Connector]]


class GeneratedData(BaseModel):
    generated_data: Dict[str, Connector]
