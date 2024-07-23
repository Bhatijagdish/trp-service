from fastapi import APIRouter, Depends
from loguru import logger
from datetime import datetime, timedelta

from profit import connections
from pydantic import NonNegativeInt
from routers.template import get_template
from routers.entity import get_process_dashboard
from database import crud, schemas
from database.database import DatabaseSession, db_connection

router = APIRouter()


@router.get("/profit_version")
async def get_profit_version(template=Depends(get_template)):
    return await connections.get_profit_version(template.profit_endpoint, template.token)


@router.get("/metainfo")
async def get_metainfo(template=Depends(get_template)):
    return await connections.get_meta_info(template.profit_endpoint, template.token)


@router.get("/get_connectors")
async def get_connectors(template=Depends(get_template)):
    meta_info = await connections.get_meta_info(template.profit_endpoint, template.token)
    return meta_info["getConnectors"]


@router.get("/get_connectors/{connector}")
async def get_connector_data(
        connector: str, skip: NonNegativeInt = 0, take: NonNegativeInt = 100, template=Depends(get_template)
):
    params = {"skip": skip, "take": take}  # TODO: kan ook met dependency
    return await connections.get_connector_data(template.profit_endpoint, template.token, connector, params=params)


@router.get("/get_connectors/{connector}/metainfo")
async def get_connector_meta_info(connector: str, template=Depends(get_template)):
    return await connections.get_connector_metainfo(template.profit_endpoint, template.token, connector)


@router.get("/update_connectors")
async def update_connectors(template=Depends(get_template)):
    meta_info = await connections.get_meta_info(template.profit_endpoint, template.token)
    return meta_info["updateConnectors"]


@router.post("/update_connectors/{connector}")
async def update_connector_post(connector: str, data: list, process=Depends(get_process_dashboard),
                                template=Depends(get_template), db: DatabaseSession = Depends(db_connection)):
    response = await connections.update_connector_post(template.profit_endpoint,
                                                       template.token,
                                                       connector,
                                                       process.process_settings.send_method,
                                                       data=data
                                                       )
    # Temporary because server is 2 hours late
    # time_exported = (datetime.now() + timedelta(hours=2)).strftime("%d-%m-%Y %H:%M:%S")
    time_exported = (datetime.now() + timedelta(hours=1)).strftime("%d-%m-%Y %H:%M:%S")
    # time_exported = (datetime.now()).strftime("%d-%m-%Y %H:%M:%S")
    percentage_exported = round((response["successful_groups_amount"] / response["groups_amount"]) * 100, 2)

    db_process = await crud.get_process_general(db, template.id, process.id)

    process = schemas.ProcessGeneralUpdate.from_orm(db_process)
    process.last_exported = time_exported
    process.percentage_exported = percentage_exported
    process.amount_failed_groups = response["failed_groups_amount"]
    process.amount_successful_groups = response["successful_groups_amount"]

    # Update the time and export-percentage on the frontpage of the application.
    await crud.update_process_general(db, template_id=template.id, process_id=process.id, process=process)
    logger.error(time_exported)
    return response


@router.get("/update_connectors/{connector}/metainfo")
async def update_connector_meta_info(connector: str, template=Depends(get_template)):
    return await connections.update_connector_metainfo(template.profit_endpoint, template.token, connector)
