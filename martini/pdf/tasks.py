import os
from typing import List, Optional

from langchain.docstore.document import Document

from celery import shared_task
from celery.utils.log import get_task_logger

from martini.stores import upload_embeddings

logger = get_task_logger(__name__)


@shared_task(bind=True)
async def store_embeddings(
    self,
    docs: List[Document],
    index_name: str,
    namespace: Optional[str] = None,
    dimension: int = os.environ.get("EMBEDDINGS_DIMENSION_OPENAI")
):
    try:
        # Recceive initialized Pinecone instance from upload_embeddings.
        pinecone_instance = await upload_embeddings(
            docs,
            index_name,
            namespace,
            dimension
        )

        # Wait for Pinecone to index embeddings.
        index = pinecone_instance.Index(index_name)
        while not index.describe_index_stats()["total_vector_count"] == len(docs):
            logger.info("waiting for Pinecone to index embeddings")
            os.sleep(5)

    except Exception as e:
        logger.error("embeddings storage failed, retrying after 5 seconds")
        raise self.retry(exc=e, countdown=5)
