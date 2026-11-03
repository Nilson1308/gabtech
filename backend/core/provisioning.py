"""
Provisionamento de gabinete (tenant): schema, migrations, RBAC e admin inicial.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from django.conf import settings
from django.core.management import call_command
from django.db import transaction

from core.models import Dominio, Gabinete


SLUG_RE = re.compile(r'^[a-z0-9](?:[a-z0-9-]{1,48}[a-z0-9])?$')
SCHEMA_RE = re.compile(r'^[a-z][a-z0-9_]{0,62}$')


@dataclass
class DadosNovoGabinete:
    nome: str
    slug: str
    admin_nome: str
    admin_email: str
    admin_senha: str
    logo: str = ''
    logo_formato: str = '1:1'


def normalizar_slug(slug: str) -> str:
    return slug.strip().lower().replace('_', '-')


def slug_para_schema_name(slug: str) -> str:
    base = slug.replace('-', '_')
    schema = f'gab_{base}'[:63]
    if not SCHEMA_RE.match(schema):
        raise ValueError('Identificador do gabinete inválido.')
    return schema


def montar_dominio_tenant(slug: str) -> str:
    suffix = getattr(settings, 'GABTECH_TENANT_DOMAIN_SUFFIX', 'localhost').strip().lstrip('.')
    return f'{slug}.{suffix}' if suffix else slug


def validar_slug(slug: str) -> None:
    if not SLUG_RE.match(slug):
        raise ValueError(
            'Use 3–50 caracteres: letras minúsculas, números e hífens (sem espaços).',
        )
    reservados = getattr(settings, 'GABTECH_SLUGS_RESERVADOS', frozenset())
    if slug in reservados:
        raise ValueError('Este identificador está reservado.')


def validar_disponibilidade(slug: str, schema_name: str, domain: str) -> None:
    if Gabinete.objects.filter(schema_name=schema_name).exists():
        raise ValueError('Já existe um gabinete com este identificador.')
    if Dominio.objects.filter(domain=domain).exists():
        raise ValueError('Este endereço já está em uso.')


@transaction.atomic
def registrar_gabinete(
    nome: str,
    schema_name: str,
    domain: str,
    logo: str = '',
    logo_formato: str = '1:1',
) -> Gabinete:
    gabinete = Gabinete(
        schema_name=schema_name,
        nome=nome,
        logo=logo or '',
        logo_formato=logo_formato or '1:1',
    )
    gabinete.save()
    Dominio.objects.create(domain=domain, tenant=gabinete, is_primary=True)
    return gabinete


def aplicar_migrations_tenant(schema_name: str) -> None:
    call_command('migrate_schemas', schema_name=schema_name, verbosity=0)


def criar_administrador_inicial(
    schema_name: str,
    *,
    nome: str,
    email: str,
    senha: str,
) -> None:
    from django_tenants.utils import schema_context

    from usuarios.models import Perfil, User
    from usuarios.rbac_seed import executar_seed_rbac
    from usuarios.rbac_utils import obter_perfil_administrador
    from usuarios.serializers import _aplicar_nome, _sincronizar_status_ativo, _username_disponivel

    with schema_context(schema_name):
        executar_seed_rbac()

        perfil = obter_perfil_administrador()
        if perfil is None:
            perfil = Perfil.objects.filter(is_admin=True).first()
        if perfil is None:
            raise RuntimeError('Perfil Administrador não encontrado após seed RBAC.')

        email_norm = email.strip().lower()
        if User.objects.filter(email__iexact=email_norm).exists():
            raise ValueError('E-mail de administrador já cadastrado neste gabinete.')

        username = _username_disponivel(email_norm.split('@')[0].replace('.', '_') or 'admin')
        user = User(
            username=username,
            email=email_norm,
            status=User.Status.ATIVO,
            is_active=True,
            is_staff=True,
            is_superuser=True,
            perfil=perfil,
        )
        _aplicar_nome(user, nome.strip())
        user.set_password(senha)
        _sincronizar_status_ativo(user)
        user.save()


def provisionar_gabinete_completo(dados: DadosNovoGabinete) -> tuple[Gabinete, str, str]:
    slug = normalizar_slug(dados.slug)
    validar_slug(slug)
    schema_name = slug_para_schema_name(slug)
    domain = montar_dominio_tenant(slug)
    validar_disponibilidade(slug, schema_name, domain)

    gabinete = registrar_gabinete(
        dados.nome.strip(),
        schema_name,
        domain,
        logo=dados.logo,
        logo_formato=dados.logo_formato or '1:1',
    )
    aplicar_migrations_tenant(schema_name)
    criar_administrador_inicial(
        schema_name,
        nome=dados.admin_nome,
        email=dados.admin_email,
        senha=dados.admin_senha,
    )
    return gabinete, schema_name, domain


def url_api_tenant(domain: str) -> str:
    port = str(getattr(settings, 'GABTECH_TENANT_API_PORT', '') or '')
    scheme = getattr(settings, 'GABTECH_TENANT_URL_SCHEME', 'http')
    omit_port = (scheme == 'https' and port in ('443', '')) or (
        scheme == 'http' and port in ('80', '')
    )
    if omit_port:
        return f'{scheme}://{domain}'
    return f'{scheme}://{domain}:{port}'
