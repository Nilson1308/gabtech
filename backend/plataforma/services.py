from __future__ import annotations

import logging
import threading
import uuid

from django.db import close_old_connections
from django.utils import timezone
from django_tenants.utils import get_public_schema_name, schema_context

from core.provisioning import DadosNovoGabinete, provisionar_gabinete_completo
from plataforma.models import CadastroGabinete

logger = logging.getLogger(__name__)


def executar_provisionamento(cadastro_id: uuid.UUID | str, senha_admin: str) -> None:
    if isinstance(cadastro_id, str):
        cadastro_id = uuid.UUID(cadastro_id)

    close_old_connections()
    public = get_public_schema_name()
    with schema_context(public):
        cadastro = CadastroGabinete.objects.get(pk=cadastro_id)
        cadastro.status = CadastroGabinete.Status.PROCESSANDO
        cadastro.tentativas += 1
        cadastro.erro_mensagem = ''
        cadastro.save(update_fields=['status', 'tentativas', 'erro_mensagem', 'updated_at'])

        try:
            dados = DadosNovoGabinete(
                nome=cadastro.nome_gabinete,
                slug=cadastro.slug,
                admin_nome=cadastro.admin_nome,
                admin_email=cadastro.admin_email,
                admin_senha=senha_admin,
                logo=cadastro.logo or '',
                logo_formato=cadastro.logo_formato or '1:1',
            )
            _gabinete, schema_name, domain = provisionar_gabinete_completo(dados)
            cadastro.status = CadastroGabinete.Status.CONCLUIDO
            cadastro.schema_name = schema_name
            cadastro.domain = domain
            cadastro.concluido_em = timezone.now()
            cadastro.save(
                update_fields=[
                    'status',
                    'schema_name',
                    'domain',
                    'concluido_em',
                    'updated_at',
                ],
            )
        except Exception as exc:
            logger.exception('Falha ao provisionar cadastro %s', cadastro_id)
            cadastro.status = CadastroGabinete.Status.FALHOU
            cadastro.erro_mensagem = str(exc)[:2000]
            cadastro.save(update_fields=['status', 'erro_mensagem', 'updated_at'])
        finally:
            close_old_connections()


def enfileirar_provisionamento(cadastro: CadastroGabinete, senha_admin: str) -> None:
    thread = threading.Thread(
        target=executar_provisionamento,
        args=(cadastro.pk, senha_admin),
        daemon=True,
        name=f'provision-{cadastro.slug}',
    )
    thread.start()
