from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UnstructuredDocumentViewSet, DocumentCollectionViewSet

router = DefaultRouter()
router.register(r'documents', UnstructuredDocumentViewSet)
router.register(r'collections', DocumentCollectionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
