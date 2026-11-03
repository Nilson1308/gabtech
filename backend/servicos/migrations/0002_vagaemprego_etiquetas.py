from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0007_documentoanexo_etiquetas'),
        ('servicos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vagaemprego',
            name='etiquetas',
            field=models.ManyToManyField(
                blank=True,
                help_text='Candidatos elegíveis devem ter currículo com ao menos uma etiqueta em comum.',
                related_name='vagas_talento',
                to='crm.tag',
                verbose_name='perfil / área da vaga',
            ),
        ),
    ]
