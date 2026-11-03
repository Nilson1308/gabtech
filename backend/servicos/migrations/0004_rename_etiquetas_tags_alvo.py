from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servicos', '0003_seed_etiquetas_talento'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vagaemprego',
            old_name='etiquetas',
            new_name='tags_alvo',
        ),
    ]
