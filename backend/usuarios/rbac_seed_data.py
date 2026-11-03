"""
Catálogo RBAC alinhado ao mock de governanca.ts (codenames em português).
"""

from __future__ import annotations

from typing import TypedDict


class PermissaoSeed(TypedDict):
    codename: str
    nome: str
    descricao: str


class ModuloSeed(TypedDict):
    codename: str
    nome: str
    icone: str
    cor: str
    permissoes: list[PermissaoSeed]


class PerfilSeed(TypedDict):
    slug: str
    nome: str
    cor: str
    icone: str
    descricao: str
    is_admin: bool
    permissoes: list[str]


MODULOS: list[ModuloSeed] = [
    {
        'codename': 'crm',
        'nome': 'CRM (Cidadãos)',
        'icone': 'users',
        'cor': '#10b981',
        'permissoes': [
            {'codename': 'ler_crm', 'nome': 'Visualizar Cidadãos', 'descricao': 'Ver lista e perfis de cidadãos'},
            {'codename': 'criar_crm', 'nome': 'Criar Cidadão', 'descricao': 'Cadastrar novos cidadãos'},
            {'codename': 'editar_crm', 'nome': 'Editar Cidadão', 'descricao': 'Modificar dados de cidadãos'},
            {'codename': 'excluir_crm', 'nome': 'Excluir Cidadão', 'descricao': 'Remover cidadãos do sistema'},
            {'codename': 'exportar_crm', 'nome': 'Exportar CSV', 'descricao': 'Exportar dados de cidadãos'},
        ],
    },
    {
        'codename': 'atendimentos',
        'nome': 'Atendimentos',
        'icone': 'inbox',
        'cor': '#3b82f6',
        'permissoes': [
            {'codename': 'ler_atend', 'nome': 'Visualizar Atendimentos', 'descricao': 'Acessar protocolos (escopo: todos ou só os atribuídos a si)'},
            {
                'codename': 'ver_todos_atend',
                'nome': 'Ver Todos os Atendimentos',
                'descricao': 'Visualizar protocolos de toda a equipe; sem ela, vê apenas os atribuídos a si como responsável',
            },
            {'codename': 'criar_atend', 'nome': 'Criar Atendimento', 'descricao': 'Registrar novos protocolos'},
            {'codename': 'editar_atend', 'nome': 'Editar Atendimento', 'descricao': 'Modificar dados do protocolo'},
            {'codename': 'mudar_status', 'nome': 'Mudar Status', 'descricao': 'Alterar status do atendimento'},
            {'codename': 'reatribuir', 'nome': 'Reatribuir Atendimento', 'descricao': 'Transferir responsável'},
            {'codename': 'excluir_atend', 'nome': 'Excluir Atendimento', 'descricao': 'Remover protocolos (apenas status aberto)'},
            {'codename': 'exportar_atend', 'nome': 'Exportar Relatório CSV', 'descricao': 'Baixar relatório CSV de atendimentos visíveis ao perfil'},
        ],
    },
    {
        'codename': 'agenda',
        'nome': 'Agenda',
        'icone': 'calendar',
        'cor': '#8b5cf6',
        'permissoes': [
            {'codename': 'ler_agenda', 'nome': 'Visualizar Agenda', 'descricao': 'Ver compromissos e eventos'},
            {'codename': 'criar_agenda', 'nome': 'Criar Compromisso', 'descricao': 'Agendar novos eventos'},
            {'codename': 'editar_agenda', 'nome': 'Editar Compromisso', 'descricao': 'Modificar eventos existentes'},
            {'codename': 'excluir_agenda', 'nome': 'Excluir Compromisso', 'descricao': 'Remover eventos da agenda'},
        ],
    },
    {
        'codename': 'eventos',
        'nome': 'Eventos & Cerimonial',
        'icone': 'users',
        'cor': '#ec4899',
        'permissoes': [
            {'codename': 'ler_eventos', 'nome': 'Visualizar Eventos', 'descricao': 'Ver eventos e cerimonial'},
            {'codename': 'criar_eventos', 'nome': 'Criar Evento', 'descricao': 'Criar novos eventos'},
            {'codename': 'gerenciar_convidados', 'nome': 'Gerenciar Convidados', 'descricao': 'Adicionar/editar lista de convidados'},
            {'codename': 'credenciamento', 'nome': 'Credenciamento', 'descricao': 'Realizar check-in de convidados'},
            {'codename': 'disparar_comunicacao', 'nome': 'Disparar Comunicação', 'descricao': 'Enviar convites e lembretes'},
        ],
    },
    {
        'codename': 'documentos',
        'nome': 'Documentos',
        'icone': 'file-text',
        'cor': '#f97316',
        'permissoes': [
            {'codename': 'ler_docs', 'nome': 'Visualizar Documentos', 'descricao': 'Ver lista e conteúdo de documentos'},
            {'codename': 'criar_docs', 'nome': 'Criar Documento', 'descricao': 'Criar novos ofícios e documentos'},
            {'codename': 'editar_docs', 'nome': 'Editar Documento', 'descricao': 'Modificar documentos existentes'},
            {'codename': 'sign_docs', 'nome': 'Assinar Documento', 'descricao': 'Assinar e finalizar documentos'},
            {'codename': 'excluir_docs', 'nome': 'Excluir Documento', 'descricao': 'Remover documentos do sistema'},
        ],
    },
    {
        'codename': 'servicos',
        'nome': 'Serviços & Entregas',
        'icone': 'briefcase',
        'cor': '#6366f1',
        'permissoes': [
            {
                'codename': 'ler_servicos',
                'nome': 'Visualizar Serviços',
                'descricao': (
                    'Acessar o módulo (visão geral), consultar dados e sugestões '
                    'inteligentes em todas as seções'
                ),
            },
            {
                'codename': 'gerenciar_talentos',
                'nome': 'Gerenciar Banco de Talentos',
                'descricao': 'Vagas, candidaturas, pipeline seletivo e matchmaking de currículos',
            },
            {
                'codename': 'gerenciar_assistencia',
                'nome': 'Gerenciar Assistência Social',
                'descricao': 'Itens de benefício, entregas e registro de público atendido',
            },
            {
                'codename': 'gerenciar_cursos',
                'nome': 'Gerenciar Cursos & Capacitação',
                'descricao': 'Turmas, inscrições, lista de espera e matchmaking de capacitação',
            },
        ],
    },
    {
        'codename': 'analytics',
        'nome': 'Analytics & Inteligência',
        'icone': 'bar-chart',
        'cor': '#0ea5e9',
        'permissoes': [
            {
                'codename': 'view_dashboard_operacional',
                'nome': 'Dashboard Operacional',
                'descricao': (
                    'Acessar painel operacional (métricas de atendimentos). '
                    'Escopo dos protocolos: com «Ver todos os atendimentos» vê a equipe; '
                    'sem ela, só os atribuídos a si'
                ),
            },
            {
                'codename': 'view_dashboard_executivo',
                'nome': 'Dashboard Executivo',
                'descricao': 'Acessar visão executiva e métricas de gestão',
            },
            {
                'codename': 'view_mapa',
                'nome': 'Inteligência Territorial',
                'descricao': 'Acessar mapa georreferenciado e análise territorial',
            },
        ],
    },
    {
        'codename': 'sistema',
        'nome': 'Sistema & Configurações',
        'icone': 'settings',
        'cor': '#6b7280',
        'permissoes': [
            {
                'codename': 'manage_tags',
                'nome': 'Classificações (Tags)',
                'descricao': 'Seção Configurações → Classificações e etiquetas do sistema',
            },
            {
                'codename': 'manage_macrotemas',
                'nome': 'Macrotemas',
                'descricao': 'Seção Configurações → categorias de atendimento',
            },
            {
                'codename': 'manage_sla_atend',
                'nome': 'SLA de Atendimentos',
                'descricao': 'Seção Configurações → prazos por prioridade',
            },
            {
                'codename': 'manage_docs_config',
                'nome': 'Documentos (Configuração)',
                'descricao': 'Seção Configurações → pastas, tipos e estrutura de documentos',
            },
            {
                'codename': 'manage_agenda_cerimonial',
                'nome': 'Agenda & Cerimonial (Configuração)',
                'descricao': 'Seção Configurações → espaços e tipos de evento',
            },
            {
                'codename': 'manage_integrations',
                'nome': 'Integrações',
                'descricao': 'Seção Configurações → calendário (Google/Outlook) e conectores',
            },
            {
                'codename': 'manage_comunicacao',
                'nome': 'Comunicação',
                'descricao': 'Seção Configurações → Email, WhatsApp e SMS',
            },
            {
                'codename': 'manage_users',
                'nome': 'Usuários e Equipe',
                'descricao': 'Seção Configurações → gestão de acessos da equipe',
            },
            {
                'codename': 'manage_profiles',
                'nome': 'Governança e Perfis (RBAC)',
                'descricao': 'Seção Configurações → matriz de permissões por perfil',
            },
        ],
    },
]

ALL_PERMISSION_CODENAMES: list[str] = [
    perm['codename']
    for module in MODULOS
    for perm in module['permissoes']
]

PERFIS: list[PerfilSeed] = [
    {
        'slug': 'admin',
        'nome': 'Administrador',
        'cor': '#dc2626',
        'icone': 'shield-check',
        'descricao': 'Acesso total ao sistema',
        'is_admin': True,
        'permissoes': ALL_PERMISSION_CODENAMES,
    },
    {
        'slug': 'chefe',
        'nome': 'Chefe de Gabinete',
        'cor': '#f59e0b',
        'icone': 'user-check',
        'descricao': 'Gerenciamento completo exceto configurações de sistema',
        'is_admin': False,
        'permissoes': [
            'ler_crm', 'criar_crm', 'editar_crm', 'exportar_crm',
            'ler_atend', 'ver_todos_atend', 'criar_atend', 'editar_atend', 'mudar_status', 'reatribuir', 'excluir_atend', 'exportar_atend',
            'ler_agenda', 'criar_agenda', 'editar_agenda', 'excluir_agenda',
            'ler_eventos', 'criar_eventos', 'gerenciar_convidados', 'disparar_comunicacao',
            'ler_docs', 'criar_docs', 'editar_docs', 'sign_docs',
            'ler_servicos',
            'gerenciar_talentos',
            'gerenciar_assistencia',
            'gerenciar_cursos',
            'view_dashboard_operacional', 'view_dashboard_executivo', 'view_mapa',
            'manage_tags',
        ],
    },
    {
        'slug': 'assessor',
        'nome': 'Assessor Parlamentar',
        'cor': '#3b82f6',
        'icone': 'user',
        'descricao': 'Operação de atendimentos e CRM',
        'is_admin': False,
        'permissoes': [
            'ler_crm', 'criar_crm', 'editar_crm',
            'ler_atend', 'criar_atend', 'editar_atend', 'mudar_status',
            'ler_agenda', 'criar_agenda',
            'ler_eventos', 'criar_eventos', 'gerenciar_convidados',
            'ler_docs', 'criar_docs', 'editar_docs',
            'ler_servicos',
            'view_dashboard_operacional',
        ],
    },
    {
        'slug': 'recepcao',
        'nome': 'Recepção',
        'cor': '#10b981',
        'icone': 'user-plus',
        'descricao': 'Cadastro de cidadãos e registro de atendimentos',
        'is_admin': False,
        'permissoes': [
            'ler_crm', 'criar_crm',
            'ler_atend', 'ver_todos_atend', 'criar_atend',
            'ler_agenda', 'ler_eventos',
            'view_dashboard_operacional',
        ],
    },
]
