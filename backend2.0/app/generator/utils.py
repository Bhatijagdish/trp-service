from typing import TypeVar, Iterator, Callable, Any, Optional, Iterable, Union, List

from loguru import logger

from errors import RocketError, ErrorCode
from generator.schemas.input import Parameter, RowFunctionParameter

_T = TypeVar("_T")


def get(obj: Union[dict, object], attr: str) -> Any:
    if isinstance(obj, dict):
        try:
            return obj[attr]
        except KeyError:
            raise RocketError(ErrorCode.Z0000)
    else:
        try:
            return getattr(obj, attr)
        except AttributeError:
            raise RocketError(ErrorCode.Z0000)


def find(iterable: Iterable[_T], function: Callable, error: RocketError) -> _T:
    for i in iterable:
        if function(i):
            return i
    raise error


def attr_find(iterable: Iterable[_T], find_attr: str, find_value: Any, error: RocketError) -> _T:
    for i in iterable:
        if get(i, find_attr) == find_value:
            return i
    raise error


def attr_find_get(iterable: Iterable, find_attr: str, find_value: Any, get_attr: str, error: RocketError) -> Any:
    for i in iterable:
        if get(i, find_attr) == find_value:
            return get(i, get_attr)
    raise error


def parameter_get(parameters: List[Union[Parameter, RowFunctionParameter]], name: str, error: RocketError) -> str:
    for parameter in parameters:
        if parameter.name == name:
            if name == "field_id":
                if name != "connector":
                    connectorname = parameter_get(parameters, "connector", error)
                return connectorname + ";" + parameter.input
            else:
                return parameter.input
    raise error


def parameter_get_solo(parameters: List[Union[Parameter, RowFunctionParameter]], name: str, error: RocketError) -> str:
    for parameter in parameters:
        if parameter.name == name:
            return parameter.input
    raise error


def find_field_name(fields: List, field):
    return [item for item in fields if item.fieldId == field][0].label


def get_year(year, month):
    if month == 1:
        year += 1
    return year


def find_values(filter_field, filter_source, raw_source_data, all_data):
    filter_values = set()
    for source, values in all_data.items():
        if source == filter_source:
            filter_values = set(row[filter_field] for row in values)
    source_data = [row for row in raw_source_data if row[filter_field] not in filter_values]
    return source_data


def remove_empty_rows(data):
    if type(data["item"]) == list:
        raise RocketError(ErrorCode.B0015)
    else:
        for update_connector, element in data["item"].items():
            if type(element["Element"]) == list:
                new_elements = []
                for new_element in element["Element"]:
                    for name, value in new_element.items():
                        if name == "Fields":
                            all_values = value.values()
                            if "##DELETE" in all_values and data["row_removed"] is not True:
                                data["row_removed"] = True
                            if "##DELETE" not in all_values:
                                new_elements.append(new_element)
                        elif name == "Objects" and len(value) != 0:
                            if type(value) == list:
                                result = remove_list_items(
                                    {
                                        "row_removed": data["row_removed"],
                                        "item": value
                                    }
                                )
                                if result["row_removed"]:
                                    data["row_removed"] = True
                                new_element["Objects"] = result["item"]
                element["Element"] = new_elements

            else:
                for name, item in element["Element"].items():
                    if name == "Fields":
                        item_values = item.values()
                        if "##DELETE" in item_values:
                            data["row_removed"] = True
                            data["item"] = None
                            return data

                    elif name == "Objects" and len(item) != 0:
                        if type(item) == list:
                            result = remove_list_items(
                                {
                                    "row_removed": data["row_removed"],
                                    "item": item
                                }
                            )
                            if result["row_removed"]:
                                data["row_removed"] = True
                            element["Element"]["Objects"] = result["item"]

    return data


def remove_list_items(data):
    all_items = []
    for item in data["item"]:
        new_item = remove_empty_rows(
            {
                "row_removed": data["row_removed"],
                "item": item
            })
        if new_item["item"] is None and data["row_removed"] is not True:
            data["row_removed"] = True
        elif new_item["row_removed"]:
            data["row_removed"] = True

        if new_item["item"] is not None:
            all_items.append(new_item["item"])
    data["items"] = all_items
    return data
