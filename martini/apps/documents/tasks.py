import os

from celery import shared_task
from celery.utils.log import get_task_logger

from apps.documents.models import UnstructuredDocument

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3)
def save_embeddings(
    self,
    filepath: str = None,
    collection_name: str = None,
    doc_name: str = None,
    instance_id: int = None
):
    '''
    Celery task creating embeddings and storing them in Qdrant using the
    class method in UnstructuredDocument.
    During this operation, the status of the task can be checked
    via the /api/documents/{task_id}/status endpoint.

    Note: not used in local development.

    Args:
        filepath (str): Path to the file to process.
        collection_name (str): Name of the collection to store the embeddings in.
        doc_name (str): Name of the document the embeddings are extracted from;
            this is used as a marker in the metadata of the embeddings for when
            the document is deleted.
        instance_id (int): ID of the UnstructuredDocument instance.
    '''
    from apps.documents.exceptions import UnprocessableDocumentError

    try:
        UnstructuredDocument.save_embeddings(
            filepath,
            collection_name,
            doc_name,
            instance_id
        )
    except Exception as e:
        # Check exception type to avoid retrying on non-retryable errors.
        if isinstance(e, UnprocessableDocumentError):
            logger.error(f'Embeddings storage failed, Aborting. Error: {e}')
        else:
            try:
                logger.error(f'Embeddings storage failed, retrying after 5 seconds. Error: {e}')
                raise self.retry(exc=e, countdown=5)
            except self.MaxRetriesExceededError:
                logger.error('Max retries exceeded for task %s', self.request.id)

@shared_task(bind=True, max_retries=3)
def delete_embeddings(self, collection_name: str, doc_name: str, instance_id: int):
    '''
    Celery task deleting embeddings from Qdrant using the
    class method in UnstructuredDocument.
    During this operation, the status of the task can be checked
    via the /api/documents/{task_id}/status endpoint.

    Note: not used in local development.

    Args:
        collection_name (str): Name of the collection to store the embeddings in.
        doc_name (str): Name of the document the embeddings are extracted from;
            this is used as a marker in the metadata of the embeddings for when
            the document is deleted.
        instance_id (int): ID of the UnstructuredDocument instance.
    '''
    from apps.documents.models import UnstructuredDocument

    if not collection_name or not doc_name or not instance_id:
        raise ValueError('collection_name, doc_name and instance_id must be specified')

    try:
        UnstructuredDocument.delete_embeddings(collection_name, doc_name, instance_id)
    except Exception as e:
        logger.error('Embeddings deletion failed, retrying after 5 seconds. Error: %s', e)
        raise self.retry(exc=e, countdown=5)
