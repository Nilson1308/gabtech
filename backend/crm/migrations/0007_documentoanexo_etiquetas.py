from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0006_documentoanexo_categoria'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentoanexo',
            name='etiquetas',
            field=models.ManyToManyField(
                blank=True,
                help_text='Usado quando a categoria é Currículo — ex.: Cozinheiro, Enfermeiro.',
                related_name='documentos_curriculo',
                to='crm.tag',
                verbose_name='áreas profissionais (currículo)',
            ),
        ),
    ]
