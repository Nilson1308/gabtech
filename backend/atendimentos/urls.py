from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AnexoViewSet,
    AtendimentoViewSet,
    ConfiguracaoSlaView,
    DespachoViewSet,
    MacrotemaViewSet,
    ResponsaveisAtendimentoView,
)

router = DefaultRouter()
router.register('macrotemas', MacrotemaViewSet, basename='macrotema')
router.register('atendimentos', AtendimentoViewSet, basename='atendimento')
router.register('despachos', DespachoViewSet, basename='despacho')
router.register('anexos', AnexoViewSet, basename='anexo-atendimento')

urlpatterns = [
    path('configuracao-sla/', ConfiguracaoSlaView.as_view(), name='configuracao-sla'),
    path('responsaveis/', ResponsaveisAtendimentoView.as_view(), name='atendimentos-responsaveis'),
    *router.urls,
]
