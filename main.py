from importlib import reload

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from core.transport.rest import router
from core.transport.graphql import graphql_router
from core.errors.base import MPDriverException
app = FastAPI()
app.include_router(router)
app.include_router(graphql_router, prefix="/graphql")


@app.exception_handler(MPDriverException)
async def mpdriver_exception(request: Request, exc: MPDriverException):
    return exc.response()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error = exc.errors()[0]
    raise MPDriverException(422, error['type'], error['msg'])
