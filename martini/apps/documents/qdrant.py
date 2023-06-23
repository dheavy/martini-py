import os

from qdrant_client import QdrantClient
from qdrant_client.http import models

qd_client = QdrantClient(url=os.environ.get('QDRANT_URL'), prefer_grpc=True)

def create_vdb_collection(collection_name: str):
    qd_client.recreate_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=os.environ.get('EMBEDDINGS_DIMENSION_OPENAI'),
            distance=models.Distance.COSINE
        ),
    )

def delete_vdb_collection(collection_name: str):
    qd_client.delete_collection(collection_name=collection_name)
