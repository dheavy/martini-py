from typing import Optional

from celery import shared_task
from celery.utils.log import get_task_logger

from martini.pdf.models import save_pdf_and_embeddings

logger = get_task_logger(__name__)


@shared_task(bind=True)
def store_embeddings(
    self,
    docs: list[str] = None,
    index_name: str = None,
    namespace: Optional[str] = None,
    dimension: int = 0,
):
    '''
    Celery task to store embeddings in Pinecone
    and save model representing PDF instance in database.

    During this operation, the status of the task can be checked
    via the /pdf/status/{task_id} endpoint.
    '''
    try:
        pdf = save_pdf_and_embeddings(
            docs=docs,
            index_name=index_name,
            dimension=dimension,
            namespace=namespace,
        )
        return pdf
    except Exception as e:
        logger.error('Embeddings storage failed, retrying after 5 seconds. Error: %s', e)
        raise self.retry(exc=e, countdown=5)
