from django.urls import path

from .views import (
    AssessorDesempenhoExportView,
    AssessorDesempenhoView,
    EquipeDesempenhoExportView,
    EquipeDesempenhoView,
    ExecutivoAnalyticsView,
    TerritorialAnalyticsView,
    TerritorialFiltrosView,
    TerritorialPinsView,
    TerritorialZonasView,
)

urlpatterns = [
    path('executivo/', ExecutivoAnalyticsView.as_view(), name='analytics-executivo'),
    path('equipe-desempenho/', EquipeDesempenhoView.as_view(), name='analytics-equipe-desempenho'),
    path(
        'equipe-desempenho/export/',
        EquipeDesempenhoExportView.as_view(),
        name='analytics-equipe-desempenho-export',
    ),
    path(
        'assessor-desempenho/',
        AssessorDesempenhoView.as_view(),
        name='analytics-assessor-desempenho',
    ),
    path(
        'assessor-desempenho/export/',
        AssessorDesempenhoExportView.as_view(),
        name='analytics-assessor-desempenho-export',
    ),
    path('territorial/filtros/', TerritorialFiltrosView.as_view(), name='analytics-territorial-filtros'),
    path('territorial/zonas/', TerritorialZonasView.as_view(), name='analytics-territorial-zonas'),
    path('territorial/pins/', TerritorialPinsView.as_view(), name='analytics-territorial-pins'),
    path('territorial/', TerritorialAnalyticsView.as_view(), name='analytics-territorial'),
]
