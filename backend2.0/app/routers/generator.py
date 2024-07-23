import time

from database.database import DatabaseSession, db_connection
from fastapi import APIRouter, Depends
from generator.schemas.input import ConfigurationDashboard
from generator.core import Engine
from generator.functions.methods import Functions
from generator.functions.utils import compose_functions_metainfo
from profit.utils import set_primary_keys_right_dict
from generator.profit import Fuel
from routers.database import get_methods
from errors import GeneratorError, ErrorCode

router = APIRouter()


@router.get("/functions_metainfo")
async def get_functions_info(methods=Depends(get_methods)):
    return compose_functions_metainfo(Functions, methods)


@router.post("/templates/{template_id}/processes/{process_id}/generate")
async def generate(
        template_id: int,
        process_id: int,
        configurations: ConfigurationDashboard,
        db: DatabaseSession = Depends(db_connection),
):
    if configurations.process_settings.send_method == "":
        raise GeneratorError(ErrorCode.U0020)

    profit_start_time = time.monotonic()
    fuel = Fuel(db, template_id, process_id, configurations)
    await fuel.compose()
    profit_completed_time = round((time.monotonic() - profit_start_time), 2)

    generation_start_time = time.monotonic()
    engine = Engine(fuel)
    engine.run()

    result = engine.generated_data
    result_pk = []
    empty_row_message = ""
    if result["row_removed"]:
        empty_row_message = "Het aantal rijen is minder, omdat er op sommige plekken het woord ##DELETE is gebruikt " \
                            "of gebruik gemaakt is van de functie Bronwaarde met vaste waarde."
    for row in result["generated_data"]:
        result_pk.append(set_primary_keys_right_dict(fuel.raw_metainfo, row, False))
    generation_complete_time = round((time.monotonic() - generation_start_time) * 1000, 2)

    response = {
        "rows": result["generated_data"],
        "group_sizes": len(result["generated_data"]),
        "profit_time_seconds": profit_completed_time,
        "generation_time_milliseconds": generation_complete_time,
        "empty_row": empty_row_message,
        "rows_pk": result_pk
    }
    return response
