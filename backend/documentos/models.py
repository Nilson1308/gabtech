from django.conf import settings
from django.db import models


class TipoDocumento(models.Model):
    nome = models.CharField('nome', max_length=120)
    slug = models.SlugField('slug', max_length=80, unique=True)
    descricao = models.TextField('descrição', blank=True)
    icone = models.CharField('ícone', max_length=50, default='file-text')
    cor = models.CharField('cor', max_length=7, default='#3b82f6')
    is_sistema = models.BooleanField('tipo do sistema', default=False)

    class Meta:
        verbose_name = 'tipo de documento'
        verbose_name_plural = 'tipos de documento'
        ordering = ('nome',)

    def __str__(self) -> str:
        return self.nome


class TemplateDocumento(models.Model):
    nome = models.CharField('nome', max_length=200)
    tipo_documento = models.ForeignKey(
        TipoDocumento,
        on_delete=models.CASCADE,
        related_name='templates',
        verbose_name='tipo de documento',
    )
    descricao = models.TextField('descrição', blank=True)
    conteudo = models.TextField('conteúdo HTML')
    is_default = models.BooleanField('padrão do tipo', default=False)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'template de documento'
        verbose_name_plural = 'templates de documento'
        ordering = ('tipo_documento__nome', 'nome')

    def __str__(self) -> str:
        return self.nome


class EtiquetaDocumento(models.Model):
    nome = models.CharField('nome', max_length=120, unique=True)
    cor = models.CharField('cor', max_length=7, default='#6b7280')
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'etiqueta de documento'
        verbose_name_plural = 'etiquetas de documento'
        ordering = ('nome',)

    def __str__(self) -> str:
        return self.nome


class PastaDocumento(models.Model):
    nome = models.CharField('nome', max_length=200)
    icone = models.CharField('ícone', max_length=50, default='folder')
    cor = models.CharField('cor', max_length=7, default='#3b82f6')
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='filhos',
        verbose_name='pasta pai',
    )
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'pasta de documento'
        verbose_name_plural = 'pastas de documento'
        ordering = ('nome',)

    def __str__(self) -> str:
        return self.nome


class Documento(models.Model):
    class Status(models.TextChoices):
        RASCUNHO = 'rascunho', 'Rascunho'
        AGUARDANDO_ASSINATURA = 'aguardando_assinatura', 'Aguardando assinatura'
        FINALIZADO = 'finalizado', 'Finalizado'

    titulo = models.CharField('título', max_length=500)
    tipo_documento = models.ForeignKey(
        TipoDocumento,
        on_delete=models.PROTECT,
        related_name='documentos',
        verbose_name='tipo',
    )
    pasta = models.ForeignKey(
        PastaDocumento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documentos',
        verbose_name='pasta',
    )
    conteudo = models.TextField('conteúdo HTML', blank=True, default='')
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='documentos_criados',
        verbose_name='autor',
    )
    status = models.CharField(
        'status',
        max_length=30,
        choices=Status.choices,
        default=Status.RASCUNHO,
    )
    versao_atual = models.PositiveIntegerField('versão atual', default=1)
    assinantes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='documentos_assinados',
        blank=True,
        verbose_name='assinantes',
    )
    etiquetas = models.ManyToManyField(
        EtiquetaDocumento,
        related_name='documentos',
        blank=True,
        verbose_name='etiquetas',
    )
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)
    finalizado_em = models.DateTimeField('finalizado em', null=True, blank=True)

    class Meta:
        verbose_name = 'documento'
        verbose_name_plural = 'documentos'
        ordering = ('-updated_at',)

    def __str__(self) -> str:
        return self.titulo


class VersaoDocumento(models.Model):
    documento = models.ForeignKey(
        Documento,
        on_delete=models.CASCADE,
        related_name='versoes',
        verbose_name='documento',
    )
    numero_versao = models.PositiveIntegerField('número da versão')
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='versoes_documento',
        verbose_name='autor',
    )
    conteudo = models.TextField('conteúdo HTML')
    mudancas = models.CharField('descrição da mudança', max_length=255, blank=True, default='')
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'versão de documento'
        verbose_name_plural = 'versões de documento'
        ordering = ('-numero_versao',)
        constraints = [
            models.UniqueConstraint(
                fields=('documento', 'numero_versao'),
                name='documentos_versao_numero_unico',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.documento_id} v{self.numero_versao}'
