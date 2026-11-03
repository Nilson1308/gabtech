import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('crm', '0007_documentoanexo_etiquetas'),
        ('servicos', '0004_rename_etiquetas_tags_alvo'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemBeneficio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200, verbose_name='nome')),
                ('descricao', models.TextField(blank=True, verbose_name='descrição')),
                ('exige_laudo', models.BooleanField(default=False, verbose_name='exige laudo médico')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('tags_alvo', models.ManyToManyField(blank=True, related_name='itens_beneficio', to='crm.tag', verbose_name='tags alvo')),
            ],
            options={
                'verbose_name': 'item de benefício',
                'verbose_name_plural': 'itens de benefício',
                'ordering': ('nome',),
            },
        ),
        migrations.CreateModel(
            name='TurmaCurso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_curso', models.CharField(max_length=255, verbose_name='nome do curso')),
                ('vagas_totais', models.PositiveIntegerField(default=20, verbose_name='vagas totais')),
                ('status', models.CharField(choices=[('aberta', 'Aberta'), ('em_andamento', 'Em andamento'), ('encerrada', 'Encerrada')], default='aberta', max_length=20, verbose_name='status')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('tags_alvo', models.ManyToManyField(blank=True, related_name='turmas_curso', to='crm.tag', verbose_name='tags alvo')),
            ],
            options={
                'verbose_name': 'turma de curso',
                'verbose_name_plural': 'turmas de curso',
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='AgendamentoAssessoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_nome', models.CharField(max_length=200, verbose_name='tipo de assessoria')),
                ('tipo_descricao', models.TextField(blank=True, verbose_name='descrição do tipo')),
                ('data_agendamento', models.DateTimeField(verbose_name='data/hora do agendamento')),
                ('status', models.CharField(choices=[('agendado', 'Agendado'), ('realizado', 'Realizado'), ('cancelado', 'Cancelado')], default='agendado', max_length=20, verbose_name='status')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('cidadao', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='agendamentos_assessoria', to='crm.cidadao', verbose_name='cidadão')),
                ('especialista_responsavel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assessorias_conduzidas', to=settings.AUTH_USER_MODEL, verbose_name='especialista responsável')),
            ],
            options={
                'verbose_name': 'agendamento de assessoria',
                'verbose_name_plural': 'agendamentos de assessoria',
                'ordering': ('-data_agendamento',),
            },
        ),
        migrations.CreateModel(
            name='EntregaBeneficio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_entrega', models.DateField(verbose_name='data da entrega')),
                ('quantidade', models.PositiveIntegerField(default=1, verbose_name='quantidade')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='registrado em')),
                ('cidadao', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='entregas_beneficio', to='crm.cidadao', verbose_name='cidadão')),
                ('entregue_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='entregas_beneficio_registradas', to=settings.AUTH_USER_MODEL, verbose_name='entregue por')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='entregas', to='servicos.itembeneficio', verbose_name='item')),
            ],
            options={
                'verbose_name': 'entrega de benefício',
                'verbose_name_plural': 'entregas de benefício',
                'ordering': ('-data_entrega', '-id'),
            },
        ),
        migrations.CreateModel(
            name='InscricaoCurso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('inscrito', 'Inscrito'), ('lista_espera', 'Lista de espera'), ('cancelado', 'Cancelado')], default='inscrito', max_length=20, verbose_name='status')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='inscrito em')),
                ('cidadao', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='inscricoes_curso', to='crm.cidadao', verbose_name='cidadão')),
                ('turma', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inscricoes', to='servicos.turmacurso', verbose_name='turma')),
            ],
            options={
                'verbose_name': 'inscrição em curso',
                'verbose_name_plural': 'inscrições em curso',
                'ordering': ('-created_at',),
            },
        ),
        migrations.AddConstraint(
            model_name='inscricaocurso',
            constraint=models.UniqueConstraint(fields=('turma', 'cidadao'), name='servicos_inscricao_turma_cidadao_uniq'),
        ),
    ]
