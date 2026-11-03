import django.db.models.deletion
from django.db import migrations, models


def seed_eixo_banco_talentos(apps, schema_editor):
    EixoServico = apps.get_model('servicos', 'EixoServico')
    EixoServico.objects.get_or_create(
        nome='Banco de Talentos',
        defaults={
            'icone': 'users',
            'cor': '#6366f1',
            'ativo': True,
        },
    )


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('crm', '0006_documentoanexo_categoria'),
    ]

    operations = [
        migrations.CreateModel(
            name='EixoServico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=120, verbose_name='nome')),
                ('icone', models.CharField(default='briefcase', max_length=50, verbose_name='ícone')),
                ('cor', models.CharField(default='#6366f1', max_length=7, verbose_name='cor')),
                ('ativo', models.BooleanField(default=True, verbose_name='ativo')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
            ],
            options={
                'verbose_name': 'eixo de serviço',
                'verbose_name_plural': 'eixos de serviço',
                'ordering': ('nome',),
            },
        ),
        migrations.CreateModel(
            name='VagaEmprego',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=255, verbose_name='título')),
                ('empresa_parceira', models.CharField(max_length=255, verbose_name='empresa parceira')),
                ('descricao', models.TextField(blank=True, verbose_name='descrição')),
                ('requisitos', models.TextField(blank=True, verbose_name='requisitos')),
                (
                    'status',
                    models.CharField(
                        choices=[('aberta', 'Aberta'), ('pausada', 'Pausada'), ('preenchida', 'Preenchida')],
                        default='aberta',
                        max_length=20,
                        verbose_name='status',
                    ),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='atualizado em')),
                (
                    'eixo',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='vagas',
                        to='servicos.eixoservico',
                        verbose_name='eixo',
                    ),
                ),
            ],
            options={
                'verbose_name': 'vaga de emprego',
                'verbose_name_plural': 'vagas de emprego',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='CandidaturaTalento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                (
                    'status_processo',
                    models.CharField(
                        choices=[
                            ('triagem', 'Triagem'),
                            ('encaminhado', 'Encaminhado'),
                            ('entrevista', 'Entrevista'),
                            ('contratado', 'Contratado'),
                            ('recusado', 'Recusado'),
                        ],
                        default='triagem',
                        max_length=20,
                        verbose_name='status no processo',
                    ),
                ),
                ('observacoes', models.TextField(blank=True, verbose_name='observações')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='atualizado em')),
                (
                    'candidato',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='candidaturas_talento',
                        to='crm.cidadao',
                        verbose_name='candidato',
                    ),
                ),
                (
                    'vaga',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='candidaturas',
                        to='servicos.vagaemprego',
                        verbose_name='vaga',
                    ),
                ),
            ],
            options={
                'verbose_name': 'candidatura (banco de talentos)',
                'verbose_name_plural': 'candidaturas (banco de talentos)',
                'ordering': ('-updated_at',),
            },
        ),
        migrations.AddConstraint(
            model_name='candidaturatalento',
            constraint=models.UniqueConstraint(
                fields=('vaga', 'candidato'),
                name='servicos_candidatura_vaga_candidato_uniq',
            ),
        ),
        migrations.RunPython(seed_eixo_banco_talentos, migrations.RunPython.noop),
    ]
