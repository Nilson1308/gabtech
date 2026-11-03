from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plataforma', '0003_cadastrogabinete_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='cadastrogabinete',
            name='logo_formato',
            field=models.CharField(
                blank=True,
                default='1:1',
                max_length=5,
                verbose_name='formato do logo',
            ),
        ),
    ]
