import cerimonial.credenciamento_config
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cerimonial', '0005_credenciado_campos_lgpd'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventocerimonial',
            name='credenciamento_config',
            field=models.JSONField(
                blank=True,
                default=cerimonial.credenciamento_config.default_credenciamento_config,
                verbose_name='parâmetros do credenciamento público',
            ),
        ),
    ]
