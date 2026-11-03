from django.db import migrations, models

NOMES_CONTEXTO_PROFISSIONAL = frozenset(
    {
        'Cozinheiro',
        'Garçom',
        'Enfermeiro',
        'Auxiliar administrativo',
        'Motorista',
        'Mercado de trabalho',
        'Qualificação e cursos',
    },
)

NOMES_SEGMENTACAO_SERVICOS = frozenset(
    {
        'Assistência social',
        'Saúde e vulnerabilidade',
    },
)


def normalizar_tags(apps, schema_editor):
    Tag = apps.get_model('crm', 'Tag')
    for tag in Tag.objects.all():
        modulos = [m for m in (tag.modulos or []) if m in ('crm', 'atendimentos')]
        if not modulos:
            modulos = ['crm']
        tag.modulos = modulos

        if tag.nome in NOMES_CONTEXTO_PROFISSIONAL:
            tag.tipo = 'contexto_profissional'
        elif tag.nome in NOMES_SEGMENTACAO_SERVICOS:
            tag.tipo = 'segmentacao'
        elif tag.tipo == 'contexto' and tag.nome not in NOMES_CONTEXTO_PROFISSIONAL:
            pass  # mantém contexto institucional
        tag.save(update_fields=['modulos', 'tipo'])


def reverter(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0007_documentoanexo_etiquetas'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='tipo',
            field=models.CharField(
                choices=[
                    ('segmentacao', 'Segmentação do cidadão'),
                    ('contexto', 'Contexto institucional'),
                    ('contexto_profissional', 'Contexto profissional'),
                    ('ambos', 'Segmentação e contexto'),
                ],
                default='ambos',
                max_length=24,
                verbose_name='tipo',
            ),
        ),
        migrations.RunPython(normalizar_tags, reverter),
    ]
