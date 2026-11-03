"""
Popula módulos, permissões e perfis padrão no schema de um tenant.

Uso:
  python manage.py seed_rbac --schema=gabinete_demo
  python manage.py tenant_command seed_rbac --schema=gabinete_demo
"""

from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import schema_context

from core.models import Gabinete
from usuarios.rbac_seed import executar_seed_rbac


class Command(BaseCommand):
    help = 'Seed de governança (RBAC) no schema do gabinete informado.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            required=True,
            help='Nome do schema PostgreSQL do tenant (ex.: gabinete_demo)',
        )
    def handle(self, *args, **options):
        schema_name = options['schema'].strip().lower()

        try:
            gabinete = Gabinete.objects.get(schema_name=schema_name)
        except Gabinete.DoesNotExist as exc:
            raise CommandError(f'Tenant/schema "{schema_name}" não encontrado.') from exc

        with schema_context(gabinete.schema_name):
            permissoes, perfis, superusers = executar_seed_rbac()

        self.stdout.write(
            self.style.SUCCESS(
                f'RBAC seed concluído em "{schema_name}": '
                f'{permissoes} permissões, {perfis} perfis padrão sincronizados, '
                f'{superusers} superusuário(s) vinculado(s) ao perfil Administrador.'
            )
        )
