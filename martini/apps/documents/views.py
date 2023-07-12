import os
import time
import uuid

from django.conf import settings
from django.utils.text import slugify

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from celery.result import AsyncResult

from .models import UnstructuredDocument, DocumentCollection
from .tasks import delete_embeddings, save_embeddings
from .serializers import (
    UnstructuredDocumentSerializer,
    DocumentCollectionSerializer
)
from .vectorstore import (
    create_vectorstore_collection,
    delete_vectorstore_collection
)


class UnstructuredDocumentViewSet(viewsets.ModelViewSet):
    queryset = UnstructuredDocument.objects.all()
    serializer_class = UnstructuredDocumentSerializer

    def perform_create(self, serializer):
        '''
        When saving the model, saves the uploaded file to the media directory with a unique name.
        Submits a task to process the UnstructuredDocument if APP_ENV is not local,
        i.e. extract embeddings from the document and store them in Qdrant.
        '''
        udoc = serializer.save()

        # Read the uploaded file binary data.
        file_data = udoc.file.read()

        # Save the binary file data to a new file.
        timestamp = int(time.time())
        unique_id = uuid.uuid4()
        new_file_name = f'{timestamp}_{unique_id}.pdf'
        file_path = default_storage.save(new_file_name, ContentFile(file_data))

        # Construct the full file path with the new name.
        media_root = settings.MEDIA_ROOT if settings.APP_ENV == 'local' else settings.MEDIA_ROOT_DOCKER
        storage_file_path = f'{media_root}/{file_path}'

        # If not specified, assign the document to the default collection.
        if not udoc.collection:
            default_collection = DocumentCollection.objects.get(
                slug=settings.MARTINI_DEFAULT_COLLECTION_NAME
            )
            udoc.collection = default_collection

        # Process the UnstructuredDocument.
        # In local development, this is done directly and synchronously.
        # In production, this is done asynchronously via a Celery task.
        if settings.APP_ENV == 'local':
            UnstructuredDocument.save_embeddings(
                storage_file_path,
                udoc.collection.slug,
                udoc.name,
                udoc.id
            )
        else:
            task = save_embeddings.delay(
                storage_file_path,
                udoc.collection.slug,
                udoc.name,
                udoc.id
            )
            # Set the task ID on the model instance for retrieval
            # via the /api/documents/{task_id}/status endpoint.
            udoc.task_id = task.id

        # Delete the initially uploaded file and save the model.
        os.remove(os.path.join(settings.MEDIA_ROOT, udoc.file.name))
        udoc.file.name = settings.UPLOAD_URL + file_path
        udoc.save()

    def perform_destroy(self, instance):
        '''
        Overrides the default destroy method of the ModelSerializer.
        Deletes the associated file from the media directory, and the associated embeddings.
        '''
        instance.file.delete(False)

        if settings.APP_ENV == 'local':
            UnstructuredDocument.delete_embeddings(
                instance.collection.slug,
                instance.name,
                instance.id
            )
        else:
            delete_embeddings.delay(
                instance.collection.slug,
                instance.name,
                instance.id
            )

        return super().perform_destroy(instance)

    def update(self, request, *args, **kwargs):
        '''
        Ensure that the file cannot be updated in a model.
        '''
        if 'file' in request.data:
            return Response({
                'detail': 'File cannot be updated.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['get'], url_path='status')
    def get_task_status(self, request, pk=None):
        '''
        Generate a /api/documents/{id}/status endpoint to query the status of a Document's current processing task.
        Because upload is synchronous but processing embeddings is not, this endpoint is necessary to check the status
        of the processing task from a frontend client.
        '''
        instance = self.get_object()
        task_id = instance.task_id

        if not task_id:
            return Response(
                {'status': 'No task or task ID found'},
                status=status.HTTP_404_NOT_FOUND
            )

        task = AsyncResult(task_id)
        if not task:
            return Response(
                {'status': 'No task or task ID found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if task.status == 'PENDING':
            # Job has not started yet
            response = {
                'status': task.status,
                'details': 'Task has not started yet'
            }
        else:
            response = {
                'status': task.status,
                'details': task.info.get('details', '')
            }

        return Response(response, status=status.HTTP_200_OK)


class DocumentCollectionViewSet(viewsets.ModelViewSet):
    # Prefetch related documents to avoid N+1 queries in nested serializers.
    queryset = DocumentCollection.objects.all().prefetch_related('documents')
    serializer_class = DocumentCollectionSerializer

    def perform_create(self, serializer):
        '''
        Create slug and save it as part of the instance.
        Create a Qdrant collection for the DocumentCollection.
        '''
        name = serializer.validated_data['name']
        slug = slugify(name)
        try:
            create_vectorstore_collection(slug)
            serializer.save(slug=slug)
        except Exception as e:
            raise e

    def perform_destroy(self, instance):
        try:
            delete_vectorstore_collection(instance.slug)
            return super().perform_destroy(instance)
        except Exception as e:
            raise e

