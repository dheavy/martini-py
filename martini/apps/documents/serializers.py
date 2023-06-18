from rest_framework import serializers

from .models import UnstructuredDocument, DocumentCollection


class UnstructuredDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnstructuredDocument
        fields = ['id', 'name', 'description', 'file', 'task_id']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['task_id'] = instance.task_id
        return rep



class DocumentCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentCollection
        fields = ['id', 'name', 'description', 'documents']
