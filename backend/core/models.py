from django.db import models
from django_tenants.models import DomainMixin, TenantMixin


class Gabinete(TenantMixin):
    """
    Tenant: cada registro gera um schema PostgreSQL isolado (schema_name).
    """

    nome = models.CharField('nome do gabinete', max_length=200)
    logo = models.TextField(
        'logo ou brasão',
        blank=True,
        help_text='Imagem em data URL (PNG/JPEG) exibida na identidade do gabinete.',
    )
    logo_formato = models.CharField(
        'formato do logo',
        max_length=5,
        blank=True,
        default='1:1',
        help_text='Proporção da identidade visual: 1:1, 1:3 ou 3:1.',
    )
    created_on = models.DateField('criado em', auto_now_add=True)

    auto_create_schema = True
    auto_drop_schema = False

    class Meta:
        verbose_name = 'gabinete'
        verbose_name_plural = 'gabinetes'

    def __str__(self) -> str:
        return f'{self.nome} ({self.schema_name})'


class Dominio(DomainMixin):
    """Mapeia host HTTP → gabinete (tenant)."""

    class Meta:
        verbose_name = 'domínio'
        verbose_name_plural = 'domínios'

    def __str__(self) -> str:
        return self.domain
