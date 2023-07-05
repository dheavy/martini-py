# This will make sure the Celery app is always imported when
# Django starts so that shared_task will use this app.
from .celery import celery as celery_app

__all__ = ('celery_app',)
