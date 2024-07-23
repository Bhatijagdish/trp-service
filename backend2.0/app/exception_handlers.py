import re

from loguru import logger

from errors import RocketError
from fastapi import Request
from fastapi.responses import ORJSONResponse

DEFAULT_ERROR_STATUS_CODE = 400


def rocket_exception_handler(_request: Request, exc: RocketError) -> ORJSONResponse:
    content = {
        "errors": [
            {
                "error": re.sub(r"(?!^)[A-Z]", lambda x: " " + x.group(0).lower(), type(exc).__name__),
                "error_code": exc.error_code.name,
                "error_msg": exc.error_msg,
                **{key: str(value) for key, value in exc.kwargs.items()},
            }
        ]
    }
    logger.error(content)
    status_code = exc.status_code if exc.status_code else DEFAULT_ERROR_STATUS_CODE
    return ORJSONResponse(content, status_code)
