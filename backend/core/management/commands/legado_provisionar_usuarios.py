"""Cria usuários a partir de tbUsuarios e reatribui responsável dos atendimentos migrados."""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import tenant_context

from core.legado.config_edsonsantos import carregar_config
from core.legado.provisionar_usuarios_legado import (
    executar_provisionamento_usuarios_legado,
    resumo_distribuicao_responsaveis,
)
from core.models import Gabinete


class Command(BaseCommand):
    help = (
        'Provisiona usuários do legado (tbUsuarios) e reatribui atendimentos via meta v_usu '
        'em legado_migracao_ref.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--config',
            default='deploy/migracao/edsonsantos.yaml',
            help='YAML de parametrização',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            default=None,
            help='Simular (padrão se --executar não for passado)',
        )
        parser.add_argument(
            '--executar',
            action='store_true',
            help='Gravar usuários e reatribuir atendimentos',
        )
        parser.add_argument(
            '--senha',
            default=None,
            help='Senha inicial para usuários criados (obrigatório com --executar)',
        )

    def handle(self, *args, **options):
        repo_root = Path(settings.BASE_DIR).parent
        config_path = Path(options['config'])
        if not config_path.is_absolute():
            config_path = repo_root / config_path
        if not config_path.is_file():
            raise CommandError(f'Config não encontrada: {config_path}')

        config = carregar_config(config_path, repo_root)
        dry_run = not options['executar']
        if options['dry_run'] is True:
            dry_run = True

        if dry_run:
            self.stdout.write(self.style.WARNING('Modo dry-run — nenhuma gravação.'))
        else:
            self.stdout.write(self.style.WARNING('Modo EXECUTAR — usuários e atendimentos serão alterados.'))

        try:
            gabinete = Gabinete.objects.get(schema_name=config.schema_name)
        except Gabinete.DoesNotExist as exc:
            raise CommandError(f'Tenant {config.schema_name} não encontrado.') from exc

        with tenant_context(gabinete):
            resultado = executar_provisionamento_usuarios_legado(
                config,
                dry_run=dry_run,
                senha=options['senha'],
            )

        self.stdout.write(self.style.SUCCESS(resultado.resumo()))

        if resultado.por_v_usu:
            self.stdout.write('Atendimentos por vUsu (legado):')
            for v_usu, qtd in sorted(resultado.por_v_usu.items(), key=lambda x: -x[1]):
                self.stdout.write(f'  vUsu={v_usu}: {qtd}')

        if resultado.plano:
            self.stdout.write('Plano de usuários:')
            for item in resultado.plano:
                self.stdout.write(f"  [{item['acao']}] id={item['legacy_id']} {item['login']} → {item['email']}")

        for err in resultado.erros:
            self.stdout.write(self.style.ERROR(err))

        if not dry_run and not resultado.erros:
            with tenant_context(gabinete):
                self.stdout.write('Distribuição atual de responsáveis:')
                for row in resumo_distribuicao_responsaveis():
                    nome = row.get('responsavel__first_name') or ''
                    self.stdout.write(
                        f"  {row['responsavel__email']} ({nome}): {row['n']}",
                    )
