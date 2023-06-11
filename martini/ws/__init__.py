from fastapi import APIRouter

ws_router = APIRouter(
    prefix='/ws',
)

from . import views # noqa
