from django.conf import settings
from django.db import models

from agenda.models import Evento
from crm.models import Cidadao, PerfilProfissional

from .credenciamento_config import default_credenciamento_config


class EventoCerimonial(models.Model):
    class StatusLogistico(models.TextChoices):
        PLANEJAMENTO = 'planejamento', 'Planejamento'
        EXECUTANDO = 'executando', 'Executando'
        CONCLUIDO = 'concluido', 'Concluído'
        CANCELADO = 'cancelado', 'Cancelado'

    evento_agenda = models.OneToOneField(
        Evento,
        on_delete=models.CASCADE,
        related_name='cerimonial',
        verbose_name='evento na agenda',
    )
    status_logistico = models.CharField(
        'status logístico',
        max_length=20,
        choices=StatusLogistico.choices,
        default=StatusLogistico.PLANEJAMENTO,
    )
    token_logistica = models.UUIDField(
        'token logística pública',
        null=True,
        blank=True,
        unique=True,
        editable=False,
    )
    logistica_publica_ativa = models.BooleanField(
        'link público de logística ativo',
        default=False,
    )
    observacao_logistica_externa = models.TextField(
        'última observação do colaborador externo',
        blank=True,
    )
    credenciamento_config = models.JSONField(
        'parâmetros do credenciamento público',
        default=default_credenciamento_config,
        blank=True,
    )
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'evento cerimonial'
        verbose_name_plural = 'eventos cerimoniais'
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return self.evento_agenda.titulo


class ItemChecklistPadrao(models.Model):
    class Categoria(models.TextChoices):
        INFRAESTRUTURA = 'infraestrutura', 'Infraestrutura'
        BUFFET = 'buffet', 'Buffet'
        CERIMONIAL = 'cerimonial', 'Cerimonial'
        COMUNICACAO = 'comunicacao', 'Comunicação'
        SEGURANCA = 'seguranca', 'Segurança'
        TECNOLOGIA = 'tecnologia', 'Tecnologia'

    categoria = models.CharField('categoria', max_length=32, choices=Categoria.choices)
    descricao = models.CharField('descrição', max_length=255)
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'item padrão de checklist'
        verbose_name_plural = 'itens padrão de checklist'
        ordering = ('categoria', 'descricao')

    def __str__(self) -> str:
        return self.descricao


class ItemChecklist(models.Model):
    class Categoria(models.TextChoices):
        INFRAESTRUTURA = 'infraestrutura', 'Infraestrutura'
        BUFFET = 'buffet', 'Buffet'
        CERIMONIAL = 'cerimonial', 'Cerimonial'
        COMUNICACAO = 'comunicacao', 'Comunicação'
        SEGURANCA = 'seguranca', 'Segurança'
        TECNOLOGIA = 'tecnologia', 'Tecnologia'

    class Status(models.TextChoices):
        PENDENTE = 'pendente', 'Pendente'
        PROVIDENCIADO = 'providenciado', 'Providenciado'
        CANCELADO = 'cancelado', 'Cancelado'

    evento = models.ForeignKey(
        EventoCerimonial,
        on_delete=models.CASCADE,
        related_name='checklist',
        verbose_name='evento',
    )
    categoria = models.CharField('categoria', max_length=32, choices=Categoria.choices)
    descricao = models.CharField('descrição', max_length=255)
    status = models.CharField(
        'status',
        max_length=20,
        choices=Status.choices,
        default=Status.PENDENTE,
    )
    responsavel = models.CharField('responsável', max_length=200, blank=True)
    prazo = models.DateField('prazo', null=True, blank=True)
    observacoes = models.TextField('observações', blank=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'item de checklist'
        verbose_name_plural = 'itens de checklist'
        ordering = ('categoria', 'id')

    def __str__(self) -> str:
        return self.descricao


class ConvidadoEvento(models.Model):
    class StatusConfirmacao(models.TextChoices):
        PENDENTE = 'pendente', 'Pendente'
        CONFIRMADO = 'confirmado', 'Confirmado'
        RECUSADO = 'recusado', 'Recusado'

    evento = models.ForeignKey(
        EventoCerimonial,
        on_delete=models.CASCADE,
        related_name='convidados',
        verbose_name='evento',
    )
    cidadao = models.ForeignKey(
        Cidadao,
        on_delete=models.CASCADE,
        related_name='convites_cerimonial',
        verbose_name='cidadão',
    )
    perfil_ativo = models.ForeignKey(
        PerfilProfissional,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='convites_evento',
        verbose_name='perfil ativo no evento',
    )
    status_confirmacao = models.CharField(
        'confirmação',
        max_length=20,
        choices=StatusConfirmacao.choices,
        default=StatusConfirmacao.PENDENTE,
    )
    ordem_precedencia = models.PositiveIntegerField('ordem de precedência', default=1)
    is_vip = models.BooleanField('VIP', default=False)
    observacoes = models.TextField('observações', blank=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'convidado do evento'
        verbose_name_plural = 'convidados do evento'
        ordering = ('ordem_precedencia', 'id')
        constraints = [
            models.UniqueConstraint(
                fields=('evento', 'cidadao'),
                name='cerimonial_convidado_unico_por_evento',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.cidadao.nome} — {self.evento}'


class Credenciado(models.Model):
    class StatusPresenca(models.TextChoices):
        PENDENTE = 'pendente', 'Pendente'
        PRESENTE = 'presente', 'Presente'

    evento = models.ForeignKey(
        EventoCerimonial,
        on_delete=models.CASCADE,
        related_name='credenciados',
        verbose_name='evento',
    )
    nome = models.CharField('nome', max_length=200)
    cpf = models.CharField('CPF', max_length=14, blank=True, default='')
    telefone = models.CharField('telefone', max_length=20)
    email = models.EmailField('e-mail', blank=True, default='')
    data_nascimento = models.DateField('data de nascimento', null=True, blank=True)
    orgao_instituicao = models.CharField('órgão / instituição', max_length=200, blank=True, default='')
    aceitou_lgpd = models.BooleanField('aceitou LGPD', default=False)
    data_registro = models.DateTimeField('data de registro', auto_now_add=True)
    status_presenca = models.CharField(
        'presença',
        max_length=20,
        choices=StatusPresenca.choices,
        default=StatusPresenca.PENDENTE,
    )

    class Meta:
        verbose_name = 'credenciado'
        verbose_name_plural = 'credenciados'
        ordering = ('-data_registro',)
        constraints = [
            models.UniqueConstraint(
                fields=('evento', 'telefone'),
                name='cerimonial_telefone_unico_por_evento',
            ),
        ]

    def __str__(self) -> str:
        return self.nome


class ComunicacaoDisparo(models.Model):
    class Canal(models.TextChoices):
        EMAIL = 'email', 'E-mail'
        WHATSAPP = 'whatsapp', 'WhatsApp'
        SMS = 'sms', 'SMS'

    class Status(models.TextChoices):
        PROCESSANDO = 'processando', 'Processando'
        ENVIADO = 'enviado', 'Enviado'
        FALHA = 'falha', 'Falha'

    evento = models.ForeignKey(
        EventoCerimonial,
        on_delete=models.CASCADE,
        related_name='comunicacoes',
        verbose_name='evento',
    )
    canal = models.CharField('canal', max_length=20, choices=Canal.choices)
    mensagem = models.TextField('mensagem')
    publico_alvo = models.JSONField('público-alvo', default=dict, blank=True)
    quantidade_envios = models.PositiveIntegerField('quantidade de envios', default=0)
    status = models.CharField(
        'status',
        max_length=20,
        choices=Status.choices,
        default=Status.PROCESSANDO,
    )
    data_hora = models.DateTimeField('data/hora', auto_now_add=True)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='disparos_cerimonial',
        verbose_name='criado por',
    )

    class Meta:
        verbose_name = 'disparo de comunicação'
        verbose_name_plural = 'disparos de comunicação'
        ordering = ('-data_hora',)

    def __str__(self) -> str:
        return f'{self.get_canal_display()} — {self.evento}'
