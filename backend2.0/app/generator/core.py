from __future__ import annotations

import random
import math
from typing import Optional

from errors import GeneratorError, ErrorCode
from generator.schemas import input
from generator.functions.function_tree import CompositeFunction, LeafFunction
from generator.profit import Fuel
from generator.schemas.functions import FunctionsMetaInfo
from generator.utils import attr_find_get, attr_find, parameter_get, find_values, remove_empty_rows,\
    parameter_get_solo, find_field_name
from generator.variables import Variables


class Engine:
    def __init__(self, fuel: Fuel):
        self._configurations = fuel.configurations
        self._metainfo = fuel.metainfo
        self._raw_source_data = fuel.source_data
        self._source_metainfo = fuel.source_metainfo  # TODO: raw separation
        self._variables = fuel.variables
        self._functions_metainfo = fuel.functions_metainfo
        self._row_counter = 0
        self._source_data = {}
        self._full_source_data = []
        self.generated_data = []

    def apply_source_filtering(self):
        for data_source in self._configurations.data_sources:
            data = {}
            if data_source.source.type_source == "GetConnector":
                source_name = data_source.source.name
                raw_source_data = self._raw_source_data[source_name]
                if filter_source := data_source.filter_source:
                    if filter_source.source.type_source == "GetConnector":
                        filter_source_name = filter_source.source.name
                        source_field_id = attr_find_get(
                            iterable=self._source_metainfo[source_name]["fields"],
                            find_attr="label",
                            find_value=filter_source.filter_field,
                            get_attr="id",
                            error=GeneratorError(ErrorCode.B0004)
                        )
                        filter_source_field_id = attr_find_get(
                            iterable=self._source_metainfo[filter_source_name]["fields"],
                            find_attr="label",
                            find_value=filter_source.filter_field,
                            get_attr="id",
                            error=GeneratorError(ErrorCode.B0004)
                        )
                        filter_values = \
                            set(row[filter_source_field_id] for row in self._raw_source_data[filter_source_name])
                        source_data = [row for row in raw_source_data if row[source_field_id] not in filter_values]
                        source_name += f" - {filter_source_name}"
                        data['repeatable'] = data_source.repeatable
                    else:
                        source_filter_field = filter_source.filter_field
                        filter_source_name = filter_source.source.csv_file.file_name
                        source_data = find_values(
                            source_filter_field,
                            filter_source_name,
                            raw_source_data,
                            self._raw_source_data
                        )
                        source_name += f" - {filter_source_name}"
                        data["repeatable"] = data_source.repeatable
                else:
                    source_data = list(raw_source_data)
                    data['repeatable'] = data_source.repeatable
            else:
                source_name = data_source.source.csv_file.file_name
                raw_source_data = self._raw_source_data[source_name]
                if filter_source := data_source.filter_source:
                    source_filter_field = filter_source.filter_field
                    if filter_source.source.type_source == "GetConnector":
                        filter_source_name = filter_source.source.name
                        filter_values = \
                            set(row[source_filter_field] for row in self._raw_source_data[filter_source_name])
                        source_data = [row for row in raw_source_data if row[source_filter_field] not in filter_values]
                        source_name += f" - {filter_source_name}"
                        data["repeatable"] = data_source.repeatable
                    else:
                        filter_source_name = filter_source.source.csv_file.file_name
                        source_data = find_values(
                            source_filter_field,
                            filter_source_name,
                            raw_source_data,
                            self._raw_source_data
                        )
                        source_name += f" - {filter_source_name}"
                        data["repeatable"] = data_source.repeatable
                else:
                    source_data = list(raw_source_data)
                    data["repeatable"] = data_source.repeatable

            for filter_row in data_source.field_filter_rows:
                pass  # TODO

            data_source.name = source_name
            data[source_name] = source_data
            self._source_data[source_name] = source_data
            self._full_source_data.append(data)

    def topological_sort_fields(self):
        """**Sorts fields in topological order.**

        Fields that use the 'veld_waarde' function are dependent on another fields generated output.
        This function check for those dependencies between fields and orders them in the correct order.

        First a dependency graph gets created in the form of a dict, for example:
            {"a": ["b"]}
        """
        for connector in self._configurations.connectors:
            graph = {}
            connector_fields = {field.field_code for field in connector.fields_}
            for field in connector.fields_:
                dependencies = []
                for function in field.functions:
                    if function.metainfo.name == "veld_waarde":
                        dependency = parameter_get_solo(function.parameters, "field_id", GeneratorError(ErrorCode.B0000))
                        if dependency in connector_fields:
                            dependencies.append(dependency)
                graph[field.field_code] = dependencies

            unsorted_fields = set(graph)
            sorted_fields = []
            while True:
                ordered = [field for field, dependencies in graph.items() if not dependencies]
                sorted_fields.extend(ordered)
                if not ordered:
                    break
                graph = {field: [dependency for dependency in dependencies if dependency not in ordered]
                         for field, dependencies in graph.items() if field not in ordered}

            failed_fields = unsorted_fields - set(sorted_fields)
            if failed_fields:
                fieldnames = [find_field_name(connector.metainfo.fields_, field) for field in failed_fields]
                raise GeneratorError(ErrorCode.U0008, (', '.join(fieldnames),))
            connector.fields_.sort(key=lambda sorted_field: sorted_fields.index(sorted_field.field_code))

    def toposort(self):
        connector_fields = {}
        for connector in self._configurations.connectors:
            graph = {}
            connector_fields[connector.name] = {field.field_code for field in connector.fields_}
            for field in connector.fields_:
                dependecies = []
                for function in field.functions:
                    if function.metainfo.name == "veld_waarde":
                        dependecy = parameter_get(function.parameters, "field_id", GeneratorError(ErrorCode.B0000))
                        aap = dependecy.split(";")
                        try:
                            try:
                                dat = aap[0].split("->")
                                losCon = dat[1].strip()
                                if aap[1] in connector_fields[losCon]:
                                    newDep = losCon + ";" + aap[1]
                                    dependecies.append(newDep)
                            except IndexError:
                                if aap[1] in connector_fields[aap[0]]:
                                    dependecies.append(dependecy)
                        except KeyError:
                            raise GeneratorError(
                                error_code=ErrorCode.U0021,
                                msg_args=(aap[0], find_field_name(connector.metainfo.fields_, aap[1]))
                            )
                graph[connector.name + ";" + field.field_code] = dependecies
            unsorted_fields = set(graph)
            sorted_fields = []
            while True:
                orderd = []
                for field, dependencies in graph.items():
                    if field not in dependencies:
                        orderd.append(field)
                sorted_fields.extend(orderd)
                if len(orderd) == 0:
                    break
                graph = {field: [dependency for dependency in dependencies if dependency not in orderd]
                         for field, dependencies in graph.items() if field not in orderd}

            failed_field = unsorted_fields - set(sorted_fields)
            if failed_field:
                oef = []
                for field in failed_field:
                    ip = field.split(";")
                    oef.append(ip[1])
                fieldnames = [find_field_name(connector.metainfo.fields_, field) for field in oef]
                raise GeneratorError(ErrorCode.U0008, (list(fieldnames),))
            fields = []
            for field in sorted_fields:
                new = field.split(";")
                fields.append(new[1])
            connector.fields_.sort(key=lambda sorted_field: fields.index(sorted_field.field_code))

    def generate(self):
        root_connector_config = attr_find(
            iterable=self._configurations.connectors,
            find_attr="hierarchy",
            find_value=self._metainfo.name,
            error=GeneratorError(ErrorCode.B0005)
        )
        root_connector = Connector(
            configurations=self._configurations,
            connector_config=root_connector_config,
            source_data=self._source_data,
            full_source_data=self._full_source_data,
            source_metainfo=self._source_metainfo,
            variables=self._variables,
            functions_metainfo=self._functions_metainfo
        )
        root_connector.run()
        for element in root_connector.generated_data["Element"]:  # TODO: maybe do this when sending to profit
            self.generated_data.append({self._metainfo.name: {"Element": element}})

    def remove_empty_rows(self):
        new_data = {
            "row_removed": False,
            "generated_data": []
        }
        for item in self.generated_data:
            new_item = remove_empty_rows(
                {
                    "row_removed": False,
                    "item": item
                }
            )
            if new_item["item"] is not None:
                new_data["generated_data"].append(new_item["item"])
            if new_item["row_removed"]:
                new_data["row_removed"] = True
        self.generated_data = new_data

    def run(self):
        self.apply_source_filtering()
        if len(self._configurations.connectors) == 1:
            self.topological_sort_fields()
        else:
            self.toposort()
        self.generate()
        self.remove_empty_rows()


class Connector:
    rows_amount: int

    def __init__(
            self,
            configurations: input.ConfigurationDashboard,
            connector_config: input.Connector,
            source_data: dict,
            full_source_data: list,
            source_metainfo: dict,
            variables: Variables,
            functions_metainfo: FunctionsMetaInfo,
            parent_generated_fields: Optional[dict] = None
    ):
        self._configurations = configurations
        self._connector_config = connector_config
        self._metainfo = self._connector_config.metainfo
        self._source_data = source_data
        self._full_source_data = full_source_data
        self._source_metainfo = source_metainfo
        self._variables = variables
        self._functions_metainfo = functions_metainfo
        self._parent_generated_fields = parent_generated_fields or {}
        self.generated_data = {"Element": []}
        self.get_connector_list = []

    def find_active_get_connectors(self):
        for field in self._connector_config.fields_:
            for function in field.functions:
                if function.metainfo.name == "bron_waarde" or function.metainfo.name == "bron_waarde_met_vaste_waarde":
                    get_connector = next(item for item in function.parameters if item.name == "get_connector")
                    self.get_connector_list.append(get_connector.input)

    def calculate_rows_amount(self):
        rows_function = self._connector_config.connector_settings.rows_function
        parameters = self._connector_config.connector_settings.row_function_parameters
        if rows_function == "random_waarde":
            try:
                min_value = int(parameter_get(parameters, "minimale_waarde", GeneratorError(ErrorCode.B0002)))
            except ValueError:
                raise GeneratorError(ErrorCode.U0014)
            try:
                max_value = int(parameter_get(parameters, "maximale_waarde", GeneratorError(ErrorCode.B0002)))
            except ValueError:
                raise GeneratorError(ErrorCode.U0014)
            if min_value > max_value:
                raise GeneratorError(ErrorCode.U0015)
            try:
                self.rows_amount = random.randint(min_value, max_value)
            except ValueError:
                raise GeneratorError(ErrorCode.B0006)
        elif rows_function == "bron_percentage":
            source = parameter_get(parameters, "bron", GeneratorError(ErrorCode.B0002))
            try:
                percentage = float(parameter_get(parameters, "bron_percentage", GeneratorError(ErrorCode.B0002)))
            except ValueError:
                raise GeneratorError(ErrorCode.U0000)
            try:
                source_length = len(self._source_data[source])
            except KeyError:
                raise GeneratorError(ErrorCode.B0012)
            self.rows_amount = int((source_length * (percentage / 100)) + 0.5)

    def prepare_sources(self):
        if len(self.get_connector_list) != 0:
            for data_source in self._full_source_data:
                for item in data_source.keys():
                    if item in self.get_connector_list:
                        for source_name, rows in data_source.items():
                            if source_name == "repeatable":
                                repeatable = rows
                            if source_name != "repeatable":
                                random.shuffle(rows)
                                if (row_amount := self.rows_amount) > len(rows) > 0:
                                    if repeatable:
                                        rows *= math.ceil(row_amount / len(rows))
                                        random.shuffle(rows)
                                    else:
                                        random.shuffle(rows)
                                    #     raise GeneratorError(ErrorCode.U0019, msg_args=(source_name,))

    def generate(self):
        row_counter = 0
        hierarchy = self._connector_config.hierarchy
        for index, row in enumerate(range(self.rows_amount)):
            row_counter += 1
            element = {"row_counter": row_counter, "Fields": {}, "Objects": []}
            generated_fields = {**self._parent_generated_fields, hierarchy: element["Fields"]}
            for field in self._connector_config.fields_:
                function_config = attr_find(
                    iterable=field.functions,
                    find_attr="order_id",
                    find_value=0,
                    error=GeneratorError(ErrorCode.F0003, msg_args=(field.metainfo.label,))
                )
                if len(field.functions) > 1:
                    function = CompositeFunction(
                        functions=field.functions,
                        function_config=function_config,
                        source_data=self._source_data,
                        source_metainfo=self._source_metainfo,
                        functions_metainfo=self._functions_metainfo,
                        variables=self._variables,
                        generated_fields=generated_fields,
                        connector_config=field,
                        row_index=index,
                        row_amount=self.rows_amount,
                    )
                    function.compose_tree()
                elif len(field.functions) == 1:
                    function = LeafFunction(
                        function_config=function_config,
                        source_data=self._source_data,
                        source_metainfo=self._source_metainfo,
                        functions_metainfo=self._functions_metainfo,
                        variables=self._variables,
                        generated_fields=generated_fields,
                        connector_config=field,
                        row_index=index,
                        row_amount=self.rows_amount,
                    )
                else:
                    raise GeneratorError(ErrorCode.B0000)
                try:
                    value = self._variables.apply(field.custom_row_values[0].input)
                    field.custom_row_values.pop(0)
                except (IndexError, AttributeError):
                    value = None
                if not value:
                    value = function.execute()
                element["Fields"][field.field_code] = value

            for connector_config in self._configurations.connectors:
                sub_hierarchy = connector_config.hierarchy
                if sub_hierarchy.startswith(hierarchy) and sub_hierarchy.count("->") == hierarchy.count("->") + 1:
                    connector = Connector(
                        configurations=self._configurations,
                        connector_config=connector_config,
                        source_data=self._source_data,
                        full_source_data=self._full_source_data,
                        source_metainfo=self._source_metainfo,
                        variables=self._variables,
                        functions_metainfo=self._functions_metainfo,
                        parent_generated_fields=generated_fields,
                    )
                    connector.run()
                    if connector.generated_data["Element"]:
                        element["Objects"].append({connector_config.name: connector.generated_data})
            self.generated_data["Element"].append(element)

    def run(self):
        self.find_active_get_connectors()
        self.calculate_rows_amount()
        self.prepare_sources()
        self.generate()
