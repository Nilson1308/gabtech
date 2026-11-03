from django.db import migrations


def seed_catalogo(apps, schema_editor):
    TipoDocumento = apps.get_model('documentos', 'TipoDocumento')
    TemplateDocumento = apps.get_model('documentos', 'TemplateDocumento')

    from documentos.seed_data import TEMPLATES_PADRAO, TIPOS_DOCUMENTO

    tipo_por_slug = {}
    for item in TIPOS_DOCUMENTO:
        tipo, _ = TipoDocumento.objects.update_or_create(
            slug=item['slug'],
            defaults={
                'nome': item['nome'],
                'descricao': item['descricao'],
                'icone': item['icone'],
                'cor': item['cor'],
                'is_sistema': True,
            },
        )
        tipo_por_slug[item['slug']] = tipo

    for tpl in TEMPLATES_PADRAO:
        tipo = tipo_por_slug[tpl['slug_tipo']]
        TemplateDocumento.objects.update_or_create(
            tipo_documento=tipo,
            nome=tpl['nome'],
            defaults={
                'descricao': tpl['descricao'],
                'conteudo': tpl['conteudo'],
                'is_default': tpl['is_default'],
            },
        )


def unseed_catalogo(apps, schema_editor):
    TipoDocumento = apps.get_model('documentos', 'TipoDocumento')
    TipoDocumento.objects.filter(is_sistema=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('documentos', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_catalogo, unseed_catalogo),
    ]
