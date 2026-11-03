"""
Associa um host HTTP adicional a um gabinete (tenant) existente.

Uso (dev): python manage.py adicionar_dominio --schema gabinete_demo --domain localhost
"""

from django.core.management.base import BaseCommand, CommandError

from core.models import Dominio, Gabinete


class Command(BaseCommand):
    help = 'Adiciona domínio extra a um tenant (schema public).'

    def add_arguments(self, parser):
        parser.add_argument('--schema', required=True, help='Schema do tenant')
        parser.add_argument('--domain', required=True, help='Host sem porta (ex.: localhost)')
        parser.add_argument(
            '--primary',
            action='store_true',
            help='Define como domínio primário do tenant',
        )

    def handle(self, *args, **options):
        schema_name = options['schema'].strip().lower()
        domain = options['domain'].strip().lower()

        try:
            gabinete = Gabinete.objects.get(schema_name=schema_name)
        except Gabinete.DoesNotExist as exc:
            raise CommandError(f'Tenant "{schema_name}" não encontrado.') from exc

        if Dominio.objects.filter(domain=domain).exists():
            raise CommandError(f'Domínio "{domain}" já está em uso.')

        if options['primary']:
            Dominio.objects.filter(tenant=gabinete, is_primary=True).update(is_primary=False)

        Dominio.objects.create(
            domain=domain,
            tenant=gabinete,
            is_primary=options['primary'],
        )

        self.stdout.write(
            self.style.SUCCESS(f'Domínio "{domain}" → schema {schema_name}')
        )
