import os

from celery import shared_task
from celery.utils.log import get_task_logger

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Qdrant
from langchain.document_loaders import PyPDFLoader
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter

from qdrant_client import QdrantClient

from .qdrant import qd_client

logger = get_task_logger(__name__)
qd_client = QdrantClient(url=os.environ.get('QDRANT_URL'), prefer_grpc=True)


def chunk_document(filepath: str) -> list[str]:
    '''
    Chunks a PDF document into smaller documents.
    '''
    loader = PyPDFLoader(filepath)
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
    docs = text_splitter.split_documents(data)
    return docs

def get_embeddings_model() -> OpenAIEmbeddings:
    '''
    Create embedding model. Use OpenAI's' by default.
    <|endoftext|> is a special token that indicates the end of a document in OpenAI's embeddings.
    We need to set this as `allowed_special` here for tiktoken to parse it without error.
    '''
    return OpenAIEmbeddings(
        openai_api_key=os.environ.get('OPENAI_API_KEY'),
        allowed_special={'<|endoftext|>'}
    )

def get_vdb_for_chains(embeddings: OpenAIEmbeddings, collection_name='') -> QdrantClient:
    '''
    Create and return a Langchain-wrapped Qdrant client (vector database),
    optimized for usage in Langchain's chains.
    '''
    return Qdrant(
        client=qd_client,
        collection_name=collection_name,
        embeddings=embeddings
    )

@shared_task(bind=True)
def store_embeddings(self, filepath: str, collection_name=''):
    '''
    Celery task creating embeddings and storing them in Qdrant.
    During this operation, the status of the task can be checked
    via the ???/{task_id} endpoint.
    '''
    try:
        docs = chunk_document(filepath)
        embeddings = get_embeddings_model()
        qdrant = get_vdb_for_chains(embeddings, collection_name=collection_name)
        qdrant.add_texts(docs)
        # docsearch = qdrant.from_documents(docs, embeddings)
    except Exception as e:
        logger.error('Embeddings storage failed, retrying after 5 seconds. Error: %s', e)
        raise self.retry(exc=e, countdown=5)
