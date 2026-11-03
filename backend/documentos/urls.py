from django.urls import path
from rest_framework.routers import DefaultRouter

from .assinatura_views import MinhaAssinaturaVisualView
from .views import (
    DocumentoViewSet,
    EtiquetaDocumentoViewSet,
    PastaDocumentoViewSet,
    TemplateDocumentoViewSet,
    TipoDocumentoViewSet,
    VersaoDocumentoViewSet,
)

router = DefaultRouter()
router.register('etiquetas', EtiquetaDocumentoViewSet, basename='etiqueta-documento')
router.register('tipos', TipoDocumentoViewSet, basename='tipo-documento')
router.register('templates', TemplateDocumentoViewSet, basename='template-documento')
router.register('pastas', PastaDocumentoViewSet, basename='pasta-documento')
router.register('documentos', DocumentoViewSet, basename='documento')
router.register('versoes', VersaoDocumentoViewSet, basename='versao-documento')

urlpatterns = [
    path('minha-assinatura/', MinhaAssinaturaVisualView.as_view(), name='minha-assinatura'),
    *router.urls,
]
