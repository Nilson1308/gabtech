from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0005_tag_modulos'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentoanexo',
            name='categoria',
            field=models.CharField(
                choices=[
                    ('curriculo', 'Currículo'),
                    ('documento_pessoal', 'Documento pessoal'),
                    ('laudo_medico', 'Laudo médico'),
                    ('comprovante_residencia', 'Comprovante de residência'),
                    ('outros', 'Outros'),
                ],
                default='outros',
                max_length=32,
                verbose_name='categoria',
            ),
        ),
    ]
