from django.contrib.auth.models import AbstractUser
from django.db import models


class Modulo(models.Model):
    """Agrupamento de permissões (catálogo RBAC por schema de tenant)."""

    codename = models.SlugField('código', max_length=50, unique=True)
    nome = models.CharField('nome', max_length=120)
    icone = models.CharField('ícone', max_length=50, blank=True)
    cor = models.CharField('cor', max_length=7, default='#6b7280')

    class Meta:
        verbose_name = 'módulo'
        verbose_name_plural = 'módulos'
        ordering = ('nome',)

    def __str__(self) -> str:
        return self.nome


class Permissao(models.Model):
    """
    Permissão atômica — codenames em português (ex.: ler_crm, criar_agenda).
    Fonte da verdade para autorização no backend.
    """

    codename = models.SlugField('codename', max_length=64, unique=True)
    nome = models.CharField('nome', max_length=120)
    descricao = models.TextField('descrição', blank=True)
    modulo = models.ForeignKey(
        Modulo,
        on_delete=models.CASCADE,
        related_name='permissoes',
        verbose_name='módulo',
    )

    class Meta:
        verbose_name = 'permissão'
        verbose_name_plural = 'permissões'
        ordering = ('modulo__nome', 'codename')

    def __str__(self) -> str:
        return self.codename


class Perfil(models.Model):
    """Perfil RBAC atribuído aos usuários do gabinete."""

    nome = models.CharField('nome', max_length=100)
    cor = models.CharField('cor', max_length=7, default='#3b82f6')
    icone = models.CharField('ícone', max_length=50, blank=True)
    descricao = models.TextField('descrição', blank=True)
    is_admin = models.BooleanField(
        'administrador',
        default=False,
        help_text='Ignora checagem granular e concede todas as permissões.',
    )
    permissoes = models.ManyToManyField(
        Permissao,
        blank=True,
        related_name='perfis',
        verbose_name='permissões',
    )
    created_at = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'perfil'
        verbose_name_plural = 'perfis'
        ordering = ('nome',)

    def __str__(self) -> str:
        return self.nome


class User(AbstractUser):
    """
    Usuário do gabinete (existente apenas no schema do tenant).
    `cargo` na API/sessão é derivado do perfil RBAC.
    """

    class Status(models.TextChoices):
        ATIVO = 'ativo', 'Ativo'
        INATIVO = 'inativo', 'Inativo'

    avatar = models.URLField('avatar', blank=True)
    assinatura_visual = models.FileField(
        'assinatura visual',
        upload_to='usuarios/assinaturas/',
        blank=True,
        null=True,
    )
    status = models.CharField(
        'status',
        max_length=10,
        choices=Status.choices,
        default=Status.ATIVO,
    )
    perfil = models.ForeignKey(
        Perfil,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='usuarios',
        verbose_name='perfil RBAC',
    )

    class Meta:
        verbose_name = 'usuário'
        verbose_name_plural = 'usuários'

    @property
    def nome(self) -> str:
        completo = self.get_full_name().strip()
        return completo or self.username

    @property
    def cargo(self) -> str:
        if self.perfil_id:
            return self.perfil.nome
        if self.is_superuser:
            return 'Administrador'
        return ''

    @property
    def is_ativo(self) -> bool:
        return self.status == self.Status.ATIVO and self.is_active

    @property
    def tem_acesso_total(self) -> bool:
        return self.is_superuser or bool(self.perfil_id and self.perfil.is_admin)

    def get_permissao_codenames(self) -> list[str]:
        if self.tem_acesso_total:
            return list(
                Permissao.objects.values_list('codename', flat=True).order_by('codename')
            )
        if not self.perfil_id:
            return []
        return list(
            self.perfil.permissoes.values_list('codename', flat=True).order_by('codename')
        )
