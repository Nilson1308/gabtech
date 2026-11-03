import os
import uuid

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

from crm.models import Cidadao, PerfilProfissional, Tag

from .sla import calcular_sla_vencimento


def anexo_atendimento_upload_to(instance, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    safe_name = f'{uuid.uuid4().hex}{ext}'
    return f'atendimentos/{instance.atendimento_id}/{safe_name}'


class Macrotema(models.Model):
    nome = models.CharField('nome', max_length=120)
    cor = models.CharField('cor', max_length=7, default='#3b82f6')
    icone = models.CharField('ícone', max_length=50, default='folder-tree')

    class Meta:
        verbose_name = 'macrotema'
        verbose_name_plural = 'macrotemas'
        ordering = ('nome',)

    def __str__(self) -> str:
        return self.nome


class Atendimento(models.Model):
    class Status(models.TextChoices):
        ABERTO = 'aberto', 'Aberto'
        EM_ANDAMENTO = 'em_andamento', 'Em andamento'
        AGUARDANDO_TERCEIROS = 'aguardando_terceiros', 'Aguardando terceiros'
        CONCLUIDO = 'concluido', 'Concluído'

    class Prioridade(models.TextChoices):
        BAIXA = 'baixa', 'Baixa'
        MEDIA = 'media', 'Média'
        ALTA = 'alta', 'Alta'
        URGENTE = 'urgente', 'Urgente'

    protocolo = models.CharField('protocolo', max_length=20, unique=True, editable=False)
    cidadao = models.ForeignKey(
        Cidadao,
        on_delete=models.PROTECT,
        related_name='atendimentos',
        verbose_name='cidadão',
    )
    perfil_ativo = models.ForeignKey(
        PerfilProfissional,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='atendimentos',
        verbose_name='perfil ativo',
    )
    assunto = models.CharField('assunto', max_length=255)
    descricao = models.TextField('descrição')
    macrotema = models.ForeignKey(
        Macrotema,
        on_delete=models.PROTECT,
        related_name='atendimentos',
        verbose_name='macrotema',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='atendimentos',
        blank=True,
        verbose_name='tags do atendimento',
    )
    status = models.CharField(
        'status',
        max_length=30,
        choices=Status.choices,
        default=Status.ABERTO,
    )
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='atendimentos_responsavel',
        verbose_name='responsável',
    )
    prioridade = models.CharField(
        'prioridade',
        max_length=10,
        choices=Prioridade.choices,
        default=Prioridade.MEDIA,
    )
    sla_vencimento = models.DateTimeField('SLA vencimento', null=True, blank=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'atendimento'
        verbose_name_plural = 'atendimentos'
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return f'{self.protocolo} — {self.assunto}'

    @classmethod
    def gerar_protocolo(cls) -> str:
        hoje = timezone.localdate().strftime('%Y%m%d')
        prefixo = f'{hoje}-'
        with transaction.atomic():
            ultimo = (
                cls.objects.select_for_update()
                .filter(protocolo__startswith=prefixo)
                .order_by('-protocolo')
                .first()
            )
            if ultimo:
                seq = int(ultimo.protocolo.split('-')[-1]) + 1
            else:
                seq = 1
            return f'{prefixo}{seq:04d}'

    def save(self, *args, **kwargs):
        if not self.protocolo:
            self.protocolo = self.gerar_protocolo()
        if self.status == self.Status.CONCLUIDO:
            self.sla_vencimento = None
        elif not self.sla_vencimento:
            self.sla_vencimento = calcular_sla_vencimento(self.prioridade)
        super().save(*args, **kwargs)

    def recalcular_sla(self, *, base=None):
        if self.status == self.Status.CONCLUIDO:
            self.sla_vencimento = None
        else:
            ref = base or self.created_at or timezone.now()
            self.sla_vencimento = calcular_sla_vencimento(self.prioridade, base=ref)


class Despacho(models.Model):
    class Tipo(models.TextChoices):
        NOTA_INTERNA = 'nota_interna', 'Nota interna'
        NOTA_PUBLICA = 'nota_publica', 'Nota pública'
        MUDANCA_STATUS = 'mudanca_status', 'Mudança de status'
        REATRIBUICAO = 'reatribuicao', 'Reatribuição'

    atendimento = models.ForeignKey(
        Atendimento,
        on_delete=models.CASCADE,
        related_name='despachos',
        verbose_name='atendimento',
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='despachos_atendimento',
        verbose_name='autor',
    )
    tipo = models.CharField('tipo', max_length=20, choices=Tipo.choices)
    conteudo = models.TextField('conteúdo')
    status_anterior = models.CharField('status anterior', max_length=30, blank=True)
    status_novo = models.CharField('status novo', max_length=30, blank=True)
    responsavel_anterior = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='despachos_responsavel_anterior',
        verbose_name='responsável anterior',
    )
    responsavel_novo = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='despachos_responsavel_novo',
        verbose_name='responsável novo',
    )
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'despacho'
        verbose_name_plural = 'despachos'
        ordering = ('created_at',)

    def __str__(self) -> str:
        return f'{self.get_tipo_display()} — {self.atendimento.protocolo}'


class Anexo(models.Model):
    atendimento = models.ForeignKey(
        Atendimento,
        on_delete=models.CASCADE,
        related_name='anexos',
        verbose_name='atendimento',
    )
    despacho = models.ForeignKey(
        Despacho,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='anexos',
        verbose_name='despacho',
    )
    arquivo = models.FileField('arquivo', upload_to=anexo_atendimento_upload_to)
    nome_original = models.CharField('nome original', max_length=255)
    content_type = models.CharField('tipo MIME', max_length=120, blank=True)
    tamanho = models.PositiveIntegerField('tamanho (bytes)')
    enviado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='anexos_atendimento_enviados',
        verbose_name='enviado por',
    )
    created_at = models.DateTimeField('enviado em', auto_now_add=True)

    class Meta:
        verbose_name = 'anexo'
        verbose_name_plural = 'anexos'
        ordering = ('created_at',)

    def __str__(self) -> str:
        return self.nome_original


class ConfiguracaoSla(models.Model):
    """Uma linha por tenant (pk fixo = 1). Prazos em horas corridas após abertura."""

    horas_baixa = models.PositiveIntegerField('horas — prioridade baixa', default=120)
    horas_media = models.PositiveIntegerField('horas — prioridade média', default=72)
    horas_alta = models.PositiveIntegerField('horas — prioridade alta', default=48)
    horas_urgente = models.PositiveIntegerField('horas — prioridade urgente', default=24)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'configuração de SLA'
        verbose_name_plural = 'configuração de SLA'

    def __str__(self) -> str:
        return 'Prazos de SLA dos atendimentos'

    @classmethod
    def get(cls) -> 'ConfiguracaoSla':
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def horas_para_prioridade(self, prioridade: str) -> int:
        mapping = {
            Atendimento.Prioridade.BAIXA: self.horas_baixa,
            Atendimento.Prioridade.MEDIA: self.horas_media,
            Atendimento.Prioridade.ALTA: self.horas_alta,
            Atendimento.Prioridade.URGENTE: self.horas_urgente,
        }
        return mapping.get(prioridade, self.horas_media)
