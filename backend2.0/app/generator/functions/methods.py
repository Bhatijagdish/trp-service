import random
from abc import abstractmethod
from typing import Any
from datetime import timedelta, datetime

from generator.schemas.functions import DataType, FunctionMetaInfo, ParameterMetaInfo
from generator.functions.utils import format_date, DATE_FORMAT, bank_codes, LETTERS, country_code
from errors import GeneratorError, ErrorCode
from pydantic import validator, BaseModel

from generator.variables import Variables


class FunctionBase(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    @property
    @abstractmethod
    def _metainfo(self) -> FunctionMetaInfo:
        pass

    @abstractmethod
    def method(self):
        pass


class Functions:
    class ConstantValue(FunctionBase):
        waarde: Any

        variables: Variables

        _metainfo = FunctionMetaInfo(
            name="vaste_waarde",
            return_data_types=[DataType.str],
            parameters=[
                ParameterMetaInfo(name="waarde", data_types=[DataType.str], allow_child_functions=False),
            ],
        )

        def method(self):
            return self.variables.apply(self.waarde)

    class ValueFromProfit(FunctionBase):
        waarde: Any

        _metainfo = FunctionMetaInfo(
            name="waarde_uit_profit",
            return_data_types=[DataType.str],
            parameters=[
                ParameterMetaInfo(name="waarde", data_types=[DataType.any], allow_child_functions=False)
            ],

        )

        def method(self):
            return self.waarde

    class SourceValue(FunctionBase):
        get_connector: str
        get_connector_field: str

        source_data: dict
        row_index: int

        _metainfo = FunctionMetaInfo(
            name="bron_waarde",
            return_data_types=[DataType.str],
            horizontal_parameters=True,
            parameters=[
                ParameterMetaInfo(name="get_connector", data_types=[DataType.str], allow_child_functions=False),
                ParameterMetaInfo(name="get_connector_field", data_types=[DataType.str], allow_child_functions=False),
            ],
        )
        extra_attributes = {"source_data": dict, "row_index": int}

        def method(self):
            try:
                value = self.source_data[self.get_connector][self.row_index][self.get_connector_field]
            except IndexError:
                raise GeneratorError(error_code=ErrorCode.U0019, msg_args=(self.get_connector,))
            except KeyError as e:
                get_connector_with_comment = "'" + self.get_connector + "'"
                if str(e) == get_connector_with_comment:
                    raise GeneratorError(error_code=ErrorCode.U0017, msg_args=(self.get_connector,))
                else:
                    raise GeneratorError(error_code=ErrorCode.U0022, msg_args=(e, self.get_connector))
            return value

    class SourceValueWithFixedValue(FunctionBase):
        get_connector: str
        get_connector_field: str
        fixed_get_connector_field: str
        fixed_value_function: str
        fixed_value: str

        source_data: dict
        row_index: int
        generated_fields: dict
        row_amount: int
        field_name: str

        _metainfo = FunctionMetaInfo(
            name="bron_waarde_met_vaste_waarde",
            return_data_types=[DataType.str],
            parameters=[
                ParameterMetaInfo(name="get_connector", data_types=[DataType.str], allow_child_functions=False),
                ParameterMetaInfo(name="get_connector_field", data_types=[DataType.str], allow_child_functions=False),
                ParameterMetaInfo(name="fixed_get_connector_field", data_types=[DataType.str],
                                  allow_child_functions=False),
                ParameterMetaInfo(name="fixed_value_function", data_types=[DataType.str], allow_child_functions=False),
                ParameterMetaInfo(name="fixed_value", data_types=[DataType.str], allow_child_functions=False)
            ]
        )

        def method(self):
            update_connector: str
            update_connector_field: str
            if "##" in self.fixed_value:
                split_value = self.fixed_value.split("##")
                if split_value[0] != "":
                    update_connector = split_value[0]
                else:
                    # errorhandling
                    pass
                if split_value[1] != "":
                    update_connector_field = split_value[1]
                else:
                    # errorhandling
                    pass
                try:
                    self.fixed_value = self.generated_fields[update_connector][update_connector_field]
                except KeyError:
                    if update_connector_field == self.field_name:
                        raise GeneratorError(error_code=ErrorCode.U0031,
                                         msg_args=(self.field_name, update_connector_field))
                    else:
                        raise GeneratorError(error_code=ErrorCode.U0021,
                                         msg_args=(update_connector, update_connector_field))
            else:
                if self.fixed_value == "":
                    # errorhandling voor vaste waarde
                    pass

            current_source_data = []
            for index, item in enumerate(self.source_data[self.get_connector]):
                if item[self.fixed_get_connector_field] == self.fixed_value:
                    current_source_data.append(item)
            try:
                value = current_source_data[self.row_index][self.get_connector_field]
            except IndexError:
                value = "##DELETE"
                # raise GeneratorError(error_code=ErrorCode.U0016)
            except KeyError as e:
                get_connector_with_comment = "'" + self.get_connector + "'"
                if str(e) == get_connector_with_comment:
                    raise GeneratorError(error_code=ErrorCode.U0017, msg_args=(self.get_connector,))
                else:
                    raise GeneratorError(error_code=ErrorCode.U0022, msg_args=(e, self.get_connector))
            return value

    class FieldValue(FunctionBase):
        connector: str
        field_id: str

        generated_fields: dict

        _metainfo = FunctionMetaInfo(
            name="veld_waarde",
            return_data_types=[DataType.str],
            horizontal_parameters=True,
            parameters=[
                ParameterMetaInfo(name="connector", data_types=[DataType.str], allow_child_functions=False),
                ParameterMetaInfo(name="field_id", data_types=[DataType.str], allow_child_functions=False),
            ]
        )

        def method(self) -> Any:
            try:
                return self.generated_fields[self.connector][self.field_id]
            except KeyError:
                raise GeneratorError(error_code=ErrorCode.U0021, msg_args=(self.connector, self.field_id))

    class RandomSelection(FunctionBase):
        values: Any

        _metainfo = FunctionMetaInfo(
            name="random_selectie",
            return_data_types=[DataType.str],
            parameters=[]
        )

        def method(self) -> Any:
            try:
                self.values = tuple(value.id for value in self.values.values)
            except AttributeError:
                raise GeneratorError(error_code=ErrorCode.U0018)
            try:
                return random.choices(self.values)[0]
            except IndexError:
                return

    class RandomBoolean(FunctionBase):
        values: Any

        _metainfo = FunctionMetaInfo(
            name="random_boolean",
            return_data_types=[DataType.boolean],
            allow_child_functions=False,
            parameters=[]
        )

        def method(self) -> bool:
            return random.choices(self.values)[0]

    class RandomNumber(FunctionBase):
        minimale_waarde: int
        maximale_waarde: int
        aantal_decimalen: int
        stapgrootte: int

        _metainfo = FunctionMetaInfo(
            name="random_getal",
            return_data_types=[DataType.int],
            parameters=[
                ParameterMetaInfo(
                    name="minimale_waarde",
                    data_types=[DataType.int],
                    allow_child_functions=True,
                ),
                ParameterMetaInfo(
                    name="maximale_waarde",
                    data_types=[DataType.int],
                    allow_child_functions=True,
                ),
                ParameterMetaInfo(
                    name="aantal_decimalen",
                    data_types=[DataType.int],
                    default_value=0,
                    allow_child_functions=True,
                ),
                ParameterMetaInfo(
                    name="stapgrootte",
                    data_types=[DataType.int],
                    default_value=1,
                    allow_child_functions=True,
                ),
            ],
        )

        @classmethod
        def _max_greater_than_min(cls, minimale_waarde: int, maximale_waarde: int):
            if maximale_waarde < minimale_waarde:
                raise GeneratorError(error_code=ErrorCode.U0010)
            return minimale_waarde

        @classmethod
        def _steps_larger_than_one(cls, stap_grootte: int):
            if stap_grootte == 0:
                raise GeneratorError(error_code=ErrorCode.U0011)
            return stap_grootte

        def method(self) -> int:
            self._max_greater_than_min(self.minimale_waarde, self.maximale_waarde)
            self._steps_larger_than_one(self.stapgrootte)

            return round(
                random.randrange(self.minimale_waarde, self.maximale_waarde + 1, self.stapgrootte),
                self.aantal_decimalen,
            )

    class RandomDecimalNumber(FunctionBase):
        minimale_waarde: float
        maximale_waarde: float
        aantal_decimalen: int

        _metainfo = FunctionMetaInfo(
            name="random_decimaal_getal",
            return_data_types=[DataType.decimal],
            parameters=[
                ParameterMetaInfo(
                    name="minimale_waarde",
                    data_types=[DataType.decimal],
                    allow_child_functions=True,
                ),
                ParameterMetaInfo(
                    name="maximale_waarde",
                    data_types=[DataType.decimal],
                    allow_child_functions=True,
                ),
                ParameterMetaInfo(
                    name="aantal_decimalen",
                    data_types=[DataType.int],
                    default_value=0,
                    allow_child_functions=True,
                ),
            ]
        )

        @classmethod
        def _max_greater_than_min(cls, minimale_waarde: float, maximale_waarde: float):
            if maximale_waarde < minimale_waarde:
                raise GeneratorError(error_code=ErrorCode.U0010)
            return minimale_waarde

        def method(self) -> float:
            self._max_greater_than_min(self.minimale_waarde, self.maximale_waarde)
            return round(random.uniform(self.minimale_waarde, self.maximale_waarde), self.aantal_decimalen)

    class RandomDate(FunctionBase):  # Moet nog verder getest worden als de value in de JSON wordt gezet op de front-end
        begin_datum: str
        eind_datum: str
        weekend_dagen_meenemen: bool

        _metainfo = FunctionMetaInfo(
            name="genereer_random_datum",
            return_data_types=[DataType.str],
            parameters=[
                ParameterMetaInfo(
                    name="begin_datum",
                    data_types=[DataType.str],
                    allow_child_functions=True,
                ),
                ParameterMetaInfo(
                    name="eind_datum",
                    data_types=[DataType.str],
                    allow_child_functions=True,
                ),
                ParameterMetaInfo(
                    name="weekend_dagen_meenemen",
                    data_types=[DataType.boolean],
                    values=[
                        {
                            "id": "True",
                            "description": True,
                        },
                        {
                            "id": "False",
                            "description": False,
                        },
                    ],
                    default_value=False,
                    allow_child_functions=False,
                ),
            ],
        )

        @classmethod
        def _end_date_later_then_begin_date(cls, first_date: datetime, last_date: datetime):
            days_between_dates = (last_date - first_date).days
            if days_between_dates < 0:
                raise GeneratorError(error_code=ErrorCode.U0012)
            return days_between_dates

        def method(self) -> str:
            first_date = format_date(self.begin_datum)
            last_date = format_date(self.eind_datum)

            days_between_dates = self._end_date_later_then_begin_date(first_date, last_date)

            if days_between_dates == 0:
                random_date = first_date
            else:
                random_number_of_days = random.randrange(0, days_between_dates + 1)
                random_date = first_date + timedelta(days=random_number_of_days)

            if not self.weekend_dagen_meenemen:
                if random_date.isoweekday() == 6:
                    random_date += timedelta(days=2)
                elif random_date.isoweekday() == 7:
                    random_date += timedelta(days=1)

            return random_date.strftime(DATE_FORMAT)

    class AddingExtraDays(FunctionBase):
        originele_datum: str
        extra_dagen: int
        weekend_dagen_meenemen: bool

        _metainfo = FunctionMetaInfo(
            name="extra_dagen_optellen",
            return_data_types=[DataType.str],
            parameters=[
                ParameterMetaInfo(
                    name="originele_datum",
                    data_types=[DataType.str],
                    allow_child_functions=True,
                ),
                ParameterMetaInfo(
                    name="extra_dagen",
                    data_types=[DataType.int],
                    allow_child_functions=True,
                ),
                ParameterMetaInfo(
                    name="weekend_dagen_meenemen",
                    data_types=[DataType.boolean],
                    values=[
                        {
                            "id": "True",
                            "description": "True",
                        },
                        {
                            "id": "False",
                            "description": "False",
                        },
                    ],
                    default_value=False,
                    allow_child_functions=False,
                )
            ]
        )

        def method(self) -> str:
            new_date = format_date(self.originele_datum) + timedelta(days=self.extra_dagen)

            if not self.weekend_dagen_meenemen:
                if new_date.isoweekday() == 6:
                    new_date += timedelta(days=2)
                elif new_date.isoweekday() == 7:
                    new_date += timedelta(days=1)

            return new_date.strftime(DATE_FORMAT)

    class SumValues(FunctionBase):
        eerste_waarde: float
        tweede_waarde: float
        aantal_decimalen: int

        _metainfo = FunctionMetaInfo(
            name="waardes_optellen",
            return_data_types=[DataType.decimal],
            parameters=[
                ParameterMetaInfo(
                    name="eerste_waarde",
                    data_types=[DataType.decimal],
                    allow_child_functions=True,
                ),
                ParameterMetaInfo(
                    name="tweede_waarde",
                    data_types=[DataType.decimal],
                    allow_child_functions=True,
                ),
                ParameterMetaInfo(
                    name="aantal_decimalen",
                    data_types=[DataType.int],
                    default_value=0,
                    allow_child_functions=True,
                ),
            ]
        )

        def method(self) -> Any:
            result = round(self.eerste_waarde + self.tweede_waarde, self.aantal_decimalen)

            if self.aantal_decimalen == 0:
                result = int(result)

            return result

    class SubtractValues(FunctionBase):
        eerste_waarde: float
        tweede_waarde: float
        aantal_decimalen: int

        _metainfo = FunctionMetaInfo(
            name="waardes_aftrekken",
            return_data_types=[DataType.decimal],
            parameters=[
                ParameterMetaInfo(
                    name="eerste_waarde",
                    data_types=[DataType.decimal],
                    allow_child_functions=True,
                ),
                ParameterMetaInfo(
                    name="tweede_waarde",
                    data_types=[DataType.decimal],
                    allow_child_functions=True,
                ),
                ParameterMetaInfo(
                    name="aantal_decimalen",
                    data_types=[DataType.int],
                    default_value=0,
                    allow_child_functions=True,
                ),
            ]
        )

        def method(self) -> Any:
            result = round(self.eerste_waarde - self.tweede_waarde, self.aantal_decimalen)

            if self.aantal_decimalen == 0:
                result = int(result)

            return result

    class MultiplyValues(FunctionBase):
        eerste_waarde: float
        tweede_waarde: float
        aantal_decimalen: int

        _metainfo = FunctionMetaInfo(
            name="waardes_vermenigvuldigen",
            return_data_types=[DataType.decimal],
            parameters=[
                ParameterMetaInfo(
                    name="eerste_waarde",
                    data_types=[DataType.decimal],
                    allow_child_functions=True,
                ),
                ParameterMetaInfo(
                    name="tweede_waarde",
                    data_types=[DataType.decimal],
                    allow_child_functions=True,
                ),
                ParameterMetaInfo(
                    name="aantal_decimalen",
                    data_types=[DataType.int],
                    default_value=0,
                    allow_child_functions=True,
                ),
            ]
        )

        def method(self) -> Any:
            result = round(self.eerste_waarde * self.tweede_waarde, self.aantal_decimalen)

            if self.aantal_decimalen == 0:
                result = int(result)

            return result

    class DivideValues(FunctionBase):
        eerste_waarde: float
        tweede_waarde: float
        aantal_decimalen: int

        _metainfo = FunctionMetaInfo(
            name="waardes_delen",
            return_data_types=[DataType.decimal],
            parameters=[
                ParameterMetaInfo(
                    name="eerste_waarde",
                    data_types=[DataType.decimal],
                    allow_child_functions=True,
                ),
                ParameterMetaInfo(
                    name="tweede_waarde",
                    data_types=[DataType.decimal],
                    allow_child_functions=True,
                ),
                ParameterMetaInfo(
                    name="aantal_decimalen",
                    data_types=[DataType.int],
                    default_value=0,
                    allow_child_functions=True,
                ),
            ]
        )

        def method(self) -> Any:
            result = round(self.eerste_waarde / self.tweede_waarde, self.aantal_decimalen)

            if self.aantal_decimalen == 0:
                result = int(result)

            return result

    class CombiningText(FunctionBase):  # nog goed testen als de frontend het goed doet en de result pagina er is.
        eerste_waarde: Any
        tweede_waarde: Any
        derde_waarde: Any
        vierde_waarde: Any
        vijfde_waarde: Any

        _metainfo = FunctionMetaInfo(
            name="tekst_samenvoegen",
            return_data_types=[DataType.str],
            parameters=[
                ParameterMetaInfo(
                    name="eerste_waarde",
                    data_types=[DataType.str],
                    optional=True,
                    allow_child_functions=True,
                ),
                ParameterMetaInfo(
                    name="tweede_waarde",
                    data_types=[DataType.str],
                    optional=True,
                    allow_child_functions=True,
                ),
                ParameterMetaInfo(
                    name="derde_waarde",
                    data_types=[DataType.str],
                    optional=True,
                    allow_child_functions=True,
                ),
                ParameterMetaInfo(
                    name="vierde_waarde",
                    data_types=[DataType.str],
                    optional=True,
                    allow_child_functions=True,
                ),
                ParameterMetaInfo(
                    name="vijfde_waarde",
                    data_types=[DataType.str],
                    optional=True,
                    allow_child_functions=True,
                )
            ]
        )

        def method(self) -> str:
            if self.eerste_waarde is None and self.tweede_waarde is None and self.derde_waarde is None \
                    and self.vierde_waarde is None and self.vijfde_waarde is None:
                raise GeneratorError(error_code=ErrorCode.U0023)
            if self.eerste_waarde is None:
                self.eerste_waarde = ""
            if self.tweede_waarde is None:
                self.tweede_waarde = ""
            if self.derde_waarde is None:
                self.derde_waarde = ""
            if self.vierde_waarde is None:
                self.vierde_waarde = ""
            if self.vijfde_waarde is None:
                self.vijfde_waarde = ""

            return \
                f"{self.eerste_waarde}{self.tweede_waarde}{self.derde_waarde}{self.vierde_waarde}{self.vijfde_waarde}"

    class RandomBSN(FunctionBase):

        _metainfo = FunctionMetaInfo(
            name="random_bsn",
            return_data_types=[DataType.str],
            allow_child_functions=False,
            parameters=[]
        )

        @classmethod
        def _validate_bsn(cls, bsn_number: int):
            bsn_numbers = [index for index in range(len(str(bsn_number)), 0, -1)]
            bsn_position = [int(char) for char in str(bsn_number)]
            bsn_numbers[-1] = -1

            output = sum((x * y) for x, y in zip(bsn_numbers, bsn_position))
            return output % 11 == 0

        def method(self) -> Any:
            for i in range(100000):
                possible_bsn = random.randint(10000000, 999999999)
                valid_bsn = self._validate_bsn(possible_bsn)
                if valid_bsn:
                    return str(possible_bsn)
            raise ArithmeticError()

    class IfElse(FunctionBase):
        waarde_genereren: Any
        operator: str
        als_waarde: Any
        dan_waarde: Any
        anders: Any

        _metainfo = FunctionMetaInfo(
            name="als_dan",
            return_data_types=[DataType.str],
            parameters=[
                ParameterMetaInfo(
                    name="waarde_genereren",
                    data_types=[DataType.str],
                    allow_child_functions=True,
                ),
                ParameterMetaInfo(
                    name="operator",
                    data_types=[DataType.str],
                    values=[
                        {
                            "id": "Gelijk aan",
                            "description": "="
                        },
                        {
                            "id": "Ongelijk aan",
                            "description": "!="
                        },
                        {
                            "id": "Kleiner dan",
                            "description": "<"
                        },
                        {
                            "id": "Kleiner dan of gelijk aan",
                            "description": "<="
                        },
                        {
                            "id": "Groter dan",
                            "description": ">"
                        },
                        {
                            "id": "Groter dan of gelijk aan",
                            "description": ">="
                        }
                    ],
                    allow_child_functions=False,
                ),
                ParameterMetaInfo(
                    name="als_waarde",
                    data_types=[DataType.str],
                    allow_child_functions=True,
                ),
                ParameterMetaInfo(
                    name="dan_waarde",
                    data_types=[DataType.str],
                    allow_child_functions=True,
                ),
                ParameterMetaInfo(
                    name="anders",
                    data_types=[DataType.str],
                    allow_child_functions=True,
                ),
            ]
        )

        def method(self) -> Any:

            if self.operator == "Gelijk aan":
                if str(self.waarde_genereren) == str(self.als_waarde):
                    value = str(self.dan_waarde)
                else:
                    value = str(self.anders)
            elif self.operator == "Ongelijk aan":
                if str(self.waarde_genereren) != str(self.als_waarde):
                    value = str(self.dan_waarde)
                else:
                    value = str(self.anders)
            elif self.operator == "Kleiner dan":
                if str(self.waarde_genereren) < str(self.als_waarde):
                    value = str(self.dan_waarde)
                else:
                    value = str(self.anders)
            elif self.operator == "Kleiner dan of gelijk aan":
                if str(self.waarde_genereren) <= str(self.als_waarde):
                    value = str(self.dan_waarde)
                else:
                    value = str(self.anders)
            elif self.operator == "Groter dan":
                if str(self.waarde_genereren) > str(self.als_waarde):
                    value = str(self.dan_waarde)
                else:
                    value = str(self.anders)
            elif self.operator == "Groter dan of gelijk aan":
                if str(self.waarde_genereren) >= str(self.als_waarde):
                    value = str(self.dan_waarde)
                else:
                    value = str(self.anders)
            else:
                raise GeneratorError(error_code=ErrorCode.U0013, msg_args=(self.operator,))

            return value

    class UploadFile(FunctionBase):
        file_name: str
        file: str

        _metainfo = FunctionMetaInfo(
            name="file_uploaden",
            return_data_types=[DataType.str],
            parameters=[
                ParameterMetaInfo(
                    name="file_name",
                    data_types=[DataType.str],
                    allow_child_functions=False,
                ),
                ParameterMetaInfo(
                    name="file",
                    data_types=[DataType.str],
                    allow_child_functions=False,
                )
            ]
        )

        def method(self):
            return self.file

    class RandomIBAN(FunctionBase):

        _metainfo = FunctionMetaInfo(
            name="random_IBAN",
            return_data_types=[DataType.str],
            allow_child_functions=False,
            parameters=[]
        )

        @classmethod
        def _generate_elfproef_number(cls):
            while True:
                number = str(random.randint(1000000000, 9999999999))
                if sum([int(num) for num in number[::2]]) - sum([int(num) for num in number[1::2]]) == 0:
                    return number

        @classmethod
        def _random_mod97(cls):
            number = random.randint(0, 99999999)
            control = number % 97
            if control < 10:
                control = f"{control:02d}"
            return control

        @classmethod
        def _number_iban(cls, iban):
            return (iban[4:] + iban[:4]).translate(LETTERS)

        @classmethod
        def _generate_iban_check_digits(cls, iban):
            number_iban = cls._number_iban(iban[:2] + '00' + iban[4:])
            return '{:0>2}'.format(98 - (int(number_iban) % 97))

        @classmethod
        def _valid_iban(cls, iban):
            return int(cls._number_iban(iban)) % 97 == 1

        @classmethod
        def _generate_bank_account_number(cls):
            bank_code = ''.join(random.choices(bank_codes))
            account_number = cls._generate_elfproef_number()
            control_number = cls._random_mod97()
            return f"{country_code}{control_number}{bank_code}{account_number}"

        def method(self) -> str:
            new_code = self._generate_bank_account_number()
            return new_code if (self._generate_iban_check_digits(new_code) == new_code[2:4]) and self._valid_iban(
                new_code) else self.method()
            pass

    class DateDifference(FunctionBase):
        eerste_datum: str
        tweede_datum: str
        weekend_dagen_meenemen: bool

        _metainfo = FunctionMetaInfo(
            name="Datumverschil",
            return_data_types=[DataType.int],
            parameters=[
                ParameterMetaInfo(
                    name="eerste_datum",
                    data_types=[DataType.str],
                    allow_child_functions=True,
                ),
                ParameterMetaInfo(
                    name="tweede_datum",
                    data_types=[DataType.str],
                    allow_child_functions=True,
                ),
                ParameterMetaInfo(
                    name="weekend_dagen_meenemen",
                    data_types=[DataType.boolean],
                    values=[
                        {
                            "id": "True",
                            "description": True,
                        },
                        {
                            "id": "False",
                            "description": False,
                        },
                    ],
                    default_value=False,
                    allow_child_functions=False,
                ),
            ]
        )

        @classmethod
        def _end_date_later_then_begin_date(cls, first_date: datetime, last_date: datetime):
            days_between_dates = (last_date - first_date).days
            return True if days_between_dates < 0 else False

        def method(self) -> int:
            days_between: int
            first_date = format_date(self.eerste_datum)
            second_date = format_date(self.tweede_datum)
            negative_day = self._end_date_later_then_begin_date(first_date, second_date)
            if negative_day:
                date1 = second_date
                date2 = first_date
            else:
                date1 = first_date
                date2 = second_date

            all_days = (date1 + timedelta(x + 1) for x in range((date2 - date1).days))
            if not self.weekend_dagen_meenemen:
                days_between = sum(1 for day in all_days if day.weekday() < 5)
            else:
                days_between = sum(1 for day in all_days)

            if negative_day:
                days_between = -days_between
            return days_between


# if __name__ == "__main__":
#     EXCLUDED_ATTRS = {
#         "seed", "seed_instance", "random", "add_provider", "factories", "format", "generator_attrs", "get_arguments",
#         "get_formatter", "get_providers", "items", "locales", "parse", "provider", "providers", "seed_locale",
#         "set_arguments", "set_formatter", "unique", "cache_pattern", "weights"
#     }
#     fake = Faker("nl_NL")
#     try:
#         options = [attr for attr in dir(fake) if not attr.startswith("_") and attr not in EXCLUDED_ATTRS]
#     except TypeError:
#         pass
#     for i in options:
#         print(i)
#         # at = getattr(fake, i)
#         # try:
#         #     parameters = signature(at).parameters
#         #     print(signature(at).parameters.get("nb"))
#         # except Exception:
#         #     pass


if __name__ == '__main__':
    # a = Functions.RandomDate(begin_datum="2020-02-05", eind_datum="2021-05-09", weekend_dagen_meenemen=False)
    a = Functions.IfElse(waarde_genereren=10.000, operator=">", als_waarde=10.011, dan_waarde=50, anders=8888)
    print(a.method())
