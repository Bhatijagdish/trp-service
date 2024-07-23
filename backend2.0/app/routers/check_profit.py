from fastapi import APIRouter

from profit import connections

router = APIRouter()


@router.post("/check_profit_version")
async def check_profit_version(data: dict):
    return await connections.get_profit_version(data["profit_endpoint"], data["token"])
