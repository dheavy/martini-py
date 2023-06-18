from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver


class DocumentCollection(models.Model):
    '''
    DocumentCollection regroups UnstructuredDocuments.
    In other words, a DocumentCollection is a group of documents that are related,
    and that can be searched together.
    DocumentCollection stores its documents in a single Qdrant collection.
    '''
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'DocumentCollection (name="{self.name}")'


class UnstructuredDocument(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='static/uploads/')
    task_id = models.CharField(max_length=255, blank=True, null=True)
    collection = models.ForeignKey(
        DocumentCollection,
        related_name='documents',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'UnstructuredDocument (name="{self.name}")'


# Delete file associated with model instance when it is deleted.
@receiver(post_delete, sender=UnstructuredDocument)
def file_delete(sender, instance: UnstructuredDocument, **kwargs):
    instance.file.delete(False)

    # llm = OpenAI(temperature=0, openai_api_key=os.environ.get('OPENAI_API_KEY'))
    # chain = load_qa_chain(llm, chain_type="stuff")
    # query = "What is the O'Reilly logo is a registered trademark of?"
    # docs = docsearch.similarity_search(query)
    # print(chain.run(input_documents=docs, question=query))
