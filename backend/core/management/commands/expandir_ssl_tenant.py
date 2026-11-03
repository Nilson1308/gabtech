"""Expande certificado Let's Encrypt para domínio de tenant (executar como root)."""

import os
import subprocess
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Adiciona FQDN ao cert nginx (certbot --expand). Requer root/sudo.'

    def add_arguments(self, parser):
        parser.add_argument('--domain', required=True, help='Ex.: cliente.gabtech.app.br')

    def handle(self, *args, **options):
        domain = options['domain'].strip().lower()
        script = Path('/var/www/gabtech/deploy/certbot-expand-domain.sh')
        if not script.is_file():
            raise CommandError(f'Script não encontrado: {script}')

        cmd = [str(script), domain] if os.geteuid() == 0 else ['sudo', str(script), domain]
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as exc:
            raise CommandError(f'certbot falhou (code {exc.returncode})') from exc
        self.stdout.write(self.style.SUCCESS(f'SSL atualizado para {domain}'))
