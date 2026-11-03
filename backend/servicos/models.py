from django.conf import settings
from django.db import models

from crm.models import Cidadao, Tag


class EixoServico(models.Model):
    nome = models.CharField('nome', max_length=120)
    icone = models.CharField('ícone', max_length=50, default='briefcase')
    cor = models.CharField('cor', max_length=7, default='#6366f1')
    ativo = models.BooleanField('ativo', default=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'eixo de serviço'
        verbose_name_plural = 'eixos de serviço'
        ordering = ('nome',)

    def __str__(self) -> str:
        return self.nome


class VagaEmprego(models.Model):
    class Status(models.TextChoices):
        ABERTA = 'aberta', 'Aberta'
        PAUSADA = 'pausada', 'Pausada'
        PREENCHIDA = 'preenchida', 'Preenchida'

    eixo = models.ForeignKey(
        EixoServico,
        on_delete=models.PROTECT,
        related_name='vagas',
        verbose_name='eixo',
    )
    titulo = models.CharField('título', max_length=255)
    empresa_parceira = models.CharField('empresa parceira', max_length=255)
    descricao = models.TextField('descrição', blank=True)
    requisitos = models.TextField('requisitos', blank=True)
    status = models.CharField(
        'status',
        max_length=20,
        choices=Status.choices,
        default=Status.ABERTA,
    )
    tags_alvo = models.ManyToManyField(
        Tag,
        related_name='vagas_talento',
        blank=True,
        verbose_name='tags alvo (matchmaking)',
    )
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'vaga de emprego'
        verbose_name_plural = 'vagas de emprego'
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return self.titulo


class CandidaturaTalento(models.Model):
    class StatusProcesso(models.TextChoices):
        TRIAGEM = 'triagem', 'Triagem'
        ENCAMINHADO = 'encaminhado', 'Encaminhado'
        ENTREVISTA = 'entrevista', 'Entrevista'
        CONTRATADO = 'contratado', 'Contratado'
        RECUSADO = 'recusado', 'Recusado'

    vaga = models.ForeignKey(
        VagaEmprego,
        on_delete=models.CASCADE,
        related_name='candidaturas',
        verbose_name='vaga',
    )
    candidato = models.ForeignKey(
        Cidadao,
        on_delete=models.PROTECT,
        related_name='candidaturas_talento',
        verbose_name='candidato',
    )
    status_processo = models.CharField(
        'status no processo',
        max_length=20,
        choices=StatusProcesso.choices,
        default=StatusProcesso.TRIAGEM,
    )
    observacoes = models.TextField('observações', blank=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'candidatura (banco de talentos)'
        verbose_name_plural = 'candidaturas (banco de talentos)'
        ordering = ('-updated_at',)
        constraints = [
            models.UniqueConstraint(
                fields=('vaga', 'candidato'),
                name='servicos_candidatura_vaga_candidato_uniq',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.candidato.nome} → {self.vaga.titulo}'


class ItemBeneficio(models.Model):
    nome = models.CharField('nome', max_length=200)
    descricao = models.TextField('descrição', blank=True)
    exige_laudo = models.BooleanField('exige laudo médico', default=False)
    tags_alvo = models.ManyToManyField(
        Tag,
        related_name='itens_beneficio',
        blank=True,
        verbose_name='tags alvo',
    )
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'item de benefício'
        verbose_name_plural = 'itens de benefício'
        ordering = ('nome',)

    def __str__(self) -> str:
        return self.nome


class EntregaBeneficio(models.Model):
    cidadao = models.ForeignKey(
        Cidadao,
        on_delete=models.PROTECT,
        related_name='entregas_beneficio',
        verbose_name='cidadão',
    )
    item = models.ForeignKey(
        ItemBeneficio,
        on_delete=models.PROTECT,
        related_name='entregas',
        verbose_name='item',
    )
    data_entrega = models.DateField('data da entrega')
    quantidade = models.PositiveIntegerField('quantidade', default=1)
    entregue_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='entregas_beneficio_registradas',
        verbose_name='entregue por',
    )
    created_at = models.DateTimeField('registrado em', auto_now_add=True)

    class Meta:
        verbose_name = 'entrega de benefício'
        verbose_name_plural = 'entregas de benefício'
        ordering = ('-data_entrega', '-id')

    def __str__(self) -> str:
        return f'{self.item.nome} → {self.cidadao.nome}'


class AgendamentoAssessoria(models.Model):
    class Status(models.TextChoices):
        AGENDADO = 'agendado', 'Agendado'
        REALIZADO = 'realizado', 'Realizado'
        CANCELADO = 'cancelado', 'Cancelado'

    cidadao = models.ForeignKey(
        Cidadao,
        on_delete=models.PROTECT,
        related_name='agendamentos_assessoria',
        verbose_name='cidadão',
    )
    tipo_nome = models.CharField('tipo de assessoria', max_length=200)
    tipo_descricao = models.TextField('descrição do tipo', blank=True)
    data_agendamento = models.DateTimeField('data/hora do agendamento')
    status = models.CharField(
        'status',
        max_length=20,
        choices=Status.choices,
        default=Status.AGENDADO,
    )
    especialista_responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assessorias_conduzidas',
        verbose_name='especialista responsável',
    )
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'agendamento de assessoria'
        verbose_name_plural = 'agendamentos de assessoria'
        ordering = ('-data_agendamento',)

    def __str__(self) -> str:
        return f'{self.tipo_nome} — {self.cidadao.nome}'


class TurmaCurso(models.Model):
    class Status(models.TextChoices):
        ABERTA = 'aberta', 'Aberta'
        EM_ANDAMENTO = 'em_andamento', 'Em andamento'
        ENCERRADA = 'encerrada', 'Encerrada'

    nome_curso = models.CharField('nome do curso', max_length=255)
    vagas_totais = models.PositiveIntegerField('vagas totais', default=20)
    status = models.CharField(
        'status',
        max_length=20,
        choices=Status.choices,
        default=Status.ABERTA,
    )
    tags_alvo = models.ManyToManyField(
        Tag,
        related_name='turmas_curso',
        blank=True,
        verbose_name='tags alvo',
    )
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'turma de curso'
        verbose_name_plural = 'turmas de curso'
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return self.nome_curso

    @property
    def vagas_ocupadas(self) -> int:
        return self.inscricoes.filter(status='inscrito').count()


class InscricaoCurso(models.Model):
    class Status(models.TextChoices):
        INSCRITO = 'inscrito', 'Inscrito'
        LISTA_ESPERA = 'lista_espera', 'Lista de espera'
        CANCELADO = 'cancelado', 'Cancelado'

    turma = models.ForeignKey(
        TurmaCurso,
        on_delete=models.CASCADE,
        related_name='inscricoes',
        verbose_name='turma',
    )
    cidadao = models.ForeignKey(
        Cidadao,
        on_delete=models.PROTECT,
        related_name='inscricoes_curso',
        verbose_name='cidadão',
    )
    status = models.CharField(
        'status',
        max_length=20,
        choices=Status.choices,
        default=Status.INSCRITO,
    )
    created_at = models.DateTimeField('inscrito em', auto_now_add=True)

    class Meta:
        verbose_name = 'inscrição em curso'
        verbose_name_plural = 'inscrições em curso'
        ordering = ('-created_at',)
        constraints = [
            models.UniqueConstraint(
                fields=('turma', 'cidadao'),
                name='servicos_inscricao_turma_cidadao_uniq',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.cidadao.nome} @ {self.turma.nome_curso}'
