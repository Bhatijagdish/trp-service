import inspect
from abc import ABCMeta, abstractmethod
from typing import Any, List, Dict
from datetime import timedelta, datetime

import pydantic.error_wrappers

from errors import GeneratorError, ErrorCode
from generator.functions.methods import Functions, FunctionBase
from generator.schemas.functions import FunctionsMetaInfo
from generator.schemas.input import Function as FunctionSchema
from generator.utils import attr_find
from generator.variables import Variables

csv_format = "%m/%d/%y"
date_format = "%Y-%m-%d"


class _Function(metaclass=ABCMeta):
    def __init__(
            self,
            function_config: FunctionSchema,
            source_data: dict,
            source_metainfo: dict,
            functions_metainfo: FunctionsMetaInfo,
            variables: Variables,
            generated_fields: dict,
            connector_config,
            row_index: int,
            row_amount: int,
    ):
        self.function_config = function_config
        self.metainfo = self.function_config.metainfo
        self._source_data = source_data
        self._source_metainfo = source_metainfo
        self._functions_metainfo = functions_metainfo
        self._variables = variables
        self.generated_fields = generated_fields
        self.connector_config = connector_config
        self.row_index = row_index
        self.row_amount = row_amount
        for field in connector_config:
            self.connector_field_config = field

    def _execute_method(self, parameters: dict) -> Any:
        for function_cls in Functions.__dict__.values():
            if inspect.isclass(function_cls) \
                    and issubclass(function_cls, FunctionBase) \
                    and self.function_config.metainfo.name == function_cls._metainfo.name:
                try:
                    function = function_cls(**parameters)
                    value = function.method()
                    try:
                        value = datetime.strptime(value, csv_format).strftime(date_format)
                    except (ValueError, TypeError):
                        pass
                    return value
                except pydantic.error_wrappers.ValidationError:
                    return "##DELETE"
        else:
            raise GeneratorError(ErrorCode.B0000)

    @abstractmethod
    def execute(self):
        pass


class CompositeFunction(_Function):
    def __init__(
            self,
            functions: List[FunctionSchema],
            function_config: FunctionSchema,
            source_data: dict,
            source_metainfo: dict,
            functions_metainfo: FunctionsMetaInfo,
            variables: Variables,
            generated_fields: dict,
            connector_config,
            row_index: int,
            row_amount: int,
    ):
        self._parameter_name = None
        self._parameter_values = None
        self._functions = functions
        super().__init__(function_config, source_data, source_metainfo, functions_metainfo, variables,
                         generated_fields, connector_config, row_index, row_amount)
        self._tree: Dict[str, _Function] = {}

    def compose_tree(self):
        for parameter in self.function_config.parameters:
            try:
                parameter_function_id = int(parameter.input)
            except ValueError:
                if parameter.input == "True" or parameter.input == "False" or parameter.name == "operator":
                    self._parameter_name = parameter.name
                    self._parameter_values = parameter.input
                elif self.function_config.method_id == 2:
                    return ""
                else:
                    raise GeneratorError(ErrorCode.B0011,
                                         msg_args=(
                                             self.connector_field_config[1].label,
                                             self.function_config.metainfo.label,
                                             parameter.name
                                         ))
            parameter_function_config = attr_find(
                iterable=self._functions,
                find_attr="order_id",
                find_value=parameter_function_id,
                error=GeneratorError(ErrorCode.B0003),
            )
            if parameter_function_config.metainfo.allow_child_functions:  # TODO: use better distinction
                parameter_function = CompositeFunction(
                    functions=self._functions,
                    function_config=parameter_function_config,
                    source_data=self._source_data,
                    source_metainfo=self._source_metainfo,
                    functions_metainfo=self._functions_metainfo,
                    variables=self._variables,
                    generated_fields=self.generated_fields,
                    connector_config=self.connector_config,
                    row_index=self.row_index,
                    row_amount=self.row_amount,
                )
                parameter_function.compose_tree()
            else:
                parameter_function = LeafFunction(
                    function_config=parameter_function_config,
                    source_data=self._source_data,
                    source_metainfo=self._source_metainfo,
                    functions_metainfo=self._functions_metainfo,
                    variables=self._variables,
                    generated_fields=self.generated_fields,
                    connector_config=self.connector_config,
                    row_index=self.row_index,
                    row_amount=self.row_amount,
                )
            self._tree[parameter.name] = parameter_function

    def execute(self):
        parameters = {
            parameter: parameter_function.execute()
            for parameter, parameter_function in self._tree.items()
        }
        try:
            if bool(self._parameter_values):
                parameters[self._parameter_name] = self._parameter_values
            return self._execute_method(parameters)
        # This try except is for if Profit returns a None as value, and it needs to be an integer.
        except pydantic.error_wrappers.ValidationError:
            for (key, value) in parameters.items():
                if value is None:
                    parameters[key] = 0
            if bool(self._parameter_values):
                parameters[self._parameter_name] = self._parameter_values
            return self._execute_method(parameters)


class LeafFunction(_Function):
    def execute(self) -> Any:
        if self.metainfo.allow_child_functions:
            try:
                raise GeneratorError(ErrorCode.B0010,
                                     msg_args=(self.connector_field_config.metainfo.label, self.metainfo.label))
            except AttributeError:
                raise GeneratorError(ErrorCode.U0024, msg_args=(
                    self.connector_field_config[1].label, self.function_config.metainfo.name))

        function_name = self.metainfo.name
        parameters = {param.name: param.input for param in self.function_config.parameters}
        if function_name == "vaste_waarde":
            parameters["variables"] = self._variables
        elif function_name == "bron_waarde":
            parameters["source_data"] = self._source_data
            parameters["row_index"] = self.row_index
        elif function_name == "bron_waarde_met_vaste_waarde":
            parameters["source_data"] = self._source_data
            parameters["row_index"] = self.row_index
            parameters["generated_fields"] = self.generated_fields
            parameters["row_amount"] = self.row_amount
            parameters["field_name"] = self.connector_field_config[1].label
        elif function_name == "veld_waarde":
            parameters["generated_fields"] = self.generated_fields
        elif function_name == "random_selectie":
            if self.connector_config.metainfo.values is None:
                raise GeneratorError(error_code=ErrorCode.U0018, msg_args=(self.connector_config.metainfo.label,))
            if self.connector_config.metainfo.values and len(self.connector_config.metainfo.values) > 0:
                parameters["values"] = self.connector_config.metainfo
        elif function_name == "random_boolean":
            parameters["values"] = ('True', 'False')
        return self._execute_method(parameters)
