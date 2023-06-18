from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UnstructuredDocumentViewSet

router = DefaultRouter()
router.register(r'documents', UnstructuredDocumentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
