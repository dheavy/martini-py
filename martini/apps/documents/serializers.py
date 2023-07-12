from rest_framework import serializers

from .models import UnstructuredDocument, DocumentCollection


class UnstructuredDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnstructuredDocument
        fields = ['id', 'name', 'description', 'file', 'task_id', 'collection']
        extra_kwargs = {
            'collection': {'required': False}
        }

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['task_id'] = instance.task_id
        return rep



class DocumentCollectionSerializer(serializers.ModelSerializer):
    documents=UnstructuredDocumentSerializer(many=True, required=False)
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = DocumentCollection
        fields = ['id', 'name', 'slug', 'description', 'documents']
