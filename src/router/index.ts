import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { CONFIG_SECTION_PERMS, PERMS } from '@/constants/rbac'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/evento/:id/credenciamento',
    name: 'CredenciamentoPublico',
    component: () => import('@/views/publico/CredenciamentoView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/evento/logistica/:token',
    name: 'LogisticaPublica',
    component: () => import('@/views/publico/LogisticaPublicaView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/privacidade',
    name: 'Privacidade',
    component: () => import('@/views/publico/PrivacidadeView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/cadastro-gabinete',
    name: 'CadastroGabinete',
    component: () => import('@/views/publico/CadastroGabineteView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/cadastro-gabinete/:id',
    name: 'CadastroGabineteStatus',
    component: () => import('@/views/publico/CadastroGabineteStatusView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: () => import('@/views/LayoutBase.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard',
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/DashboardView.vue'),
        meta: {
          permissionAny: [PERMS.dashboardOperacional, PERMS.dashboard],
          headerTitle: 'Dashboard',
        },
      },
      {
        path: 'desempenho-equipe',
        name: 'DesempenhoEquipe',
        component: () => import('@/views/DesempenhoEquipeView.vue'),
        meta: {
          permissionAny: [PERMS.dashboardOperacional, PERMS.dashboard],
          headerTitle: 'Desempenho da Equipe',
        },
      },
      {
        path: 'crm',
        name: 'CRM',
        component: () => import('@/views/crm/CrmListView.vue'),
        meta: { permission: PERMS.crm, headerTitle: 'Gestão de Cidadãos' },
      },
      {
        path: 'crm/:id',
        name: 'CRMPerfil',
        component: () => import('@/views/crm/CrmPerfilView.vue'),
        meta: { permission: PERMS.crm, headerTitle: 'Perfil do Cidadão' },
      },
      {
        path: 'atendimentos',
        name: 'Atendimentos',
        component: () => import('@/views/atendimentos/AtendimentosView.vue'),
        meta: { permission: PERMS.atendimentos, headerTitle: 'Atendimentos e Protocolos' },
      },
      {
        path: 'servicos',
        component: () => import('@/views/servicos/ServicosLayout.vue'),
        meta: { permission: PERMS.servicos, headerTitle: 'Serviços & Entregas' },
        children: [
          {
            path: '',
            name: 'Servicos',
            component: () => import('@/views/servicos/ServicosDashboardView.vue'),
          },
          {
            path: 'talentos',
            name: 'BancoTalentos',
            component: () => import('@/views/servicos/BancoTalentosView.vue'),
          },
          {
            path: 'beneficios',
            name: 'ServicosBeneficios',
            component: () => import('@/views/servicos/ServicosBeneficiosView.vue'),
          },
          {
            path: 'cursos',
            name: 'ServicosCursos',
            component: () => import('@/views/servicos/ServicosCursosView.vue'),
          },
        ],
      },
      {
        path: 'atendimentos/:id',
        name: 'AtendimentoDetalhes',
        component: () => import('@/views/atendimentos/AtendimentoDetalhesView.vue'),
        meta: { permission: PERMS.atendimentos, headerTitle: 'Detalhes do Atendimento' },
      },
      {
        path: 'configuracoes',
        name: 'Configuracoes',
        component: () => import('@/views/ConfiguracoesView.vue'),
        meta: { permissionAny: [...CONFIG_SECTION_PERMS], headerTitle: 'Configurações' },
      },
      {
        path: 'configuracoes/governanca',
        name: 'Governanca',
        component: () => import('@/views/configuracoes/GovernancaView.vue'),
        meta: { permission: PERMS.manageProfiles, headerTitle: 'Governança' },
      },
      {
        path: 'agenda',
        name: 'Agenda',
        component: () => import('@/views/agenda/AgendaView.vue'),
        meta: { permission: PERMS.agenda, headerTitle: 'Agenda e Calendário' },
      },
      {
        path: 'agenda/tipos',
        name: 'TiposEvento',
        component: () => import('@/views/agenda/TiposEventoView.vue'),
        meta: { permission: PERMS.manageProfiles, headerTitle: 'Agenda e Calendário' },
      },
      {
        path: 'agenda/espacos',
        name: 'Espacos',
        component: () => import('@/views/agenda/EspacosView.vue'),
        meta: { permission: PERMS.manageProfiles, headerTitle: 'Agenda e Calendário' },
      },
      {
        path: 'agenda/integracoes',
        name: 'Integracoes',
        component: () => import('@/views/agenda/IntegracoesView.vue'),
        meta: { permission: PERMS.manageProfiles, headerTitle: 'Agenda e Calendário' },
      },
      {
        path: 'documentos',
        name: 'Documentos',
        component: () => import('@/views/documentos/DocumentosListView.vue'),
        meta: { permission: PERMS.docs, headerTitle: 'Gestão de Documentos' },
      },
      {
        path: 'documentos/editor/:id',
        name: 'DocumentoEditor',
        component: () => import('@/views/documentos/DocumentoEditorView.vue'),
        meta: { permission: PERMS.docs, headerTitle: 'Editor de Documentos' },
      },
      {
        path: 'documentos/templates',
        name: 'Templates',
        component: () => import('@/views/documentos/TemplatesView.vue'),
        meta: { permission: PERMS.docs, headerTitle: 'Gestão de Templates' },
      },
      {
        path: 'documentos/configuracoes',
        name: 'ConfiguracoesDocumentos',
        component: () => import('@/views/documentos/ConfiguracoesDocumentosView.vue'),
        meta: { permission: PERMS.manageProfiles, headerTitle: 'Configurações de Documentos' },
      },
      {
        path: 'eventos',
        name: 'EventosList',
        component: () => import('@/views/cerimonial/EventosListView.vue'),
        meta: { permission: PERMS.eventos, headerTitle: 'Eventos & Cerimonial' },
      },
      {
        path: 'eventos/:id',
        name: 'EventoDashboard',
        component: () => import('@/views/cerimonial/EventoDashboardView.vue'),
        meta: { permission: PERMS.eventos, headerTitle: 'Dashboard do Evento' },
      },
      {
        path: 'perfil',
        name: 'MeuPerfil',
        component: () => import('@/views/MeuPerfilView.vue'),
        meta: { headerTitle: 'Meu Perfil' },
      },
      {
        path: 'mapa',
        name: 'Mapa',
        component: () => import('@/views/mapa/MapaView.vue'),
        meta: { permission: PERMS.mapa, headerTitle: 'Mapa' },
      },
      {
        path: 'sobre',
        name: 'Sobre',
        component: () => import('@/views/SobreView.vue'),
        meta: { headerTitle: 'Sobre o GabTech' },
      },
      {
        path: 'manual',
        name: 'Manual',
        component: () => import('@/views/ManualView.vue'),
        meta: { headerTitle: 'Manual do Usuário' },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue'),
  },
]

const layoutChildRoutes = routes.find(r => r.path === '/')?.children ?? []

function flattenNamedRoutes(records: RouteRecordRaw[]): RouteRecordRaw[] {
  const out: RouteRecordRaw[] = []
  for (const record of records) {
    if (record.name) out.push(record)
    if (record.children?.length) out.push(...flattenNamedRoutes(record.children))
  }
  return out
}

const allLayoutNamedRoutes = flattenNamedRoutes(layoutChildRoutes)

function routeRequiredPermissions(routeName: string | symbol | undefined): string[] {
  if (!routeName || typeof routeName !== 'string') return []
  const record = allLayoutNamedRoutes.find(r => r.name === routeName)
  const parent = layoutChildRoutes.find(r => r.children?.some(c => c.name === routeName))
  let meta = record?.meta ?? {}
  const hasPerm = meta.permission || (meta.permissionAny as string[] | undefined)?.length
  if (!hasPerm && parent?.meta) {
    meta = parent.meta
  }
  const any = meta.permissionAny as string[] | undefined
  if (any?.length) return any
  const single = meta.permission as string | undefined
  return single ? [single] : []
}

function canAccessRoute(
  routeName: string,
  hasPermission: (codename: string) => boolean,
): boolean {
  const permissions = routeRequiredPermissions(routeName)
  if (permissions.length === 0) return true
  return permissions.some(p => hasPermission(p))
}

/** Primeira rota do layout que o usuário pode abrir (ordem do menu). */
function firstAccessibleRouteName(hasPermission: (codename: string) => boolean): string {
  const priority = [
    'Dashboard',
    'CRM',
    'Atendimentos',
    'Servicos',
    'BancoTalentos',
    'Agenda',
    'Documentos',
    'EventosList',
    'Mapa',
    'Configuracoes',
    'MeuPerfil',
    'Sobre',
    'Manual',
  ] as const

  for (const name of priority) {
    if (canAccessRoute(name, hasPermission)) {
      return name
    }
  }
  return 'MeuPerfil'
}

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const authStore = useAuthStore()
  const checkPerm = (codename: string) => authStore.hasPermission(codename)
  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth && !authStore.isAuthenticated) {
    return { name: 'Login', query: { redirect: to.fullPath } }
  }

  if (to.name === 'Login' && authStore.isAuthenticated) {
    return { name: firstAccessibleRouteName(checkPerm) }
  }

  const permissionAny = to.meta.permissionAny as string[] | undefined
  const permission = to.meta.permission as string | undefined
  const required = permissionAny?.length ? permissionAny : permission ? [permission] : []
  if (required.length > 0 && !required.some(p => checkPerm(p))) {
    const fallbackName = firstAccessibleRouteName(checkPerm)
    if (to.name !== fallbackName) {
      return { name: fallbackName }
    }
  }
})

export default router
