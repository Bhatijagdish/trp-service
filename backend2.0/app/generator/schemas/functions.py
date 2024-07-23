from enum import Enum
from typing import Any, List, Optional, Union

from errors import GeneratorError, ErrorCode
from pydantic import BaseModel, PositiveInt, conlist, validator


class DataType(Enum):
    any = Union[str, int, float, bool]
    str = str
    int = int
    decimal = float
    boolean = bool


ANY = (DataType.str, DataType.int, DataType.decimal, DataType.boolean)


# class FunctionMetaInfoBase(BaseModel):
#     name: str
#     label: str
#     return_data_types: conlist(str, min_items=1)
#     horizontal_parameters: bool = False
#
#
# class FunctionMetaInfoStatic(FunctionMetaInfoBase):
#     pass


class ParameterMetainfoValue(BaseModel):
    id: str
    description: str


class ParameterMetaInfo(BaseModel):
    name: Optional[str] = None
    data_types: conlist(Any, min_items=1)
    label: str = None
    optional: bool = False
    default_value: Optional[Any] = None
    allow_child_functions: bool = True
    values: List[ParameterMetainfoValue] = []


class FunctionMetaInfo(BaseModel):
    name: str
    return_data_types: conlist(Any, min_items=1)
    method_id: PositiveInt = None
    label: str = None
    horizontal_parameters: bool = False
    parameters: List[ParameterMetaInfo]

    @property
    def allow_child_functions(self) -> bool:
        return any(param.allow_child_functions for param in self.parameters)

    @validator("parameters")
    def horizontal_only_without_child_functions(cls, v: List[ParameterMetaInfo], values: dict):
        if values["horizontal_parameters"] and any(param.allow_child_functions for param in v):
            raise GeneratorError(ErrorCode.B0000)
        return v


class FunctionsMetaInfo(BaseModel):
    functions: List[FunctionMetaInfo] = []


class Test(BaseModel):
    aaa: List[Union[str, DataType]]

    @validator("aaa")
    def bab(cls, v, values):
        for index, datatype in enumerate(v):
            if type(datatype) == str:
                try:
                    v[index] = DataType.__getattr__(datatype)
                except AttributeError:
                    raise
        return v


if __name__ == "__main__":
    a = Test(aaa=["int", "str"])
    print(a)
