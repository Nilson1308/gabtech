"""
Reprocessa cadastros presos em pendente/processando (ex.: após restart do servidor).

Uso: python manage.py processar_cadastros_pendentes
Requer senha temporária — apenas para recuperação em dev; cadastros incompletos
devem ser refeitos pelo usuário em produção.
"""

from django.core.management.base import BaseCommand

from plataforma.models import CadastroGabinete


class Command(BaseCommand):
    help = 'Lista cadastros não concluídos (não reprovisiona automaticamente).'

    def handle(self, *args, **options):
        qs = CadastroGabinete.objects.exclude(status=CadastroGabinete.Status.CONCLUIDO)
        if not qs.exists():
            self.stdout.write(self.style.SUCCESS('Nenhum cadastro pendente ou com falha.'))
            return
        for c in qs:
            self.stdout.write(
                f'{c.id} | {c.slug} | {c.status} | {c.erro_mensagem[:80] if c.erro_mensagem else "-"}',
            )
