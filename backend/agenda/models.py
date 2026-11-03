from django.conf import settings
from django.db import models

from crm.models import Cidadao


class TipoEvento(models.Model):
    nome = models.CharField('nome', max_length=120)
    cor = models.CharField('cor', max_length=7, default='#3b82f6')
    icone = models.CharField('ícone', max_length=50, default='calendar')
    descricao = models.TextField('descrição', blank=True)
    ativo = models.BooleanField('ativo', default=True)

    class Meta:
        verbose_name = 'tipo de evento'
        verbose_name_plural = 'tipos de evento'
        ordering = ('nome',)

    def __str__(self) -> str:
        return self.nome


class Espaco(models.Model):
    nome = models.CharField('nome', max_length=120)
    descricao = models.TextField('descrição', blank=True)
    capacidade = models.PositiveIntegerField('capacidade', default=10)
    icone = models.CharField('ícone', max_length=50, default='map-pin')
    cor = models.CharField('cor', max_length=7, default='#3b82f6')
    ativo = models.BooleanField('ativo', default=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'espaço'
        verbose_name_plural = 'espaços'
        ordering = ('nome',)

    def __str__(self) -> str:
        return self.nome


class Evento(models.Model):
    class Status(models.TextChoices):
        AGENDADO = 'agendado', 'Agendado'
        REALIZADO = 'realizado', 'Realizado'
        CANCELADO = 'cancelado', 'Cancelado'

    titulo = models.CharField('título', max_length=255)
    descricao = models.TextField('descrição', blank=True)
    data = models.DateField('data')
    hora_inicio = models.TimeField('hora início')
    hora_fim = models.TimeField('hora fim')
    tipo = models.ForeignKey(
        TipoEvento,
        on_delete=models.PROTECT,
        related_name='eventos',
        verbose_name='tipo',
    )
    espaco = models.ForeignKey(
        Espaco,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eventos',
        verbose_name='espaço',
    )
    convidados = models.ManyToManyField(
        Cidadao,
        related_name='eventos_agenda',
        blank=True,
        verbose_name='convidados',
    )
    is_synced_google = models.BooleanField('sincronizado Google', default=False)
    is_synced_outlook = models.BooleanField('sincronizado Outlook', default=False)
    status = models.CharField(
        'status',
        max_length=20,
        choices=Status.choices,
        default=Status.AGENDADO,
    )
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='eventos_agenda_criados',
        verbose_name='criado por',
    )
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'evento'
        verbose_name_plural = 'eventos'
        ordering = ('data', 'hora_inicio')

    def __str__(self) -> str:
        return f'{self.titulo} ({self.data})'
