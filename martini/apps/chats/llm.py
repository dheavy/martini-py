import os

from django.conf import settings

from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.embeddings import OpenAIEmbeddings

from apps.documents.vectorstore import get_vectorstore_for_chains

_llm = OpenAI(temperature=0, openai_api_key=os.environ.get('OPENAI_API_KEY'))

# In OpenAI's embedding model, <|endoftext|> is a special token that indicates the end of a document in OpenAI's embeddings.
# We need to set this as `allowed_special` here for tiktoken to parse it without error.
_embeddings = OpenAIEmbeddings(
    openai_api_key=os.environ.get('OPENAI_API_KEY'),
    allowed_special={'<|endoftext|>'}
)

def get_llm():
    '''
    Return an instance of an LLM. Use OpenAI's by default.
    '''
    return _llm

def get_embeddings_model() -> OpenAIEmbeddings:
    '''
    Return embedding model. Use OpenAI's' by default.
    '''
    return _embeddings
