from broadcaster import Broadcast
from fastapi import FastAPI

from martini.config import settings

# Used by FastAPI to broadcast WS messages to all connected clients
broadcast = Broadcast(settings.WS_MESSAGE_QUEUE)


def create_app() -> FastAPI:
    """
    Factory function: create a FastAPI instance and return it.
    Also creates a Celery app instance and attaches it to the FastAPI app instance,
    and declares the routes, including a WebSocket route for Celery task status updates.
    """
    app = FastAPI()

    # do this before loading routes
    from martini.celery import create_celery
    app.celery_app = create_celery()

    from martini.pdf import pdf_router
    app.include_router(pdf_router)

    from martini.ws import ws_router                   # new
    app.include_router(ws_router)

    @app.on_event("startup")
    async def startup_event():
        await broadcast.connect()

    @app.on_event("shutdown")
    async def shutdown_event():
        await broadcast.disconnect()

    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    return app
