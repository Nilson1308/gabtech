from django.urls import path

from plataforma.views import CadastroGabineteCreateView, CadastroGabineteStatusView

urlpatterns = [
    path(
        'cadastro-gabinete/',
        CadastroGabineteCreateView.as_view(),
        name='platform-cadastro-gabinete',
    ),
    path(
        'cadastro-gabinete/<uuid:cadastro_id>/',
        CadastroGabineteStatusView.as_view(),
        name='platform-cadastro-gabinete-status',
    ),
]
