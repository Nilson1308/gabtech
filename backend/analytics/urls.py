from django.urls import path

from .views import ExecutivoAnalyticsView, TerritorialAnalyticsView

urlpatterns = [
    path('executivo/', ExecutivoAnalyticsView.as_view(), name='analytics-executivo'),
    path('territorial/', TerritorialAnalyticsView.as_view(), name='analytics-territorial'),
]
