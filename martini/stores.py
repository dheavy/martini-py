import os
import time
from typing import Optional

from celery.utils.log import get_task_logger

import pinecone


def upload_embeddings(
    docs: list[str] = None,
    index_name: str = None,
    namespace: Optional[str] = None,
    dimension: int = 0
):
    from langchain.vectorstores import Pinecone
    from langchain.embeddings.openai import OpenAIEmbeddings

    logger = get_task_logger(__name__)

    # Initialize Pinecone.
    pinecone.init(
        api_key=os.environ.get('PINECONE_API_KEY'),
        environment=os.environ.get('PINECONE_API_ENV'),
    )

    # Use OpenAI embeddings by default.
    # <|endoftext|> is a special token that indicates the end of
    # a document in OpenAI's embeddings. # We need to set this
    # as `allowed_special` here for tiktoken to parse it without error.
    embeddings = OpenAIEmbeddings(
        openai_api_key=os.environ.get('OPENAI_API_KEY'),
        allowed_special={'<|endoftext|>'}
    )

    # Upsert index: first, verify if index exists
    # If yes, then add embeddings. Otherwise create index before adding.
    indexes = pinecone.list_indexes()
    logger.info(f'Pinecone indexes: {indexes}')

    if index_name not in indexes:
        logger.info(f'Creating Pinecone index: {index_name}')
        pinecone.create_index(name=index_name, dimension=dimension, pods=0)

    logger.info('Start adding embeddings to Pinecone...')
    Pinecone.from_texts(docs, embeddings, index_name=index_name, namespace=namespace)

    index = pinecone.Index(index_name)
    total_uploaded = int(index.describe_index_stats()['total_vector_count'])
    logger.info(f'Done! Added {total_uploaded} embeddings ({len(docs)} documents) to Pinecone index "{index_name}"')
