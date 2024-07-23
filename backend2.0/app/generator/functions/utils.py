from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Dict, List, Optional, Type, Union, Any
from datetime import datetime
import string

from pydantic import BaseModel, create_model, BaseConfig

from database.crud import create_method
from database.database import DatabaseSession
from database.models import Method
from database.schemas import MethodCreate
from errors import GeneratorError, ErrorCode
from generator.schemas.functions import DataType, FunctionMetaInfo, FunctionsMetaInfo

if TYPE_CHECKING:
    from generator.functions.methods import Functions, FunctionBase

DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
LETTERS: dict = {ord(d): str(i) for i, d in enumerate(string.digits + string.ascii_uppercase)}
bank_codes: list = ['RABO', 'INGB', 'ABNA', 'KNAB']
country_code: str = "NL"


def compose_functions_metainfo(functions_cls: Type[Functions], methods: List[Method]) -> FunctionsMetaInfo:
    # TODO: ^ (partly) redo this function ^
    functions_metainfo = FunctionsMetaInfo()
    for attr_name in dir(functions_cls):
        attr: FunctionBase = getattr(functions_cls, attr_name)
        # TODO: you can use attr.__fields__ to get a handy dictionary from pydantic
        if inspect.isclass(attr) and hasattr(attr, "_metainfo"):
            metainfo: FunctionMetaInfo = attr._metainfo
            metainfo.label = metainfo.name.replace("_", " ").capitalize()
            metainfo.return_data_types = [
                data_type.name for data_type in metainfo.return_data_types if type(data_type) == DataType
            ]
            try:
                metainfo.method_id = next(method.id for method in methods if method.name == metainfo.name)
            except StopIteration:
                db = DatabaseSession()
                try:
                    db_method = create_method(db, MethodCreate(name=metainfo.name))
                    metainfo.method_id = db_method.id
                except Exception as e:
                    raise GeneratorError(ErrorCode.B0000)
                finally:
                    db.close()

            for index, parameter in enumerate(metainfo.parameters):
                # parameter.name = attr.__slots__[index]
                # parameter.label = parameter.name.replace("_", " ").capitalize()
                parameter.data_types = [
                    data_type.name for data_type in parameter.data_types if type(data_type) == DataType
                ]

            functions_metainfo.functions.append(metainfo)
    return functions_metainfo


def format_date(date_str):
    try:
        date = datetime.strptime(date_str, DATE_FORMAT)
    except ValueError:
        try:
            date = datetime.strptime(date_str, DATETIME_FORMAT)
        except ValueError:
            raise GeneratorError(ErrorCode.U0009, (DATE_FORMAT, DATETIME_FORMAT))
    return date
