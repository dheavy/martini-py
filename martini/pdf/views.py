import os
import re
import shutil
import unicodedata
from typing import List

from fastapi import UploadFile, File, status
from fastapi.responses import JSONResponse

from celery.result import AsyncResult

from langchain.document_loaders import PyPDFLoader
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from . import pdf_router
from .tasks import store_embeddings

@pdf_router.post('/upload', status_code=status.HTTP_202_ACCEPTED)
def upload(file: UploadFile = File(...)) -> JSONResponse:
    '''Upload a PDF file to the server and store its embeddings in Pinecone.'''
    filepath = f'static/uploads/{file.filename}'

    # Save file to disk.
    with open(filepath, 'wb') as f:
        shutil.copyfileobj(file.file, f)

    # Chunk document into smaller documents.
    # Makes it easier to store and compare embeddings,
    # and do similarity search and other things in documents.
    docs = [t.page_content for t in chunk_document(filepath)]

    # Store embeddings in Pinecone through a Celery task.
    # Index name is truncated if too long to fit in Pinecone.
    embeddings_dimension = int(os.environ.get('EMBEDDINGS_DIMENSION_OPENAI'))
    index_name_len = int(os.environ.get('EMBEDDINGS_INDEX_NAME_LENGTH'))
    index_name = slugify(file.filename)[:index_name_len].removesuffix('-')
    task = store_embeddings.delay(
        docs=docs,
        index_name=index_name,
        namespace=file.filename,
        dimension=embeddings_dimension
    )

    return JSONResponse({
        'message': 'File uploaded successfully, processing embeddings...',
        'task_id': task.id,
    })


@pdf_router.get("/status/{task_id}")
def task_status(task_id: str) -> JSONResponse:
    '''Check the status of a PDF upload and embedding Celery task.'''
    task = AsyncResult(task_id)
    state = task.state

    if state == 'FAILURE':
        error = str(task.result)
        response = {
            'state': state,
            'error': error,
        }
    else:
        response = {
            'state': state,
        }

    return JSONResponse(response)


def chunk_document(filepath: str) -> List[Document]:
    '''
    Chunks a PDF document into smaller documents.
    '''
    loader = PyPDFLoader(filepath)
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
    docs = text_splitter.split_documents(data)
    return docs


def slugify(value) -> str:
    '''
    Converts to lowercase, removes non-word characters (alphanumerics and
    underscores) and converts spaces to hyphens. Also strips leading and
    trailing whitespace. Stolen from Django's slugify function.
    '''
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    return re.sub('[-\s]+', '-', value)
