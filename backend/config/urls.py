"""
URLs dos schemas de tenant (gabinetes).
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health(_request):
    return JsonResponse({'status': 'ok'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health, name='health-tenant'),
    path('', include('usuarios.urls')),
    path('api/crm/', include('crm.urls')),
    path('api/atendimentos/', include('atendimentos.urls')),
    path('api/agenda/', include('agenda.urls')),
    path('api/documentos/', include('documentos.urls')),
    path('api/cerimonial/', include('cerimonial.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/servicos/', include('servicos.urls')),
    path('api/auditoria/', include('auditoria.urls')),
    path('api/platform/', include('plataforma.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
