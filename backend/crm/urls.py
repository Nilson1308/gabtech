from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CidadaoViewSet, DocumentoAnexoViewSet, GeocodeEnderecoView, TagViewSet

router = DefaultRouter()
router.register('cidadaos', CidadaoViewSet, basename='cidadao')
router.register('documentos', DocumentoAnexoViewSet, basename='documento-anexo')
router.register('tags', TagViewSet, basename='tag')

urlpatterns = [
    path('geocode/', GeocodeEnderecoView.as_view(), name='crm-geocode'),
    *router.urls,
]
