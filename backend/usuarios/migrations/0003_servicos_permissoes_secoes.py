"""
Cria permissões de seção do módulo Serviços e concede a perfis que já tinham
«gerenciar_talentos» (compatibilidade com RBAC anterior monolítico).
"""

from django.db import migrations


NOVAS_PERMISSOES = (
    {
        'codename': 'gerenciar_assistencia',
        'nome': 'Gerenciar Assistência Social',
        'descricao': 'Itens de benefício, entregas e registro de público atendido',
    },
    {
        'codename': 'gerenciar_cursos',
        'nome': 'Gerenciar Cursos & Capacitação',
        'descricao': 'Turmas, inscrições, lista de espera e matchmaking de capacitação',
    },
)

DESCRICOES_ATUALIZADAS = {
    'ler_servicos': (
        'Acessar o módulo (visão geral), consultar dados e sugestões '
        'inteligentes em todas as seções'
    ),
    'gerenciar_talentos': 'Vagas, candidaturas, pipeline seletivo e matchmaking de currículos',
}


def _forward(apps, schema_editor):
    Modulo = apps.get_model('usuarios', 'Modulo')
    Permissao = apps.get_model('usuarios', 'Permissao')
    Perfil = apps.get_model('usuarios', 'Perfil')

    modulo = Modulo.objects.filter(codename='servicos').first()
    if not modulo:
        return

    modulo.nome = 'Serviços & Entregas'
    modulo.icone = 'briefcase'
    modulo.cor = '#6366f1'
    modulo.save(update_fields=['nome', 'icone', 'cor'])

    for codename, descricao in DESCRICOES_ATUALIZADAS.items():
        Permissao.objects.filter(codename=codename, modulo=modulo).update(descricao=descricao)

    novas: list = []
    for item in NOVAS_PERMISSOES:
        perm, _ = Permissao.objects.get_or_create(
            codename=item['codename'],
            defaults={
                'nome': item['nome'],
                'descricao': item['descricao'],
                'modulo': modulo,
            },
        )
        if perm.nome != item['nome'] or perm.descricao != item['descricao']:
            perm.nome = item['nome']
            perm.descricao = item['descricao']
            perm.modulo = modulo
            perm.save(update_fields=['nome', 'descricao', 'modulo'])
        novas.append(perm)

    talentos = Permissao.objects.filter(codename='gerenciar_talentos').first()
    if not talentos or not novas:
        return

    for perfil in Perfil.objects.filter(permissoes=talentos).distinct():
        perfil.permissoes.add(*novas)


def _backward(apps, schema_editor):
    Permissao = apps.get_model('usuarios', 'Permissao')
    Permissao.objects.filter(
        codename__in=[p['codename'] for p in NOVAS_PERMISSOES],
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_user_assinatura_visual'),
    ]

    operations = [
        migrations.RunPython(_forward, _backward),
    ]
