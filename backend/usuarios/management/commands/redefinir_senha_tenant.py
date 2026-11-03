"""Redefine senha de usuário em um schema de gabinete (suporte / dev)."""

from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import tenant_context

from core.models import Gabinete
from usuarios.models import User


class Command(BaseCommand):
    help = 'Redefine a senha de um usuário pelo e-mail dentro do schema do gabinete.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            required=True,
            help='schema_name do gabinete (ex.: gab_gab_edsonsantos)',
        )
        parser.add_argument('--email', required=True, help='E-mail do usuário')
        parser.add_argument('--senha', required=True, help='Nova senha')

    def handle(self, *args, **options):
        schema = options['schema'].strip()
        email = options['email'].strip().lower()
        senha = options['senha']

        try:
            gabinete = Gabinete.objects.get(schema_name=schema)
        except Gabinete.DoesNotExist as exc:
            raise CommandError(f'Gabinete com schema "{schema}" não encontrado.') from exc

        with tenant_context(gabinete):
            user = User.objects.filter(email__iexact=email).first()
            if user is None:
                raise CommandError(f'Usuário {email} não encontrado neste gabinete.')
            user.set_password(senha)
            user.save(update_fields=['password'])
            self.stdout.write(
                self.style.SUCCESS(
                    f'Senha atualizada para {email} (username: {user.username}) em {schema}.',
                ),
            )
