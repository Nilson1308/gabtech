"""Dados iniciais de tipos e templates (Fábrica de Ofícios)."""

TIPOS_DOCUMENTO = [
    {
        'slug': 'oficio',
        'nome': 'Ofício',
        'descricao': 'Comunicação formal externa',
        'icone': 'file-text',
        'cor': '#3b82f6',
    },
    {
        'slug': 'memorando',
        'nome': 'Memorando',
        'descricao': 'Comunicação interna',
        'icone': 'mail',
        'cor': '#f59e0b',
    },
    {
        'slug': 'requerimento',
        'nome': 'Requerimento',
        'descricao': 'Solicitações formais',
        'icone': 'clipboard-list',
        'cor': '#8b5cf6',
    },
    {
        'slug': 'projeto_lei',
        'nome': 'Projeto de Lei',
        'descricao': 'Proposições legislativas',
        'icone': 'scale',
        'cor': '#10b981',
    },
    {
        'slug': 'ata',
        'nome': 'Ata',
        'descricao': 'Registro de reuniões',
        'icone': 'file-text',
        'cor': '#6366f1',
    },
    {
        'slug': 'declaracao',
        'nome': 'Declaração',
        'descricao': 'Declarações oficiais',
        'icone': 'file-check',
        'cor': '#06b6d4',
    },
    {
        'slug': 'parecer',
        'nome': 'Parecer',
        'descricao': 'Pareceres técnicos',
        'icone': 'file-badge',
        'cor': '#f97316',
    },
    {
        'slug': 'relatorio',
        'nome': 'Relatório',
        'descricao': 'Relatórios gerais',
        'icone': 'file-chart',
        'cor': '#84cc16',
    },
    {
        'slug': 'mocao',
        'nome': 'Moção',
        'descricao': 'Manifestações formais',
        'icone': 'megaphone',
        'cor': '#ec4899',
    },
    {
        'slug': 'indicacao',
        'nome': 'Indicação',
        'descricao': 'Sugestões ao Poder Executivo',
        'icone': 'lightbulb',
        'cor': '#facc15',
    },
    {
        'slug': 'generico',
        'nome': 'Genérico',
        'descricao': 'Documento personalizado',
        'icone': 'file',
        'cor': '#6b7280',
    },
]

_BLOCO_PADRAO = (
    '<div style="font-family: Arial, sans-serif; line-height: 1.6;">'
    '<p style="margin-bottom: 1rem;">[CONTEÚDO DO DOCUMENTO]</p>'
    '</div>'
)

TEMPLATES_PADRAO = [
    {
        'slug_tipo': 'oficio',
        'nome': 'Ofício Padrão',
        'descricao': 'Template padrão para ofícios formais',
        'is_default': True,
        'conteudo': (
            '<div style="font-family: Arial, sans-serif; line-height: 1.6;">'
            '<p style="text-align: right; margin-bottom: 2rem;">'
            '<strong>Ofício nº ___/2026</strong><br/>Brasília-DF, [DATA]</p>'
            '<p style="margin-bottom: 1rem;"><strong>Assunto:</strong> [ASSUNTO]</p>'
            '<p style="text-indent: 2rem; text-align: justify;">[CONTEÚDO DO OFÍCIO]</p>'
            '</div>'
        ),
    },
    {
        'slug_tipo': 'memorando',
        'nome': 'Memorando Padrão',
        'descricao': 'Template padrão para comunicação interna',
        'is_default': True,
        'conteudo': (
            '<div style="font-family: Arial, sans-serif; line-height: 1.6;">'
            '<p style="text-align: center; margin-bottom: 2rem;">'
            '<strong>MEMORANDO INTERNO Nº ___/2026</strong></p>'
            '<p><strong>ASSUNTO:</strong> [ASSUNTO]</p>'
            '<p>[CONTEÚDO DO MEMORANDO]</p>'
            '</div>'
        ),
    },
    {
        'slug_tipo': 'requerimento',
        'nome': 'Requerimento Padrão',
        'descricao': 'Template padrão para requerimentos',
        'is_default': True,
        'conteudo': _BLOCO_PADRAO,
    },
    {
        'slug_tipo': 'projeto_lei',
        'nome': 'Projeto de Lei Padrão',
        'descricao': 'Template padrão para projetos de lei',
        'is_default': True,
        'conteudo': _BLOCO_PADRAO,
    },
    {
        'slug_tipo': 'ata',
        'nome': 'Ata de Reunião',
        'descricao': 'Template para registro de reuniões',
        'is_default': True,
        'conteudo': _BLOCO_PADRAO,
    },
    {
        'slug_tipo': 'declaracao',
        'nome': 'Declaração',
        'descricao': 'Template para declarações oficiais',
        'is_default': True,
        'conteudo': _BLOCO_PADRAO,
    },
    {
        'slug_tipo': 'parecer',
        'nome': 'Parecer Técnico',
        'descricao': 'Template para pareceres técnicos',
        'is_default': True,
        'conteudo': _BLOCO_PADRAO,
    },
    {
        'slug_tipo': 'relatorio',
        'nome': 'Relatório',
        'descricao': 'Template para relatórios gerais',
        'is_default': True,
        'conteudo': _BLOCO_PADRAO,
    },
    {
        'slug_tipo': 'mocao',
        'nome': 'Moção',
        'descricao': 'Template para moções',
        'is_default': True,
        'conteudo': _BLOCO_PADRAO,
    },
    {
        'slug_tipo': 'indicacao',
        'nome': 'Indicação',
        'descricao': 'Template para indicações',
        'is_default': True,
        'conteudo': _BLOCO_PADRAO,
    },
    {
        'slug_tipo': 'generico',
        'nome': 'Documento em Branco',
        'descricao': 'Template vazio para documentos personalizados',
        'is_default': True,
        'conteudo': _BLOCO_PADRAO,
    },
]
