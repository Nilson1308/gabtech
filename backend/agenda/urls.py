from rest_framework.routers import DefaultRouter

from .views import EspacoViewSet, EventoViewSet, TipoEventoViewSet

router = DefaultRouter()
router.register('tipos-evento', TipoEventoViewSet, basename='tipo-evento')
router.register('espacos', EspacoViewSet, basename='espaco')
router.register('eventos', EventoViewSet, basename='evento')

urlpatterns = router.urls
