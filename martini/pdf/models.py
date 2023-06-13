import datetime
import os
from typing import Optional

import pinecone
from celery.utils.log import get_task_logger
from sqlalchemy import Column, Integer, String

from martini.database import Base, DateTime, SessionLocal


class Pdf(Base):
    __tablename__ = 'pdfs'

    id = Column(String(128), primary_key=True, index=True, nullable=False)
    index_name = Column(String(50), unique=True, index=True, nullable=False)
    filename = Column(String(250), nullable=False)
    namspace = Column(String(200))
    vector_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<Pdf(id={%s}, index_name={%s}, filename={%s}, vector_count={%s})>' % (
            self.id,
            self.index_name,
            self.filename,
            self.vector_count
        )

def save_pdf_instance(
    id: str,
    index_name: str,
    filename: str,
    namespace: Optional[str] = '',
    vector_count: int = 0,
) -> Pdf:
    '''
    Save a PDF instance in the database, representing a PDF file
    that has been uploaded and processed.
    '''
    session = SessionLocal()

    pdf = Pdf(
        id=id,
        index_name=index_name,
        filename=filename,
        namespace=namespace,
        vector_count=vector_count,
    )

    session.add(pdf)
    session.commit()
    session.refresh(pdf)
    session.close()

    return pdf


def get_pdf_instance_by(key: str, value: str) -> Pdf:
    session = SessionLocal()
    query = session.query(Pdf)

    if key == 'id':
        query = query.filter_by(id=value)
    elif key == 'index_name':
        query = query.filter_by(index_name=value)
    else:
        raise ValueError(f'get_pdf_instance_by - invalid filter key: {key}')

    return query.first()


def save_pdf_and_embeddings(
    docs: list[str] = None,
    index_name: str = None,
    dimension: int = 0,
    namespace: Optional[str] = ''
):
    from langchain.embeddings.openai import OpenAIEmbeddings
    from langchain.vectorstores import Pinecone

    logger = get_task_logger(__name__)

    # Initialize Pinecone.
    pinecone.init(
        api_key=os.environ.get('PINECONE_API_KEY'),
        environment=os.environ.get('PINECONE_API_ENV'),
    )

    # Use OpenAI embeddings by default.
    # <|endoftext|> is a special token that indicates the end of
    # a document in OpenAI's embeddings. We need to set this
    # as `allowed_special` here for tiktoken to parse it without error.
    embeddings = OpenAIEmbeddings(
        openai_api_key=os.environ.get('OPENAI_API_KEY'),
        allowed_special={'<|endoftext|>'}
    )

    indexes = pinecone.list_indexes()
    logger.info(f'Current Pinecone indexes: {indexes}')

    # Create index and add embeddings if it doesn't exist yet,
    # and save a Pdf instance in the database.
    if index_name not in indexes:
        logger.info(f'Index not found, creating new Pinecone index: {index_name}')
        pinecone.create_index(name=index_name, dimension=dimension, pods=0)

        logger.info('Start adding embeddings to Pinecone...')
        Pinecone.from_texts(docs, embeddings, index_name=index_name, namespace=namespace)

        index = pinecone.Index(index_name)
        total_uploaded = int(index.describe_index_stats()['total_vector_count'])
        logger.info(f'Done! Added {total_uploaded} embeddings ({len(docs)} documents) to Pinecone index "{index_name}"')

        return save_pdf_instance(
            id=index_name,
            index_name=index_name,
            filename=index_name,
            namespace=namespace,
            vector_count=total_uploaded
        )
    # Otherwise just return the existing Pdf instance.
    else:
        logger.info(f'Index found, using existing Pinecone index: {index_name}')
        return get_pdf_instance_by('index_name', index_name)
