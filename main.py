from celery import Celery
from martini import create_app


celery = Celery(
    __name__,
    broker="redis://127.0.0.1:32787/0",
    backend="redis://127.0.0.1:32787/0",
)

app = create_app()
celery = app.celery_app
