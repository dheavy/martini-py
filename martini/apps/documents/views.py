from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from celery.result import AsyncResult
from celery.result import AsyncResult

from .models import UnstructuredDocument, DocumentCollection
from .tasks import store_embeddings
from .serializers import (
    UnstructuredDocumentSerializer,
    DocumentCollectionSerializer
)


class UnstructuredDocumentViewSet(viewsets.ModelViewSet):
    queryset = UnstructuredDocument.objects.all()
    serializer_class = UnstructuredDocumentSerializer

    def perform_create(self, serializer):
        '''
        Overrides the default create method of the ModelSerializer.
        Saves the UnstructuredDocument object, then submit a task to process the UnstructuredDocument.
        Updates and saves the object with task ID for status checking.
        '''
        udoc = serializer.save()

        # Submit a task to process the UnstructuredDocument.
        task = store_embeddings.delay(udoc.file.path)
        udoc.task_id = task.id

        # Bind to the default DocumentCollection before saving.
        udoc.collection = DocumentCollection.objects.get(name='default')

        udoc.save()

    def update(self, request, *args, **kwargs):
        if 'file' in request.data:
            return Response({"detail": "File cannot be updated."}, status=status.HTTP_400_BAD_REQUEST)

        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['get'], url_path='status')
    def get_task_status(self, request, pk=None):
        '''
        Generate a /api/documents/{pk}/status endpoint to check
        the status of a related Celery task (e.g. processing embeddings).
        '''
        instance = self.get_object()
        task_id = instance.task_id
        task = AsyncResult(task_id)
        return Response({ 'status': task.status }, status=status.HTTP_200_OK)


class DocumentCollectionViewSet(viewsets.ModelViewSet):
    queryset = DocumentCollection.objects.all()
    serializer_class = DocumentCollectionSerializer
