"""Importação faseada do dump edsons79_sys para tenant configurado."""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import tenant_context

from core.legado.config_edsonsantos import carregar_config
from core.legado.import_fase1_crm import executar_fase1_crm
from core.legado.import_fase2_atendimentos import executar_fase2_atendimentos
from core.legado.import_fase4_anexos import executar_fase4_anexos
from core.legado.import_fase3_agenda import executar_fase3_agenda
from core.legado.import_fase5_legislativo import executar_fase5_legislativo
from core.models import Gabinete


class Command(BaseCommand):
    help = 'Migra dados do legado edsons79 (fases 1–5: CRM, atendimentos, agenda, anexos, legislativo).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--config',
            default='deploy/migracao/edsonsantos.yaml',
            help='YAML de parametrização',
        )
        parser.add_argument('--fase', type=int, default=1, choices=[1, 2, 3, 4, 5])
        parser.add_argument(
            '--dry-run',
            action='store_true',
            default=None,
            help='Simular (padrão do YAML: dry_run_default)',
        )
        parser.add_argument(
            '--executar',
            action='store_true',
            help='Gravar no banco (desliga dry-run)',
        )
        parser.add_argument('--limit', type=int, default=None, help='Limitar registros (teste)')

    def handle(self, *args, **options):
        fase = options['fase']

        repo_root = Path(settings.BASE_DIR).parent
        config_path = Path(options['config'])
        if not config_path.is_absolute():
            config_path = repo_root / config_path
        if not config_path.is_file():
            raise CommandError(f'Config não encontrada: {config_path}')

        config = carregar_config(config_path, repo_root)
        if not config.sql_path.is_file():
            raise CommandError(f'SQL não encontrado: {config.sql_path}')

        try:
            gabinete = Gabinete.objects.get(schema_name=config.schema_name)
        except Gabinete.DoesNotExist as exc:
            raise CommandError(f'Tenant {config.schema_name} não encontrado.') from exc

        dry_run = config.raw['execucao'].get('dry_run_default', True)
        if options['executar']:
            dry_run = False
        elif options['dry_run'] is True:
            dry_run = True

        if dry_run:
            self.stdout.write(self.style.WARNING('Modo dry-run — nenhuma gravação.'))
        else:
            self.stdout.write(self.style.WARNING('Modo EXECUTAR — gravando no tenant.'))

        with tenant_context(gabinete):
            if fase == 1:
                resultado = executar_fase1_crm(
                    config,
                    dry_run=dry_run,
                    limit=options['limit'],
                )
            elif fase == 2:
                resultado = executar_fase2_atendimentos(
                    config,
                    dry_run=dry_run,
                    limit=options['limit'],
                )
            elif fase == 3:
                resultado = executar_fase3_agenda(
                    config,
                    dry_run=dry_run,
                    limit=options['limit'],
                )
            elif fase == 4:
                resultado = executar_fase4_anexos(
                    config,
                    dry_run=dry_run,
                    limit=options['limit'],
                )
            elif fase == 5:
                resultado = executar_fase5_legislativo(
                    config,
                    dry_run=dry_run,
                    limit=options['limit'],
                    repo_root=repo_root,
                )
            else:
                raise CommandError(f'Fase {fase} inválida.')

        self.stdout.write(self.style.SUCCESS(resultado.resumo()))
        for err in resultado.erros[:20]:
            self.stdout.write(self.style.ERROR(err))
        if len(resultado.erros) > 20:
            self.stdout.write(f'… +{len(resultado.erros) - 20} erros')
