from fastapi import APIRouter

pdf_router = APIRouter(
    prefix="/pdf",
)

from . import tasks # noqa
