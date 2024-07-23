import json
from typing import Any, Dict, Literal
import asyncio
import time

import orjson
from aiohttp import ClientSession, TCPConnector
from aiohttp.client_exceptions import (
    ClientConnectionError,  ## Geen bevoegdheid voor hogere tier code.
    ClientConnectorCertificateError,  ## Cetificaat error
    ClientConnectorError,  ## De connector heeft uitzonderingen, waarop je bent gestuit
    ClientConnectorSSLError,  ## De responsedata overtreed de SSL (Secure Sockets Layer)
    ClientError,  ## Basisclass voor specifieke uitzonderingen per gebruiker.
    ClientHttpProxyError,  ## Voor deze verbinding heb je specifieke authenticatie codes nodig en die ontbreken.
    ClientOSError,  ## Het OS geeft specifieke eigen errors.
    ClientPayloadError,  ## Response data is niet in het goede format of bestaat helemaal niet
    ClientProxyConnectionError,  ## Zie message bij ClientConnectorError
    ClientResponseError,  ## De ontvangen data is niet in het goede datatype(JSON) of kan niet uitgelezen worden
    ClientSSLError,  ## Zie message bij ClientConnectorError
    ContentTypeError,  ## Als een parameter niet in het goede datatype staat(JSON),
    InvalidURL,  ## Niet bestaande URL
    ServerConnectionError,  ## Kan geen connectie maken met de specifieke server.
    ServerDisconnectedError,  ## Server is uit
    ServerFingerprintMismatch,  ## Zie message bij ServerConnectionError
    ServerTimeoutError,  ## Timeout gekregen van de server met reden van AFK of gegevenswijziging.
    WSServerHandshakeError,  ## Websocket ligt er uit.
)
from loguru import logger

from errors import ErrorCode, ProfitError, GeneratorError
from profit.utils import flatten_metainfo, get_token_headers, get_keys, set_primary_keys_right_dict

TCP_LIMIT = 35  # Profit block at limit >= 70 (or less?)
JSON_ENCODER = orjson.dumps
JSON_DECODER = orjson.loads


async def session_conn():
    conn = TCPConnector(verify_ssl=False, limit=TCP_LIMIT)
    session = ClientSession(connector=conn)
    return session


async def profit_request(
        method: Literal["GET", "POST", "PUT", "DELETE"],
        url: str,
        environment_token: str,
        *,
        params: dict = None,
        data: Dict[str, Any] = None,
        **kwargs: Dict[str, Any],
) -> Any:
    headers = get_token_headers(environment_token)
    session = await session_conn()
    try:  # TODO: Error handling
        async with session.request(method=method, url=url, headers=headers, params=params, data=json.dumps(data),
                                   **kwargs) as resp:
            try:
                response = await resp.json(loads=JSON_DECODER)
                lack_off_response = {
                    "response": "Update/Delete went well"
                }
                if response is None:
                    response = lack_off_response

                return response
            except (ContentTypeError, ClientResponseError) as e:
                raise ProfitError(ErrorCode.P0009, profit_msg=e.message, profit_status=e.status,
                                  aiohttp_error=type(e).__name__)
            except WSServerHandshakeError as e:
                raise ProfitError(ErrorCode.P0011, profit_msg=e.message, profit_status=e.status,
                                  aiohttp_error=type(e).__name__)
            except ClientHttpProxyError as e:
                raise ProfitError(ErrorCode.P0007, profit_msg=e.message, profit_status=e.status,
                                  aiohttp_error=type(e).__name__)
            except ClientConnectorCertificateError as e:
                raise ProfitError(ErrorCode.P0003, aiohttp_error=type(e).__name__)
            except ClientConnectorSSLError as e:
                raise ProfitError(ErrorCode.P0005, aiohttp_error=type(e).__name__)
            except (ClientSSLError, ClientProxyConnectionError, ClientConnectorError) as e:
                raise ProfitError(ErrorCode.P0004, aiohttp_error=type(e).__name__)
            except (ServerDisconnectedError, ServerTimeoutError, ServerFingerprintMismatch, ServerConnectionError) as e:
                raise ProfitError(ErrorCode.P0011, aiohttp_error=type(e).__name__)
            except ClientOSError as e:
                raise ProfitError(ErrorCode.P0008, aiohttp_error=type(e).__name__)
            except ClientConnectionError as e:
                raise ProfitError(ErrorCode.P0002, aiohttp_error=type(e).__name__)
            except ClientPayloadError as e:
                raise ProfitError(ErrorCode.P0009, aiohttp_error=type(e).__name__)
            except InvalidURL as e:
                raise ProfitError(ErrorCode.P0010, aiohttp_error=type(e).__name__)
            except ClientError as e:
                raise ProfitError(ErrorCode.P0006, aiohttp_error=type(e).__name__)
            except Exception as e:  # TODO: maybe do specific catching on deserialization
                raise ProfitError(ErrorCode.P0000, aiohttp_error=type(e).__name__, decode_error=True)

    except (ContentTypeError, ClientResponseError) as e:
        raise ProfitError(ErrorCode.P0009, profit_msg=e.message, profit_status=e.status, aiohttp_error=type(e).__name__)
    except WSServerHandshakeError as e:
        raise ProfitError(ErrorCode.P0011, profit_msg=e.message, profit_status=e.status, aiohttp_error=type(e).__name__)
    except ClientHttpProxyError as e:
        raise ProfitError(ErrorCode.P0007, profit_msg=e.message, profit_status=e.status, aiohttp_error=type(e).__name__)
    except ClientConnectorCertificateError as e:
        raise ProfitError(ErrorCode.P0003, aiohttp_error=type(e).__name__)
    except ClientConnectorSSLError as e:
        raise ProfitError(ErrorCode.P0005, aiohttp_error=type(e).__name__)
    except (ClientSSLError, ClientProxyConnectionError, ClientConnectorError) as e:
        raise ProfitError(ErrorCode.P0004, aiohttp_error=type(e).__name__)
    except (ServerDisconnectedError, ServerTimeoutError, ServerFingerprintMismatch, ServerConnectionError) as e:
        raise ProfitError(ErrorCode.P0011, aiohttp_error=type(e).__name__)
    except ClientOSError as e:
        raise ProfitError(ErrorCode.P0008, aiohttp_error=type(e).__name__)
    except ClientConnectionError as e:
        raise ProfitError(ErrorCode.P0002, aiohttp_error=type(e).__name__)
    except ClientPayloadError as e:
        raise ProfitError(ErrorCode.P0009, aiohttp_error=type(e).__name__)
    except InvalidURL as e:
        raise ProfitError(ErrorCode.P0010, aiohttp_error=type(e).__name__)
    except ClientError as e:
        raise ProfitError(ErrorCode.P0006, aiohttp_error=type(e).__name__)


async def get_profit_version(endpoint: str, environment_token: str):
    url = f"{endpoint}/ProfitRestServices/profitversion"
    iets = await profit_request("GET", url, environment_token)
    logger.info(iets)
    # return await profit_request("GET", url, environment_token)
    return iets

    # try:  # TODO: eventueel speciefieke error handeling toevoegen, geld voor alle connection functies
    #     return await profit_request("GET", url, environment_token)
    # except ProfitError:
    #     raise


async def get_meta_info(endpoint: str, environment_token: str):
    url = f"{endpoint}/ProfitRestServices/metainfo"
    return await profit_request("GET", url, environment_token)


async def get_connector_metainfo(endpoint: str, environment_token: str, connector: str):
    url = f"{endpoint}/ProfitRestServices/metainfo/get/{connector}"
    return await profit_request("GET", url, environment_token)


async def get_connector_data(endpoint: str, environment_token: str, connector: str, params: dict = None):
    url = f"{endpoint}/ProfitRestServices/connectors/{connector}"
    return await profit_request("GET", url, environment_token, params=params)


async def update_connector_metainfo(endpoint: str, environment_token: str, connector: str):
    url = f"{endpoint}/ProfitRestServices/metainfo/update/{connector}"
    profit_metainfo = await profit_request("GET", url, environment_token)
    metainfo = {
        "id": profit_metainfo["id"],
        "description": profit_metainfo["description"],
        "name": profit_metainfo["name"],
        "connectors": [],
    }
    flatten_metainfo(metainfo, profit_metainfo, metainfo["name"])
    return metainfo


async def update_connector_post(endpoint: str, environment_token: str, connector: str, send_method: str,
                                data: list) -> dict or str:
    start_time = time.monotonic()

    url = f"{endpoint}/ProfitRestServices/connectors/{connector}"
    tasks = []
    metainfo = await update_connector_metainfo(endpoint, environment_token, connector)

    if send_method == "POST":
        for generated_dict in data:
            new_dict = set_primary_keys_right_dict(metainfo, generated_dict, True)
            task = asyncio.create_task(profit_request("POST", url, environment_token, data=new_dict))
            tasks.append(task)
        profit_responses = await asyncio.gather(*tasks)
    elif send_method == "PUT":
        for generated_dict in data:
            new_dict = set_primary_keys_right_dict(metainfo, generated_dict, True)
            task = asyncio.create_task(profit_request("PUT", url, environment_token, data=new_dict))
            tasks.append(task)
        profit_responses = await asyncio.gather(*tasks)

    elif send_method == "DELETE":
        for generated_dict in data:
            new_dict = set_primary_keys_right_dict(metainfo, generated_dict, True)
            task = asyncio.create_task(
                update_connector_delete(endpoint, environment_token, connector, send_method, new_dict))
            tasks.append(task)
        profit_responses = await asyncio.gather(*tasks)
    else:
        raise GeneratorError(ErrorCode.B0007)

    groups_amount = len(profit_responses)
    failed_groups_amount = len([group for group in profit_responses if "errorNumber" in group])
    successful_groups_amount = groups_amount - failed_groups_amount

    completed_time = time.monotonic() - start_time
    logger.info(completed_time)

    response = {
        "groups_amount": groups_amount,
        "successful_groups_amount": successful_groups_amount,
        "failed_groups_amount": failed_groups_amount,
        "export_time": round(completed_time, 2),
        "responses": profit_responses
    }

    return response


async def update_connector_put(endpoint: str, environment_token: str, connector: str, data: dict) -> dict or str:
    url = f"{endpoint}/ProfitRestServices/connectors/{connector}"
    return await profit_request("PUT", url, environment_token, data=data)


async def update_connector_delete(endpoint: str, environment_token: str, connector: str, send_method: str,
                                  data: dict) -> dict or str:
    final_url = get_keys([], data)
    url = f"{endpoint}/ProfitRestServices/connectors/{connector}/{final_url[:-1]}"
    return await profit_request("DELETE", url, environment_token)
