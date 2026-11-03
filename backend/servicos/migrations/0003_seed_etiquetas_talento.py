from django.db import migrations


ETIQUETAS_TALENTO = (
    ('Cozinheiro', '#ea580c'),
    ('Garçom', '#ca8a04'),
    ('Enfermeiro', '#0284c7'),
    ('Auxiliar administrativo', '#6366f1'),
    ('Motorista', '#64748b'),
)


def criar_etiquetas(apps, schema_editor):
    Tag = apps.get_model('crm', 'Tag')
    for nome, cor in ETIQUETAS_TALENTO:
        tag, created = Tag.objects.get_or_create(
            nome=nome,
            defaults={
                'cor': cor,
                'tipo': 'contexto',
                'modulos': ['servicos'],
            },
        )
        if not created:
            modulos = list(tag.modulos or [])
            if 'servicos' not in modulos:
                modulos.append('servicos')
                tag.modulos = modulos
                tag.save(update_fields=['modulos'])


def reverter(apps, schema_editor):
    Tag = apps.get_model('crm', 'Tag')
    nomes = [n for n, _ in ETIQUETAS_TALENTO]
    for tag in Tag.objects.filter(nome__in=nomes):
        modulos = [m for m in (tag.modulos or []) if m != 'servicos']
        if modulos:
            tag.modulos = modulos
            tag.save(update_fields=['modulos'])
        elif tag.modulos == ['servicos']:
            tag.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('servicos', '0002_vagaemprego_etiquetas'),
        ('crm', '0007_documentoanexo_etiquetas'),
    ]

    operations = [
        migrations.RunPython(criar_etiquetas, reverter),
    ]
