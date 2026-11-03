import crm.models
from django.db import migrations, models


def preencher_modulos_crm(apps, schema_editor):
    Tag = apps.get_model('crm', 'Tag')
    for tag in Tag.objects.all():
        if not tag.modulos:
            tag.modulos = ['crm']
            tag.save(update_fields=['modulos'])


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0004_documentoanexo'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='modulos',
            field=models.JSONField(
                default=crm.models.default_tag_modulos,
                help_text='Onde a tag aparece: crm, atendimentos (ou ambos).',
                verbose_name='módulos',
            ),
        ),
        migrations.RunPython(preencher_modulos_crm, migrations.RunPython.noop),
    ]
