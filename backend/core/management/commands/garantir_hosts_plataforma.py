"""
Registra o tenant do schema public e domínios de plataforma (api, app, raiz).

Necessário para SHOW_PUBLIC_IF_NO_TENANT_FOUND=false sem quebrar api/app.
"""

from django.core.management.base import BaseCommand
from django_tenants.utils import get_public_schema_name, schema_context

from core.models import Dominio, Gabinete


DEFAULT_HOSTS = (
    'api.gabtech.app.br',
    'app.gabtech.app.br',
    'gabtech.app.br',
    'www.gabtech.app.br',
)


class Command(BaseCommand):
    help = 'Cria tenant schema public (se faltar) e domínios HTTP da plataforma.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--domain',
            action='append',
            dest='domains',
            help='Host adicional (pode repetir). Padrão: api/app/gabtech/www .gabtech.app.br',
        )

    def handle(self, *args, **options):
        hosts = options['domains'] or list(DEFAULT_HOSTS)
        public_schema = get_public_schema_name()

        with schema_context(public_schema):
            gabinete, created = Gabinete.objects.get_or_create(
                schema_name=public_schema,
                defaults={'nome': 'Plataforma GabTech'},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Tenant public criado (id={gabinete.pk}).'))
            else:
                self.stdout.write(f'Tenant public já existe (id={gabinete.pk}).')

            primary = 'api.gabtech.app.br'
            for domain in hosts:
                domain = domain.strip().lower()
                if not domain:
                    continue
                if Dominio.objects.filter(domain=domain).exists():
                    self.stdout.write(f'  • {domain} — já cadastrado')
                    continue
                Dominio.objects.create(
                    domain=domain,
                    tenant=gabinete,
                    is_primary=(domain == primary),
                )
                self.stdout.write(self.style.SUCCESS(f'  • {domain} → schema public'))
