import uuid

from django.contrib.auth.hashers import check_password, make_password
from django.db import models


class OperadorPlataforma(models.Model):
    """Credencial de ops (schema public) — não é o User dos gabinetes."""

    email = models.EmailField('e-mail', unique=True)
    nome = models.CharField('nome', max_length=200)
    senha = models.CharField('senha', max_length=128)
    is_active = models.BooleanField('ativo', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'operador da plataforma'
        verbose_name_plural = 'operadores da plataforma'

    def __str__(self) -> str:
        return self.email

    def set_senha(self, raw: str) -> None:
        self.senha = make_password(raw)

    def verificar_senha(self, raw: str) -> bool:
        return check_password(raw, self.senha)


class CadastroGabinete(models.Model):
    """Solicitação de self-service — dados sensíveis (senha) não são persistidos."""

    class Status(models.TextChoices):
        PENDENTE = 'pendente', 'Pendente'
        PROCESSANDO = 'processando', 'Processando'
        CONCLUIDO = 'concluido', 'Concluído'
        FALHOU = 'falhou', 'Falhou'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDENTE,
        db_index=True,
    )

    slug = models.SlugField('identificador', max_length=50, unique=True)
    nome_gabinete = models.CharField('nome do gabinete', max_length=200)
    logo = models.TextField('logo ou brasão', blank=True)
    logo_formato = models.CharField(
        'formato do logo',
        max_length=5,
        blank=True,
        default='1:1',
    )
    schema_name = models.CharField(max_length=63, blank=True)
    domain = models.CharField(max_length=253, blank=True)

    admin_nome = models.CharField('nome do administrador', max_length=300)
    admin_email = models.EmailField('e-mail do administrador')

    aceite_termos = models.BooleanField('aceite dos termos', default=False)
    ip_origem = models.GenericIPAddressField(null=True, blank=True)

    erro_mensagem = models.TextField(blank=True)
    tentativas = models.PositiveSmallIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    concluido_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'cadastro de gabinete'
        verbose_name_plural = 'cadastros de gabinetes'
        ordering = ('-created_at',)

    def __str__(self) -> str:
        return f'{self.nome_gabinete} ({self.slug}) — {self.status}'
