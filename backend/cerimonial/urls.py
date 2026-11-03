from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .public_views import LogisticaPublicaEnviarView, LogisticaPublicaView
from .views import (
    ComunicacaoDisparoViewSet,
    ConvidadoEventoViewSet,
    CredenciadoViewSet,
    EventoCerimonialViewSet,
    ItemChecklistPadraoViewSet,
    ItemChecklistViewSet,
)

router = DefaultRouter()
router.register('eventos', EventoCerimonialViewSet, basename='cerimonial-evento')
router.register('checklist-itens', ItemChecklistViewSet, basename='cerimonial-checklist')
router.register('checklist-padrao', ItemChecklistPadraoViewSet, basename='cerimonial-checklist-padrao')
router.register('convidados', ConvidadoEventoViewSet, basename='cerimonial-convidado')
router.register('credenciados', CredenciadoViewSet, basename='cerimonial-credenciado')
router.register('comunicacoes', ComunicacaoDisparoViewSet, basename='cerimonial-comunicacao')

urlpatterns = [
    path(
        'logistica-publica/<uuid:token>/',
        LogisticaPublicaView.as_view(),
        name='cerimonial-logistica-publica',
    ),
    path(
        'logistica-publica/<uuid:token>/enviar/',
        LogisticaPublicaEnviarView.as_view(),
        name='cerimonial-logistica-publica-enviar',
    ),
    path('', include(router.urls)),
]
