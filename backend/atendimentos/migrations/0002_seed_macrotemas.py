from django.db import migrations


MACROTEMAS = [
    {'nome': 'Saúde', 'cor': '#ef4444', 'icone': 'heart-pulse'},
    {'nome': 'Educação', 'cor': '#3b82f6', 'icone': 'graduation-cap'},
    {'nome': 'Zeladoria', 'cor': '#f59e0b', 'icone': 'wrench'},
    {'nome': 'Transporte', 'cor': '#8b5cf6', 'icone': 'bus'},
    {'nome': 'Assistência Social', 'cor': '#10b981', 'icone': 'users'},
    {'nome': 'Segurança', 'cor': '#dc2626', 'icone': 'shield'},
]


def seed_macrotemas(apps, schema_editor):
    Macrotema = apps.get_model('atendimentos', 'Macrotema')
    for item in MACROTEMAS:
        Macrotema.objects.get_or_create(nome=item['nome'], defaults=item)


def unseed_macrotemas(apps, schema_editor):
    Macrotema = apps.get_model('atendimentos', 'Macrotema')
    Macrotema.objects.filter(nome__in=[m['nome'] for m in MACROTEMAS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('atendimentos', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_macrotemas, unseed_macrotemas),
    ]
