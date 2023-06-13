import datetime
import os
from typing import Optional

import pinecone
from celery.utils.log import get_task_logger
from sqlalchemy import Column, Integer, String, DateTime

from martini.database import Base, SessionLocal



class Pdf(Base):
    __tablename__ = 'pdfs'

    id = Column(String(128), primary_key=True, index=True, nullable=False)
    index_name = Column(String(50), unique=True, index=True, nullable=False)
    filename = Column(String(250), nullable=False)
    namespace = Column(String(200))
    vector_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<Pdf(id={%s}, index_name={%s}, filename={%s}, namespace={%s}, vector_count={%s})>' % (
            self.id,
            self.index_name,
            self.filename,
            self.namespace,
            self.vector_count
        )

    def save(self):
        '''
        Save a PDF instance in the SQL database, representing a PDF file
        that has been uploaded and had its content stored in a vector database.
        '''
        session = SessionLocal()
        session.add(self)
        session.commit()
        session.refresh(self)
        session.close()
        return self

    @classmethod
    def get_by(self, key: str, value: str):
        '''
        Class method to retrieve a PDF instance from the SQL database,
        either by id or index_name.

        Example:
        >>> Pdf.get_by('index_name', 'my-pdf-index-name')
        '''
        session = SessionLocal()
        query = session.query(Pdf)

        if key == 'id':
            query = query.filter_by(id=value)
        elif key == 'index_name':
            query = query.filter_by(index_name=value)
        else:
            raise ValueError(f'Pdf.get_by - invalid filter key: {key}')

        instance = query.first()
        session.close()

        if instance is not None:
            return instance
        else:
            raise ValueError(f'Pdf.get_by - no instance found with {key}={value}')



def save_pdf_and_embeddings(
    docs: list[str] = None,
    index_name: str = None,
    dimension: int = 0,
    namespace: Optional[str] = ''
):
    '''
    Store embeddings in Pinecone and save model representing PDF instance in SQL database.
    '''
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

        pdf = Pdf(
            id=index_name,
            index_name=index_name,
            filename=index_name,
            namespace=namespace,
            vector_count=total_uploaded
        )
        return pdf.save()
    # Otherwise just return the existing Pdf instance.
    else:
        logger.info(f'Index found, using existing Pinecone index: {index_name}')
        return Pdf.get_by('index_name', index_name)
