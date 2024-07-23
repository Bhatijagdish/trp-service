from typing import List
import asyncio
import json

from database import constants, crud, schemas, utils
from profit import connections
from database.database import db_connection
from routers.entity import get_process_dashboard
from fastapi import APIRouter, Depends
from pydantic import NonNegativeInt
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/csv_files", response_model=List[schemas.CSVFileGet])
async def get_csv_files(
        skip: int = constants.DEFAULT_SKIP, take: int = constants.DEFAULT_TAKE, db: Session = Depends(db_connection)
):
    return await crud.get_csv_files(db, skip, take)


@router.post("/csv_file", response_model=schemas.CSVFileGet)
async def create_csv_file(csv_file: schemas.CSVFileCreate, db: Session = Depends(db_connection)):
    return await crud.create_csv_file(db, csv_file)


@router.get("/csv_file", response_model=schemas.CSVFileGet)
async def get_csv_file(csv_id: NonNegativeInt, db: Session = Depends(db_connection)):
    return await crud.get_csv_file(db, csv_id)


@router.put("/csv_file", response_model=schemas.CSVFileGet)
async def update_csv_file(
        csv_id: NonNegativeInt, csv_file: schemas.CSVFileUpdate, db: Session = Depends(db_connection)
):
    return await crud.update_csv_file(db, csv_id, csv_file)


@router.delete("/csv_file", response_model=schemas.CSVFileGet)
async def delete_csv_file(csv_id: NonNegativeInt, db: Session = Depends(db_connection)):
    return await crud.delete_csv_file(db, csv_id)


@router.get("/templates/{template_id}/processes/{process_id}/length_sources")
async def get_length_sources(
        template_id: NonNegativeInt,
        process_id: NonNegativeInt,
        db: Session = Depends(db_connection)
):
    db_template = await crud.get_template(db, template_id)
    db_dashboard = await crud.get_process_dashboard(db, template_id, process_id)

    tasks = []
    for source in db_dashboard.data_sources:
        task = asyncio.create_task(utils.get_source_length(db_template, db_dashboard.data_sources, source))
        tasks.append(task)
    source_lengths = await asyncio.gather(*tasks)
    return source_lengths


@router.get("/templates/{template_id}/processes/{process_id}/source_filter_options")
async def get_source_filter_options(
        template_id: NonNegativeInt,
        process_id: NonNegativeInt,
        db: Session = Depends(db_connection)
):
    db_template = await crud.get_template(db, template_id)
    meta_info = await connections.get_meta_info(db_template.profit_endpoint, db_template.token)
    process_dashboard = await get_process_dashboard(template_id, process_id, True, db)
    csv_files = []
    for source in process_dashboard.data_sources:
        new_csv = {}
        if source.source.type_source == "csv" and source.filter_source is None:
            new_csv["name"] = source.source.csv_file.file_name
            csv_dict = json.loads(source.source.csv_file.file)
            new_csv["fields"] = [*csv_dict[0]]
            csv_files.append(new_csv)
    tasks = []

    for connector in meta_info["getConnectors"]:
        tasks.append(asyncio.create_task(
            connections.get_connector_metainfo(db_template.profit_endpoint, db_template.token, connector["id"])
        ))
    connectors_metainfo = await asyncio.gather(*tasks)

    result = []
    for connector in connectors_metainfo:
        item = {
            "type_source": "GetConnector",
            "source_name": connector["name"],
            "csv_id": None,
            "filter_options": []
        }
        fields = [field["label"] for field in connector["fields"]]
        for filter_connector in connectors_metainfo:
            if filter_connector["name"] != connector["name"]:
                filter_item_getconnector = {
                    "type_source": "GetConnector",
                    "source_name": filter_connector["name"],
                    "filter_fields": []
                }
                for filter_field in filter_connector["fields"]:
                    if filter_field["label"] in fields:
                        filter_item_getconnector["filter_fields"].append(filter_field["label"])
                if filter_item_getconnector["filter_fields"]:
                    item["filter_options"].append(filter_item_getconnector)
        for file in csv_files:
            if file["name"] != connector["name"]:
                filter_item_csv = {
                    "type_source": "csv",
                    "source_name": file["name"],
                    "filter_fields": [],
                }
                for filter_field in file["fields"]:
                    if filter_field in fields:
                        filter_item_csv["filter_fields"].append(filter_field)
                if filter_item_csv["filter_fields"]:
                    item["filter_options"].append(filter_item_csv)
        result.append(item)
    return result


@router.post("/templates/{template_id}/csv_filter_options")
async def get_csv_filter_options(
        template_id: NonNegativeInt,
        csv_data: dict,
        db: Session = Depends(db_connection),
):
    db_template = await crud.get_template(db, template_id)
    meta_info = await connections.get_meta_info(db_template.profit_endpoint, db_template.token)
    tasks = []

    for connector in meta_info["getConnectors"]:
        tasks.append(asyncio.create_task(
            connections.get_connector_metainfo(db_template.profit_endpoint, db_template.token, connector["id"])
        ))
    connectors_metainfo = await asyncio.gather(*tasks)
    result = []

    csv_file = json.loads(csv_data["csv_data"])
    fields = [*csv_file[0]]
    for filter_connector in connectors_metainfo:
        filter_item_csv = {
            "type_source": "GetConnector",
            "source_name": filter_connector["name"],
            "filter_fields": []
        }
        for filter_field in filter_connector["fields"]:
            if filter_field["label"] in fields:
                filter_item_csv["filter_fields"].append(filter_field["label"])
        if filter_item_csv["filter_fields"]:
            result.append(filter_item_csv)
    return result
