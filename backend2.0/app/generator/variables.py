from typing import List
from datetime import timedelta, datetime
from calendar import monthrange

from loguru import logger

from database.models import GlobalVariable, ProcessVariable, TemplateVariable
from generator.utils import get_year

date_format = "%Y-%m-%d"
datetime_format = "%Y-%m-%dT%H:%M:%SZ"


def first_day_of_the_month(date):
    return datetime.strftime(date.replace(day=1), date_format)


def last_day_of_the_month(date):
    return datetime.strftime(date.replace(day=monthrange(date.year, date.month)[1]), date_format)


def next_month(date):
    month = date.month + 1
    if month == 13:
        month = 1
    return month


def first_day_of_next_month(date):
    month = next_month(date)
    year = get_year(date.year, month)
    new_date = datetime.strftime(date.replace(year=year, month=month, day=1), date_format)
    return new_date


def last_day_of_next_month(date):
    month = next_month(date)
    year = get_year(date.year, month)
    new_date = datetime.strftime(date.replace(year=year, month=month, day=monthrange(date.year, month)[1]), date_format)
    return new_date


def get_week(date):
    str_date = datetime.strftime(date, datetime_format)
    date_time_date = datetime.strptime(str_date, datetime_format)
    return date_time_date.isocalendar()[1]


def get_next_year_based_on_month(date):
    current_month = date.month
    current_year = date.year
    if current_month == 12:
        current_year += 1
    return current_year


class Variables:
    def __init__(
            self,
            global_vars: List[GlobalVariable],
            template_vars: List[TemplateVariable],
            process_vars: List[ProcessVariable],
    ):
        self.global_vars = global_vars
        self.template_vars = template_vars
        self.process_vars = process_vars
        self.dynamic_variables = {}
        self.static_variables = {}
        self.combined_vars = []
        self.today = datetime.today().date()
        self.create_dynamic_variables()
        self._add_static_vars()
        self._add_dynamic_vars()
        self._combine_vars()

    @property
    def variables(self) -> dict:
        self.create_dynamic_variables()

        all_variables = {}
        variable_names = []
        for name, value in self.static_variables.items():
            variable_names.append(name)
            all_variables[name] = value
            if name not in variable_names:
                all_variables[name] = value

        for dy_name, dy_value in self.dynamic_variables.items():
            if dy_name not in variable_names:
                all_variables[dy_name] = dy_value

        return all_variables

    def _add_static_vars(self):
        for global_var in self.global_vars:
            self.static_variables[global_var.name] = global_var.input
        for template_var in self.template_vars:
            self.static_variables[template_var.name] = template_var.input
        for process_var in self.process_vars:
            self.static_variables[process_var.name] = process_var.input

    def _combine_vars(self):
        var_names = []
        for variable in self.process_vars:
            self.combined_vars.append(variable)
            var_names.append(variable.name)
        for var in self.template_vars:
            if var.name not in var_names:
                self.combined_vars.append(var)
                var_names.append(var.name)
        for global_var in self.global_vars:
            if global_var.name not in var_names:
                self.combined_vars.append(global_var)
                var_names.append(global_var.name)

    def _add_dynamic_vars(self):
        self.dynamic_variables = {
            "datum": str(datetime.strftime(self.today, date_format)),
            "jaar": str(self.today.year),
            "maand": str(self.today.month),
            "dag": str(self.today.day),
            "week": str(get_week(self.today)),
            "volgende_maand": str(next_month(self.today)),
            "eerste_dag_maand": str(first_day_of_the_month(self.today)),
            "laatste_dag_maand": str(last_day_of_the_month(self.today)),
            "eerste_dag_volgende_maand": str(first_day_of_next_month(self.today)),
            "laatste_dag_volgende_maand": str(last_day_of_next_month(self.today)),
            "jaar_volgende_maand": str(get_next_year_based_on_month(self.today)),
        }
        return self.dynamic_variables

    def apply(self, string: str) -> str:
        old_string = string.rsplit(' ')
        for index, item in enumerate(old_string):
            if "$" in item:
                value = self.get_variable_name(item)
                if value is not None:
                    old_string[index] = value

        new_string = " ".join(old_string)
        return new_string

    def get_variable_name(self, string):
        new_string = string
        all_variables = dict(self.variables.items())
        sorted_vars = {}
        for k in sorted(all_variables, key=len, reverse=True):
            sorted_vars[k] = all_variables[k]
        for var_name, var_value in sorted_vars.items():
            if var_name in new_string:
                new_string = new_string.replace("$" + var_name, var_value)
        return new_string

    def create_dynamic_variables(self):
        var_names = []
        var_dicts = []
        for variable in self.combined_vars:
            var_dicts.append(variable)
            var_names.append(variable.name)

        if "datum" in var_names:
            value = [i.input for i in var_dicts if i.name == "datum"][0]
            try:
                self.today = datetime.strptime(value, date_format)
                return self._add_dynamic_vars()
            except ValueError:
                pass

        if "jaar" in var_names:
            for i in var_dicts:
                given_year = [i.input for i in var_dicts if i.name == "jaar"][0]
                try:
                    self.today = self.today.replace(year=int(given_year))
                except ValueError:
                    pass

        if "maand" in var_names:
            for i in var_dicts:
                given_month = [i.input for i in var_dicts if i.name == "maand"][0]

                try:
                    self.today = self.today.replace(month=int(given_month))
                except ValueError:
                    try:
                        self.today = self.today.replace(month=int(given_month), day=28)
                    except ValueError:
                        pass

        if "dag" in var_names:
            for i in var_dicts:
                given_day = [i.input for i in var_dicts if i.name == "dag"][0]
                try:
                    self.today = self.today.replace(day=int(given_day))
                except ValueError:
                    pass

        return self._add_dynamic_vars()
