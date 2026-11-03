"""Cria operador de ops no schema public (login do /admin/ da plataforma)."""

from getpass import getpass

from django.core.management.base import BaseCommand, CommandError

from plataforma.models import OperadorPlataforma


class Command(BaseCommand):
    help = 'Cria credencial para o Django Admin da plataforma (schema public).'

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True)
        parser.add_argument('--nome', default='Operador Plataforma')
        parser.add_argument('--senha', default='', help='Se omitida, solicita no terminal.')

    def handle(self, *args, **options):
        email = options['email'].strip().lower()
        nome = options['nome'].strip()
        senha = options['senha'] or getpass('Senha: ')
        if len(senha) < 8:
            raise CommandError('Senha deve ter ao menos 8 caracteres.')

        if OperadorPlataforma.objects.filter(email__iexact=email).exists():
            raise CommandError(f'Operador "{email}" já existe.')

        op = OperadorPlataforma(email=email, nome=nome, is_active=True)
        op.set_senha(senha)
        op.save()

        self.stdout.write(self.style.SUCCESS(f'Operador criado: {email}'))
