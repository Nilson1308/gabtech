"""
Prepara o tenant demo para dev local: RBAC, contas com senha conhecida e seed Mogi.

Uso:
  python manage.py bootstrap_demo
  python manage.py bootstrap_demo --reset-seed
  python manage.py bootstrap_demo --senha=minhasenha123
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import schema_context

from core.demo_contas import DEV_SENHA_PADRAO, sincronizar_contas_demo
from core.models import Dominio, Gabinete
from usuarios.rbac_seed import executar_seed_rbac


class Command(BaseCommand):
    help = 'RBAC + contas demo + seed de conteúdo (gabinete_demo / localhost:8800).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            default='gabinete_demo',
            help='Schema do tenant demo (padrão: gabinete_demo)',
        )
        parser.add_argument(
            '--senha',
            default=DEV_SENHA_PADRAO,
            help=f'Senha das contas demo (padrão: {DEV_SENHA_PADRAO})',
        )
        parser.add_argument(
            '--reset-seed',
            action='store_true',
            help='Recria cidadãos/atendimentos/eventos demo (seed_demo --reset)',
        )

    def handle(self, *args, **options):
        schema_name = options['schema'].strip().lower()
        senha = options['senha']

        if len(senha) < 8:
            raise CommandError('A senha deve ter no mínimo 8 caracteres.')

        try:
            gabinete = Gabinete.objects.get(schema_name=schema_name)
        except Gabinete.DoesNotExist as exc:
            raise CommandError(
                f'Tenant "{schema_name}" não existe. '
                'Crie com: python manage.py criar_gabinete --schema gabinete_demo '
                '--nome "Gabinete Demo" --domain demo.localhost',
            ) from exc

        self._garantir_localhost(gabinete)

        with schema_context(gabinete.schema_name):
            permissoes, perfis, _super = executar_seed_rbac()
            emails = sincronizar_contas_demo(senha)

        seed_args = ['--schema', schema_name]
        if options['reset_seed']:
            seed_args.append('--reset')
        call_command('seed_demo', *seed_args)

        self.stdout.write(self.style.SUCCESS(f'Tenant: {schema_name} ({gabinete.nome})'))
        self.stdout.write(f'RBAC: {permissoes} permissões, {perfis} perfis.')
        self.stdout.write('Contas (app — login por e-mail):')
        for email in emails:
            self.stdout.write(f'  • {email}')
        self.stdout.write(f'Senha (todas): {senha}')
        self.stdout.write('')
        self.stdout.write('App:  http://localhost:5173/login')
        self.stdout.write('Admin Django (usuário admin): http://localhost:8800/admin/')
        self.stdout.write('  username: admin  |  e-mail admin no app: admin@demo.localhost')

    def _garantir_localhost(self, gabinete: Gabinete) -> None:
        if not Dominio.objects.filter(domain='localhost', tenant=gabinete).exists():
            if Dominio.objects.filter(domain='localhost').exists():
                self.stdout.write(
                    self.style.WARNING(
                        'Domínio "localhost" já aponta para outro tenant; '
                        'use demo.localhost:5173 ou ajuste Dominio no admin public.',
                    ),
                )
                return
            Dominio.objects.create(domain='localhost', tenant=gabinete, is_primary=False)
            self.stdout.write('Domínio localhost → gabinete_demo criado.')
