from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0002_cidadao_avatar_textfield'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='tipo',
            field=models.CharField(
                choices=[
                    ('segmentacao', 'Segmentação do cidadão'),
                    ('contexto', 'Contexto institucional'),
                    ('ambos', 'Segmentação e contexto'),
                ],
                default='ambos',
                max_length=20,
                verbose_name='tipo',
            ),
        ),
        migrations.AddField(
            model_name='cidadao',
            name='marcadores',
            field=models.ManyToManyField(
                blank=True,
                related_name='cidadaos_marcados',
                to='crm.tag',
                verbose_name='marcadores',
            ),
        ),
    ]
