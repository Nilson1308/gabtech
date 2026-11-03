"""Gera inventário JSON a partir do dump edsons79_sys.sql."""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from core.legado.inventario_edsons79 import analisar_dump, salvar_inventario


class Command(BaseCommand):
    help = 'Analisa public/db_bkp/edsonsantos/edsons79_sys.sql e grava inventário JSON.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sql',
            default='public/db_bkp/edsonsantos/edsons79_sys.sql',
            help='Caminho do dump .sql (relativo à raiz do repo ou absoluto)',
        )
        parser.add_argument(
            '--saida',
            default='deploy/migracao/edsonsantos-inventario.json',
            help='Arquivo JSON de saída',
        )

    def handle(self, *args, **options):
        base = Path(settings.BASE_DIR).parent
        sql_path = Path(options['sql'])
        if not sql_path.is_absolute():
            sql_path = base / sql_path
        if not sql_path.is_file():
            raise CommandError(f'Dump não encontrado: {sql_path}')

        inv = analisar_dump(sql_path)
        out = Path(options['saida'])
        if not out.is_absolute():
            out = base / out
        salvar_inventario(inv, out)

        self.stdout.write(self.style.SUCCESS(f'Inventário gravado em {out}'))
        self.stdout.write(f"  Cadastros: {inv.cadastro_total} (stts={inv.cadastro_stts})")
        self.stdout.write(f"  Atendimentos: {inv.atendimento_total} (órfãos vCad: {inv.atendimento_orfaos_vcad})")
        self.stdout.write(f"  Eventos: {inv.eventos_total} | Legislativo: {inv.legislativo_total}")
        self.stdout.write(
            f"  Anexos meta: cadastro={inv.cadastro_docs_total} atendimento={inv.atendimento_docs_total}",
        )
