import os
import uuid

from django.conf import settings
from django.db import models


def documento_cidadao_upload_to(instance, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    safe_name = f'{uuid.uuid4().hex}{ext}'
    return f'crm/cidadaos/{instance.cidadao_id}/{safe_name}'


def default_tag_modulos():
    return ['crm']


class Tag(models.Model):
    class Tipo(models.TextChoices):
        SEGMENTACAO = 'segmentacao', 'Segmentação do cidadão'
        CONTEXTO = 'contexto', 'Contexto institucional'
        CONTEXTO_PROFISSIONAL = 'contexto_profissional', 'Contexto profissional'
        AMBOS = 'ambos', 'Segmentação e contexto'

    nome = models.CharField('nome', max_length=120)
    cor = models.CharField('cor', max_length=7, default='#6b7280')
    tipo = models.CharField(
        'tipo',
        max_length=24,
        choices=Tipo.choices,
        default=Tipo.AMBOS,
    )
    modulos = models.JSONField(
        'módulos',
        default=default_tag_modulos,
        help_text='Onde a tag aparece: crm, atendimentos (ou ambos).',
    )

    class Meta:
        verbose_name = 'tag'
        verbose_name_plural = 'tags'
        ordering = ('nome',)

    def __str__(self) -> str:
        return self.nome


class Cidadao(models.Model):
    nome = models.CharField('nome', max_length=200)
    nome_social = models.CharField('nome social', max_length=200, blank=True)
    cpf = models.CharField('CPF', max_length=14, unique=True, null=True, blank=True)
    telefone = models.CharField('telefone', max_length=20)
    email = models.EmailField('e-mail', blank=True)
    # TextField: aceita URL externa ou data URL (cropper do frontend)
    avatar = models.TextField('avatar', blank=True)
    observacoes = models.TextField('observações', blank=True)
    marcadores = models.ManyToManyField(
        Tag,
        related_name='cidadaos_marcados',
        blank=True,
        verbose_name='marcadores',
    )
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'cidadão'
        verbose_name_plural = 'cidadãos'
        ordering = ('nome',)

    def __str__(self) -> str:
        return self.nome

    @property
    def bairro(self) -> str:
        endereco = getattr(self, 'endereco', None)
        return endereco.bairro if endereco else ''


class Endereco(models.Model):
    cidadao = models.OneToOneField(
        Cidadao,
        on_delete=models.CASCADE,
        related_name='endereco',
        verbose_name='cidadão',
    )
    logradouro = models.CharField('logradouro', max_length=200, blank=True)
    numero = models.CharField('número', max_length=20, blank=True)
    complemento = models.CharField('complemento', max_length=100, blank=True)
    bairro = models.CharField('bairro', max_length=120, blank=True)
    cidade = models.CharField('cidade', max_length=120, blank=True)
    estado = models.CharField('estado', max_length=2, blank=True)
    cep = models.CharField('CEP', max_length=9, blank=True)
    latitude = models.DecimalField(
        'latitude',
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    longitude = models.DecimalField(
        'longitude',
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'endereço'
        verbose_name_plural = 'endereços'

    def __str__(self) -> str:
        return f'{self.logradouro}, {self.numero} — {self.cidadao.nome}'


class PerfilProfissional(models.Model):
    cidadao = models.ForeignKey(
        Cidadao,
        on_delete=models.CASCADE,
        related_name='perfis_profissionais',
        verbose_name='cidadão',
    )
    instituicao = models.CharField('instituição', max_length=200)
    cargo = models.CharField('cargo', max_length=120)
    tag = models.ForeignKey(
        Tag,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='perfis_profissionais',
        verbose_name='tag',
    )

    class Meta:
        verbose_name = 'perfil profissional'
        verbose_name_plural = 'perfis profissionais'
        ordering = ('id',)

    def __str__(self) -> str:
        return f'{self.cargo} @ {self.instituicao}'


class DocumentoAnexo(models.Model):
    class Categoria(models.TextChoices):
        CURRICULO = 'curriculo', 'Currículo'
        DOCUMENTO_PESSOAL = 'documento_pessoal', 'Documento pessoal'
        LAUDO_MEDICO = 'laudo_medico', 'Laudo médico'
        COMPROVANTE_RESIDENCIA = 'comprovante_residencia', 'Comprovante de residência'
        OUTROS = 'outros', 'Outros'

    cidadao = models.ForeignKey(
        Cidadao,
        on_delete=models.CASCADE,
        related_name='documentos',
        verbose_name='cidadão',
    )
    categoria = models.CharField(
        'categoria',
        max_length=32,
        choices=Categoria.choices,
        default=Categoria.OUTROS,
    )
    arquivo = models.FileField('arquivo', upload_to=documento_cidadao_upload_to)
    nome_original = models.CharField('nome original', max_length=255)
    content_type = models.CharField('tipo MIME', max_length=120, blank=True)
    tamanho = models.PositiveIntegerField('tamanho (bytes)')
    enviado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documentos_crm_enviados',
        verbose_name='enviado por',
    )
    created_at = models.DateTimeField('enviado em', auto_now_add=True)
    etiquetas = models.ManyToManyField(
        Tag,
        related_name='documentos_curriculo',
        blank=True,
        verbose_name='etiquetas de serviços (currículo)',
        help_text='Matchmaking: tags do módulo Serviços vinculadas ao currículo.',
    )

    class Meta:
        verbose_name = 'documento anexo'
        verbose_name_plural = 'documentos anexos'
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return self.nome_original


class MigracaoLegadoRef(models.Model):
    """Mapeamento id legado → registro GabTech (importação edsons79 e similares)."""

    class Tipo(models.TextChoices):
        CADASTRO = 'cadastro', 'Cadastro'
        ATENDIMENTO = 'atendimento', 'Atendimento'
        EVENTO = 'evento', 'Evento'
        ANEXO_CADASTRO = 'anexo_cadastro', 'Anexo cadastro'
        ANEXO_ATENDIMENTO = 'anexo_atendimento', 'Anexo atendimento'
        LEGISLATIVO = 'legislativo', 'Legislativo'

    tipo = models.CharField('tipo', max_length=32, choices=Tipo.choices)
    legacy_id = models.PositiveIntegerField('ID legado')
    gabtech_id = models.PositiveIntegerField('ID GabTech')
    meta = models.JSONField('metadados', default=dict, blank=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        db_table = 'legado_migracao_ref'
        verbose_name = 'referência migração legado'
        verbose_name_plural = 'referências migração legado'
        constraints = [
            models.UniqueConstraint(
                fields=('tipo', 'legacy_id'),
                name='legado_migracao_ref_tipo_legacy_uniq',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.tipo}:{self.legacy_id}→{self.gabtech_id}'
