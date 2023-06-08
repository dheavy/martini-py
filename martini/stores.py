import os
from typing import List, Optional

from langchain.docstore.document import Document

import pinecone


async def upload_embeddings(
    docs: List[Document],
    index_name: str,
    namespace: Optional[str] = None,
    dimension: int = os.environ.get("EMBEDDINGS_DIMENSION_OPENAI")
):
    from langchain.vectorstores import Pinecone
    from langchain.embeddings.openai import OpenAIEmbeddings

    # Initialize Pinecone.
    pinecone.init(
        api_key=os.environ.get("PINECONE_API_KEY"),
        environment=os.environ.get("PINECONE_API_ENV"),
    )

    # Use OpenAI embeddings by default.
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ.get("OPENAI_API_KEY"))

    # Upsert index: first, verify if index exists
    # If yes, then add embeddings. Otherwise create index before adding.
    indexes = pinecone.list_indexes()

    if index_name not in indexes:
        pinecone.create_index(name=index_name, dimension=dimension)

    Pinecone.from_texts(docs, embeddings, index_name=index_name, namespace=namespace)

    return pinecone
