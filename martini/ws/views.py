import json

from fastapi import WebSocket

from . import ws_router
from martini import broadcast
from martini.celery import get_task_info


@ws_router.websocket("/task/status/{task_id}")
async def ws_task_status(websocket: WebSocket):
    await websocket.accept()

    task_id = websocket.scope["path_params"]["task_id"]

    async with broadcast.subscribe(channel=task_id) as subscriber:
        # Check in case the task already finished.
        data = get_task_info(task_id)
        await websocket.send_json(data)

        async for event in subscriber:
            await websocket.send_json(json.loads(event.message))


async def update_celery_task_status(task_id: str):
    """
    Called by Celery worker in task_postrun signal handler,
    that is, after the task has finished.
    """
    await broadcast.connect()
    await broadcast.publish(
        channel=task_id,
        message=json.dumps(get_task_info(task_id))  # RedisProtocol.publish expects str
    )
    await broadcast.disconnect()
