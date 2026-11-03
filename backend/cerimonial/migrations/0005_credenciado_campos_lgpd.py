from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cerimonial', '0004_observacao_logistica_externa'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='credenciado',
            name='cerimonial_cpf_unico_por_evento',
        ),
        migrations.AlterField(
            model_name='credenciado',
            name='cpf',
            field=models.CharField(blank=True, default='', max_length=14, verbose_name='CPF'),
        ),
        migrations.AddField(
            model_name='credenciado',
            name='data_nascimento',
            field=models.DateField(blank=True, null=True, verbose_name='data de nascimento'),
        ),
        migrations.AddField(
            model_name='credenciado',
            name='email',
            field=models.EmailField(blank=True, default='', max_length=254, verbose_name='e-mail'),
        ),
        migrations.AddField(
            model_name='credenciado',
            name='orgao_instituicao',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='órgão / instituição'),
        ),
        migrations.AddConstraint(
            model_name='credenciado',
            constraint=models.UniqueConstraint(
                fields=('evento', 'telefone'),
                name='cerimonial_telefone_unico_por_evento',
            ),
        ),
    ]
