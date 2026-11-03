from django.urls import path

from .views import HistoricoAuditoriaView

urlpatterns = [
    path('historico/', HistoricoAuditoriaView.as_view(), name='auditoria-historico'),
]
