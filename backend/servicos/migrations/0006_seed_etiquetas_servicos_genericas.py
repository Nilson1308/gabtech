from django.db import migrations

ETIQUETAS_GENERICAS = (
    ('Mercado de trabalho', '#6366f1', 'contexto'),
    ('Qualificação e cursos', '#7c3aed', 'contexto'),
    ('Assistência social', '#059669', 'contexto'),
    ('Saúde e vulnerabilidade', '#0284c7', 'segmentacao'),
)


def criar(apps, schema_editor):
    Tag = apps.get_model('crm', 'Tag')
    for nome, cor, tipo in ETIQUETAS_GENERICAS:
        tag, created = Tag.objects.get_or_create(
            nome=nome,
            defaults={'cor': cor, 'tipo': tipo, 'modulos': ['servicos']},
        )
        if not created:
            modulos = list(tag.modulos or [])
            if 'servicos' not in modulos:
                modulos.append('servicos')
                tag.modulos = modulos
                tag.save(update_fields=['modulos'])


def reverter(apps, schema_editor):
    Tag = apps.get_model('crm', 'Tag')
    nomes = [n for n, _, _ in ETIQUETAS_GENERICAS]
    Tag.objects.filter(nome__in=nomes, modulos=['servicos']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('servicos', '0005_assistencia_cursos_matchmaking'),
        ('crm', '0007_documentoanexo_etiquetas'),
    ]

    operations = [
        migrations.RunPython(criar, reverter),
    ]
