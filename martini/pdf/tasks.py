from typing import Optional

from langchain.docstore.document import Document

from celery import shared_task
from celery.utils.log import get_task_logger

from martini.stores import upload_embeddings

logger = get_task_logger(__name__)


@shared_task(bind=True)
def store_embeddings(
    self,
    docs: list[str] = None,
    index_name: str = None,
    namespace: Optional[str] = None,
    dimension: int = 0,
):
    try:
        upload_embeddings(
            docs=docs,
            index_name=index_name,
            namespace=namespace,
            dimension=dimension,
        )
    except Exception as e:
        logger.error('Embeddings storage failed, retrying after 5 seconds. Error: %s', e)
        raise self.retry(exc=e, countdown=5)
