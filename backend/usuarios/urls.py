from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .user_views import PerfilViewSet, UsuarioViewSet
from .views import LoginView

router = DefaultRouter()
router.register('api/usuarios', UsuarioViewSet, basename='usuario')
router.register('api/perfis', PerfilViewSet, basename='perfil')

urlpatterns = [
    path('api/auth/login/', LoginView.as_view(), name='auth-login'),
    path('', include(router.urls)),
]
