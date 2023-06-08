import shutil
from typing import List

from fastapi import UploadFile, File, status
from fastapi.responses import JSONResponse

from celery.result import AsyncResult

from langchain.document_loaders import PyPDFLoader
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from . import pdf_router
from .tasks import store_embeddings

@pdf_router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
def upload(file: UploadFile = File(...)):
    """Upload a PDF file to the server and store its embeddings in Pinecone."""
    filepath = f"static/uploads/{file.filename}"

    # Save file to disk.
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Chunk document into smaller documents.
    # Makes it easier to store and compare embeddings,
    # and do similarity search through a token-limited LLM.
    docs = chunk_document(filepath)

    # Store embeddings in Pinecone through a Celery task.
    task = store_embeddings.delay(docs, file.filename, file.filename)

    return JSONResponse({
        "message": "File uploaded successfully, processing embeddings...",
        "task_id": task.id,
    })


@pdf_router.get("/status/{task_id}")
def task_status(task_id: str):
    """Check the status of a PDF upload and embedding Celery task."""
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
    loader = PyPDFLoader(filepath)
    data = loader.load()
    print (f'You have {len(data)} document(s) in your data')
    print (f'There are {len(data[30].page_content)} characters in your document')
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0)
    docs = text_splitter.split_documents(data)
    print (f'Now you have {len(docs)} documents')
    return docs
