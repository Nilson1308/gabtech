from django.db import migrations

ITENS = [
    ('infraestrutura', 'Verificar ar-condicionado'),
    ('infraestrutura', 'Preparar mesa de honra'),
    ('infraestrutura', 'Organizar cadeiras no plenário'),
    ('infraestrutura', 'Instalar painel decorativo'),
    ('buffet', 'Contratar buffet'),
    ('buffet', 'Solicitar bebidas (água, refrigerante, café)'),
    ('buffet', 'Confirmar horário de montagem'),
    ('cerimonial', 'Elaborar roteiro da cerimônia'),
    ('cerimonial', 'Confeccionar diplomas/certificados'),
    ('cerimonial', 'Preparar discursos'),
    ('cerimonial', 'Definir ordem de entrada das autoridades'),
    ('comunicacao', 'Enviar convites digitais'),
    ('comunicacao', 'Publicar em redes sociais'),
    ('comunicacao', 'Contratar fotógrafo'),
    ('comunicacao', 'Preparar release para imprensa'),
    ('seguranca', 'Solicitar reforço de segurança'),
    ('seguranca', 'Preparar lista de credenciados'),
    ('tecnologia', 'Testar sistema de som e microfones'),
    ('tecnologia', 'Configurar projetor e telão'),
    ('tecnologia', 'Preparar apresentação em slides'),
]


def seed_itens(apps, schema_editor):
    ItemChecklistPadrao = apps.get_model('cerimonial', 'ItemChecklistPadrao')
    for categoria, descricao in ITENS:
        ItemChecklistPadrao.objects.get_or_create(
            categoria=categoria,
            descricao=descricao,
        )


def unseed_itens(apps, schema_editor):
    ItemChecklistPadrao = apps.get_model('cerimonial', 'ItemChecklistPadrao')
    for categoria, descricao in ITENS:
        ItemChecklistPadrao.objects.filter(categoria=categoria, descricao=descricao).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cerimonial', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_itens, unseed_itens),
    ]
