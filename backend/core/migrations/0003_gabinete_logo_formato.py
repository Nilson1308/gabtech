from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_gabinete_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='gabinete',
            name='logo_formato',
            field=models.CharField(
                blank=True,
                default='1:1',
                help_text='Proporção da identidade visual: 1:1, 1:3 ou 3:1.',
                max_length=5,
                verbose_name='formato do logo',
            ),
        ),
    ]
