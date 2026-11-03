import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ApiError, apiFetch } from '@/services/api'
import { mapRastreabilidade, type RastreabilidadeApi } from '@/utils/rastreabilidade'

// ==================== TIPOS ====================
export interface Perfil {
  id: string
  nome: string
  cor: string
  icone?: string
  descricao?: string
  isAdmin: boolean
  permissoes: string[]
  createdAt: string
  rastreabilidade?: import('@/utils/rastreabilidade').Rastreabilidade | null
}

export interface Permissao {
  id: string
  nome: string
  descricao: string
  modulo: string
}

export interface ModuloPermissoes {
  id: string
  nome: string
  icone: string
  cor: string
  permissoes: Permissao[]
}

// ==================== STORE ====================
export const useGovernancaStore = defineStore('governanca', () => {
  // State
  const perfis = ref<Perfil[]>([])
  const modulos = ref<ModuloPermissoes[]>([])
  const loading = ref(false)

  // ==================== MOCK DATA ====================
  
  // Módulos e Permissões do Sistema
  const modulosDisponiveis: ModuloPermissoes[] = [
    {
      id: 'crm',
      nome: 'CRM (Cidadãos)',
      icone: 'users',
      cor: '#10b981',
      permissoes: [
        { id: 'ler_crm', nome: 'Visualizar Cidadãos', descricao: 'Ver lista e perfis de cidadãos', modulo: 'crm' },
        { id: 'criar_crm', nome: 'Criar Cidadão', descricao: 'Cadastrar novos cidadãos', modulo: 'crm' },
        { id: 'editar_crm', nome: 'Editar Cidadão', descricao: 'Modificar dados de cidadãos', modulo: 'crm' },
        { id: 'excluir_crm', nome: 'Excluir Cidadão', descricao: 'Remover cidadãos do sistema', modulo: 'crm' },
        { id: 'exportar_crm', nome: 'Exportar CSV', descricao: 'Exportar dados de cidadãos', modulo: 'crm' },
      ]
    },
    {
      id: 'atendimentos',
      nome: 'Atendimentos',
      icone: 'inbox',
      cor: '#3b82f6',
      permissoes: [
        { id: 'ler_atend', nome: 'Visualizar Atendimentos', descricao: 'Acessar protocolos (escopo conforme «Ver todos»)', modulo: 'atendimentos' },
        { id: 'ver_todos_atend', nome: 'Ver Todos os Atendimentos', descricao: 'Ver protocolos de toda a equipe; sem ela, só os atribuídos a si', modulo: 'atendimentos' },
        { id: 'criar_atend', nome: 'Criar Atendimento', descricao: 'Registrar novos protocolos', modulo: 'atendimentos' },
        { id: 'editar_atend', nome: 'Editar Atendimento', descricao: 'Modificar dados do protocolo', modulo: 'atendimentos' },
        { id: 'mudar_status', nome: 'Mudar Status', descricao: 'Alterar status do atendimento', modulo: 'atendimentos' },
        { id: 'reatribuir', nome: 'Reatribuir Atendimento', descricao: 'Transferir responsável', modulo: 'atendimentos' },
        { id: 'excluir_atend', nome: 'Excluir Atendimento', descricao: 'Remover protocolos (apenas status aberto)', modulo: 'atendimentos' },
        { id: 'exportar_atend', nome: 'Exportar Relatório CSV', descricao: 'Baixar relatório CSV de atendimentos', modulo: 'atendimentos' },
      ]
    },
    {
      id: 'agenda',
      nome: 'Agenda',
      icone: 'calendar',
      cor: '#8b5cf6',
      permissoes: [
        { id: 'ler_agenda', nome: 'Visualizar Agenda', descricao: 'Ver compromissos e eventos', modulo: 'agenda' },
        { id: 'criar_agenda', nome: 'Criar Compromisso', descricao: 'Agendar novos eventos', modulo: 'agenda' },
        { id: 'editar_agenda', nome: 'Editar Compromisso', descricao: 'Modificar eventos existentes', modulo: 'agenda' },
        { id: 'excluir_agenda', nome: 'Excluir Compromisso', descricao: 'Remover eventos da agenda', modulo: 'agenda' },
      ]
    },
    {
      id: 'eventos',
      nome: 'Eventos & Cerimonial',
      icone: 'users',
      cor: '#ec4899',
      permissoes: [
        { id: 'ler_eventos', nome: 'Visualizar Eventos', descricao: 'Ver eventos e cerimonial', modulo: 'eventos' },
        { id: 'criar_eventos', nome: 'Criar Evento', descricao: 'Criar novos eventos', modulo: 'eventos' },
        { id: 'gerenciar_convidados', nome: 'Gerenciar Convidados', descricao: 'Adicionar/editar lista de convidados', modulo: 'eventos' },
        { id: 'credenciamento', nome: 'Credenciamento', descricao: 'Realizar check-in de convidados', modulo: 'eventos' },
        { id: 'disparar_comunicacao', nome: 'Disparar Comunicação', descricao: 'Enviar convites e lembretes', modulo: 'eventos' },
      ]
    },
    {
      id: 'documentos',
      nome: 'Documentos',
      icone: 'file-text',
      cor: '#f97316',
      permissoes: [
        { id: 'ler_docs', nome: 'Visualizar Documentos', descricao: 'Ver lista e conteúdo de documentos', modulo: 'documentos' },
        { id: 'criar_docs', nome: 'Criar Documento', descricao: 'Criar novos ofícios e documentos', modulo: 'documentos' },
        { id: 'editar_docs', nome: 'Editar Documento', descricao: 'Modificar documentos existentes', modulo: 'documentos' },
        { id: 'sign_docs', nome: 'Assinar Documento', descricao: 'Assinar e finalizar documentos', modulo: 'documentos' },
        { id: 'excluir_docs', nome: 'Excluir Documento', descricao: 'Remover documentos do sistema', modulo: 'documentos' },
      ]
    },
    {
      id: 'servicos',
      nome: 'Serviços & Entregas',
      icone: 'briefcase',
      cor: '#6366f1',
      permissoes: [
        {
          id: 'ler_servicos',
          nome: 'Visualizar Serviços',
          descricao: 'Visão geral, consultas e sugestões inteligentes em todas as seções',
          modulo: 'servicos',
        },
        {
          id: 'gerenciar_talentos',
          nome: 'Gerenciar Banco de Talentos',
          descricao: 'Seção Talentos — vagas, candidaturas e pipeline seletivo',
          modulo: 'servicos',
        },
        {
          id: 'gerenciar_assistencia',
          nome: 'Gerenciar Assistência Social',
          descricao: 'Seção Assistência — itens de benefício e entregas',
          modulo: 'servicos',
        },
        {
          id: 'gerenciar_cursos',
          nome: 'Gerenciar Cursos & Capacitação',
          descricao: 'Seção Cursos — turmas, inscrições e lista de espera',
          modulo: 'servicos',
        },
      ],
    },
    {
      id: 'analytics',
      nome: 'Analytics & Inteligência',
      icone: 'bar-chart',
      cor: '#0ea5e9',
      permissoes: [
        {
          id: 'view_dashboard_operacional',
          nome: 'Dashboard Operacional',
          descricao: 'Painel operacional; escopo de protocolos conforme «Ver todos os atendimentos»',
          modulo: 'analytics',
        },
        { id: 'view_dashboard_executivo', nome: 'Dashboard Executivo', descricao: 'Acessar visão executiva e métricas de gestão', modulo: 'analytics' },
        { id: 'view_mapa', nome: 'Inteligência Territorial', descricao: 'Acessar mapa georreferenciado e análise territorial', modulo: 'analytics' },
      ]
    },
    {
      id: 'sistema',
      nome: 'Sistema & Configurações',
      icone: 'settings',
      cor: '#6b7280',
      permissoes: [
        { id: 'manage_tags', nome: 'Classificações (Tags)', descricao: 'Configurações → Classificações e etiquetas', modulo: 'sistema' },
        { id: 'manage_macrotemas', nome: 'Macrotemas', descricao: 'Configurações → categorias de atendimento', modulo: 'sistema' },
        { id: 'manage_sla_atend', nome: 'SLA de Atendimentos', descricao: 'Configurações → prazos por prioridade', modulo: 'sistema' },
        { id: 'manage_docs_config', nome: 'Documentos (Configuração)', descricao: 'Configurações → pastas e tipos', modulo: 'sistema' },
        { id: 'manage_agenda_cerimonial', nome: 'Agenda & Cerimonial (Configuração)', descricao: 'Configurações → espaços e tipos de evento', modulo: 'sistema' },
        { id: 'manage_integrations', nome: 'Integrações', descricao: 'Configurações → calendário e conectores', modulo: 'sistema' },
        { id: 'manage_comunicacao', nome: 'Comunicação', descricao: 'Configurações → Email, WhatsApp e SMS', modulo: 'sistema' },
        { id: 'manage_users', nome: 'Usuários e Equipe', descricao: 'Configurações → gestão de acessos', modulo: 'sistema' },
        { id: 'manage_profiles', nome: 'Governança e Perfis (RBAC)', descricao: 'Configurações → matriz RBAC', modulo: 'sistema' },
      ]
    }
  ]

  // Perfis Padrão do Sistema
  const perfisIniciais: Perfil[] = [
    {
      id: 'admin',
      nome: 'Administrador',
      cor: '#dc2626',
      icone: 'shield-check',
      descricao: 'Acesso total ao sistema',
      isAdmin: true,
      permissoes: [
        // Tem TODAS as permissões
        'ler_crm', 'criar_crm', 'editar_crm', 'excluir_crm', 'exportar_crm',
        'ler_atend', 'ver_todos_atend', 'criar_atend', 'editar_atend', 'mudar_status', 'reatribuir', 'excluir_atend', 'exportar_atend',
        'ler_agenda', 'criar_agenda', 'editar_agenda', 'excluir_agenda',
        'ler_eventos', 'criar_eventos', 'gerenciar_convidados', 'credenciamento', 'disparar_comunicacao',
        'ler_docs', 'criar_docs', 'editar_docs', 'sign_docs', 'excluir_docs',
        'ler_servicos', 'gerenciar_talentos', 'gerenciar_assistencia', 'gerenciar_cursos',
        'view_dashboard_operacional', 'view_dashboard_executivo', 'view_mapa',
        'manage_tags', 'manage_macrotemas', 'manage_sla_atend', 'manage_docs_config',
        'manage_agenda_cerimonial', 'manage_integrations', 'manage_comunicacao',
        'manage_users', 'manage_profiles',
      ],
      createdAt: new Date().toISOString()
    },
    {
      id: 'chefe',
      nome: 'Chefe de Gabinete',
      cor: '#f59e0b',
      icone: 'user-check',
      descricao: 'Gerenciamento completo exceto configurações de sistema',
      isAdmin: false,
      permissoes: [
        'ler_crm', 'criar_crm', 'editar_crm', 'exportar_crm',
        'ler_atend', 'ver_todos_atend', 'criar_atend', 'editar_atend', 'mudar_status', 'reatribuir', 'excluir_atend', 'exportar_atend',
        'ler_agenda', 'criar_agenda', 'editar_agenda', 'excluir_agenda',
        'ler_eventos', 'criar_eventos', 'gerenciar_convidados', 'disparar_comunicacao',
        'ler_docs', 'criar_docs', 'editar_docs', 'sign_docs',
        'ler_servicos', 'gerenciar_talentos', 'gerenciar_assistencia', 'gerenciar_cursos',
        'view_dashboard_operacional', 'view_dashboard_executivo', 'view_mapa',
        'manage_tags'
      ],
      createdAt: new Date().toISOString()
    },
    {
      id: 'assessor',
      nome: 'Assessor Parlamentar',
      cor: '#3b82f6',
      icone: 'user',
      descricao: 'Operação de atendimentos e CRM',
      isAdmin: false,
      permissoes: [
        'ler_crm', 'criar_crm', 'editar_crm',
        'ler_atend', 'criar_atend', 'editar_atend', 'mudar_status',
        'ler_agenda', 'criar_agenda',
        'ler_eventos', 'criar_eventos', 'gerenciar_convidados',
        'ler_docs', 'criar_docs', 'editar_docs',
        'ler_servicos',
        'view_dashboard_operacional',
      ],
      createdAt: new Date().toISOString()
    },
    {
      id: 'recepcao',
      nome: 'Recepção',
      cor: '#10b981',
      icone: 'user-plus',
      descricao: 'Cadastro de cidadãos e registro de atendimentos',
      isAdmin: false,
      permissoes: [
        'ler_crm', 'criar_crm',
        'ler_atend', 'ver_todos_atend', 'criar_atend',
        'ler_agenda', 'ler_eventos',
        'view_dashboard_operacional',
      ],
      createdAt: new Date().toISOString()
    }
  ]

  // ==================== COMPUTED ====================
  
  // Todas as permissões do sistema (flat)
  const todasPermissoes = computed(() => {
    return modulos.value.flatMap(m => m.permissoes)
  })

  // ==================== ACTIONS ====================
  
  interface PerfilApi {
    id: number
    nome: string
    cor: string
    icone?: string
    descricao?: string
    is_admin: boolean
    permissoes: string[]
    created_at: string
    rastreabilidade?: RastreabilidadeApi
  }

  function mapPerfilFromApi(item: PerfilApi): Perfil {
    const permissoes = Array.isArray(item.permissoes) ? [...item.permissoes] : []
    return {
      id: String(item.id),
      nome: item.nome,
      cor: item.cor || '#3b82f6',
      icone: item.icone,
      descricao: item.descricao,
      isAdmin: item.is_admin,
      permissoes,
      createdAt: item.created_at,
      rastreabilidade: mapRastreabilidade(item.rastreabilidade),
    }
  }

  async function fetchPerfis() {
    loading.value = true
    try {
      const data = await apiFetch<PerfilApi[]>('/api/perfis/')
      perfis.value = data.map(mapPerfilFromApi)
    } catch (err) {
      if (err instanceof ApiError && err.status === 403) {
        perfis.value = perfisIniciais
        return
      }
      throw err
    } finally {
      loading.value = false
    }
  }

  // Inicializar dados mock (módulos/permissões locais; perfis vêm da API quando possível)
  async function initialize() {
    loading.value = true
    modulos.value = modulosDisponiveis
    try {
      await fetchPerfis()
    } catch {
      perfis.value = perfisIniciais
    }
    loading.value = false
  }

  // ==================== CRUD DE PERFIS ====================
  
  function patchPerfilApi(id: string, body: Record<string, unknown>) {
    return apiFetch<PerfilApi>(`/api/perfis/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify(body),
    })
  }

  function applyPerfilFromApi(id: string, item: PerfilApi) {
    const mapped = mapPerfilFromApi(item)
    const index = perfis.value.findIndex(p => p.id === id)
    if (index >= 0) {
      perfis.value[index] = mapped
    }
    return mapped
  }

  async function createPerfil(data: { nome: string; cor: string; icone?: string; descricao?: string }) {
    loading.value = true
    try {
      const created = await apiFetch<PerfilApi>('/api/perfis/', {
        method: 'POST',
        body: JSON.stringify({
          nome: data.nome,
          cor: data.cor,
          icone: data.icone ?? '',
          descricao: data.descricao ?? '',
          permissoes: [],
        }),
      })
      const mapped = mapPerfilFromApi(created)
      perfis.value.push(mapped)
      return mapped
    } finally {
      loading.value = false
    }
  }

  async function updatePerfil(
    id: string,
    data: { nome?: string; cor?: string; icone?: string; descricao?: string },
  ) {
    const perfil = perfis.value.find(p => p.id === id)
    if (!perfil || perfil.isAdmin) {
      return false
    }

    loading.value = true
    try {
      const updated = await patchPerfilApi(id, {
        nome: data.nome ?? perfil.nome,
        cor: data.cor ?? perfil.cor,
        icone: data.icone ?? perfil.icone ?? '',
        descricao: data.descricao ?? perfil.descricao ?? '',
        permissoes: perfil.permissoes,
      })
      applyPerfilFromApi(id, updated)
      return true
    } finally {
      loading.value = false
    }
  }

  async function deletePerfil(id: string) {
    const perfil = perfis.value.find(p => p.id === id)
    if (perfil?.isAdmin) {
      throw new Error('Não é possível excluir o perfil de Administrador')
    }

    loading.value = true
    try {
      await apiFetch(`/api/perfis/${id}/`, { method: 'DELETE', parseJson: false })
      const index = perfis.value.findIndex(p => p.id === id)
      if (index > -1) {
        perfis.value.splice(index, 1)
      }
      return true
    } finally {
      loading.value = false
    }
  }

  // ==================== GERENCIAMENTO DE PERMISSÕES ====================
  
  async function togglePermissao(perfilId: string, permissaoId: string) {
    const perfil = perfis.value.find(p => p.id === perfilId)

    if (!perfil || perfil.isAdmin) {
      return false
    }

    if (!Array.isArray(perfil.permissoes)) {
      perfil.permissoes = []
    }

    const anterior = [...perfil.permissoes]
    const index = perfil.permissoes.indexOf(permissaoId)

    if (index > -1) {
      perfil.permissoes.splice(index, 1)
    } else {
      perfil.permissoes.push(permissaoId)
    }

    if (index === -1) {
      const codenamesCatalogo = new Set(todasPermissoes.value.map(p => p.id))
      if (!codenamesCatalogo.has(permissaoId)) {
        throw new ApiError(
          'Esta permissão ainda não existe no tenant. Sincronize o RBAC (seed) no servidor.',
          400,
        )
      }
    }

    try {
      const updated = await patchPerfilApi(perfilId, {
        permissoes: [...new Set(perfil.permissoes)],
      })
      applyPerfilFromApi(perfilId, updated)
      return true
    } catch (err) {
      perfil.permissoes = anterior
      throw err
    }
  }

  // Verificar se perfil tem permissão
  function hasPermissao(perfilId: string, permissaoId: string): boolean {
    const perfil = perfis.value.find(p => p.id === perfilId)
    if (!perfil || !Array.isArray(perfil.permissoes)) {
      return false
    }
    return perfil.permissoes.includes(permissaoId)
  }

  // Definir permissões em massa para um perfil
  async function setPermissoes(perfilId: string, permissoes: string[]) {
    const perfil = perfis.value.find(p => p.id === perfilId)

    if (!perfil || perfil.isAdmin) {
      return false
    }

    const anterior = [...perfil.permissoes]
    perfil.permissoes = permissoes

    try {
      const updated = await patchPerfilApi(perfilId, { permissoes: [...permissoes] })
      applyPerfilFromApi(perfilId, updated)
      return true
    } catch (err) {
      perfil.permissoes = anterior
      throw err
    }
  }

  // ==================== RETURN ====================
  
  return {
    // State
    perfis,
    modulos,
    loading,
    
    // Computed
    todasPermissoes,
    
    // Actions
    initialize,
    fetchPerfis,
    createPerfil,
    updatePerfil,
    deletePerfil,
    togglePermissao,
    hasPermissao,
    setPermissoes,
  }
})
