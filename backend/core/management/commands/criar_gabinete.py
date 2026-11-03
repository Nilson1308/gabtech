"""
Cria um gabinete (tenant) + domínio no schema public.
Uso (dev): python manage.py criar_gabinete --schema gabinete_demo --nome "Gabinete Demo" --domain demo.localhost
"""

from django.core.management.base import BaseCommand, CommandError

from core.provisioning import normalizar_slug, registrar_gabinete, validar_disponibilidade, validar_slug


class Command(BaseCommand):
    help = 'Registra um novo gabinete (schema PostgreSQL) e seu domínio HTTP.'

    def add_arguments(self, parser):
        parser.add_argument('--schema', required=True, help='Nome do schema (ex.: gabinete_a)')
        parser.add_argument('--nome', required=True, help='Nome exibido do gabinete')
        parser.add_argument('--domain', required=True, help='Host (ex.: gabinete-a.localhost)')

    def handle(self, *args, **options):
        schema_name = options['schema'].strip().lower()
        nome = options['nome'].strip()
        domain = options['domain'].strip().lower()

        slug = normalizar_slug(domain.split('.')[0])
        try:
            validar_slug(slug)
        except ValueError as exc:
            raise CommandError(str(exc)) from exc
        try:
            validar_disponibilidade(slug, schema_name, domain)
        except ValueError as exc:
            raise CommandError(str(exc)) from exc

        gabinete = registrar_gabinete(nome, schema_name, domain)

        self.stdout.write(
            self.style.SUCCESS(
                f'Gabinete criado: {nome} | schema={schema_name} | domain={domain}'
            )
        )
