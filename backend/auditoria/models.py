from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class EventoAuditoria(models.Model):
    """Registro append-only de create/update/delete via API (por tenant)."""

    class Acao(models.TextChoices):
        CRIAR = 'criar', 'Criação'
        ALTERAR = 'alterar', 'Alteração'
        EXCLUIR = 'excluir', 'Exclusão'

    acao = models.CharField('ação', max_length=12, choices=Acao.choices)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name='tipo de registro',
    )
    object_id = models.CharField('ID do registro', max_length=64)
    content_object = GenericForeignKey('content_type', 'object_id')
    object_repr = models.CharField('descrição', max_length=255, blank=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eventos_auditoria',
        verbose_name='usuário',
    )
    ocorrido_em = models.DateTimeField('ocorrido em', auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'evento de auditoria'
        verbose_name_plural = 'eventos de auditoria'
        ordering = ('-ocorrido_em',)
        indexes = [
            models.Index(fields=['content_type', 'object_id', '-ocorrido_em']),
        ]

    def __str__(self) -> str:
        return f'{self.get_acao_display()} · {self.object_repr or self.object_id}'
