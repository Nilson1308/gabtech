"""
URLs do schema public (gestão de tenants / healthcheck).
Sem autenticação de usuários de gabinete — User existe apenas nos schemas de tenant.
"""

from django.http import JsonResponse
from django.urls import include, path

from plataforma.platform_admin import platform_admin_site


def health(_request):
    return JsonResponse({'status': 'ok', 'schema': 'public'})


urlpatterns = [
    path('admin/', platform_admin_site.urls),
    path('health/', health, name='health-public'),
    path('api/platform/', include('plataforma.urls')),
]
