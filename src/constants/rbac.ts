/** Codenames alinhados ao backend (usuarios.rbac_seed_data). */
export const PERMS = {
  dashboard: 'view_dashboard_executivo',
  dashboardOperacional: 'view_dashboard_operacional',
  crm: 'ler_crm',
  crmCreate: 'criar_crm',
  crmEdit: 'editar_crm',
  crmDelete: 'excluir_crm',
  crmExport: 'exportar_crm',
  atendimentos: 'ler_atend',
  atendViewAll: 'ver_todos_atend',
  atendCreate: 'criar_atend',
  atendEdit: 'editar_atend',
  atendDelete: 'excluir_atend',
  atendExport: 'exportar_atend',
  atendStatus: 'mudar_status',
  atendReassign: 'reatribuir',
  agenda: 'ler_agenda',
  agendaCreate: 'criar_agenda',
  agendaEdit: 'editar_agenda',
  agendaDelete: 'excluir_agenda',
  docs: 'ler_docs',
  mapa: 'view_mapa',
  /** Acesso ao módulo Serviços (leitura / visão geral). */
  servicos: 'ler_servicos',
  /** Seção Banco de Talentos — CRUD vagas e candidaturas. */
  servicosTalentos: 'gerenciar_talentos',
  /** Seção Assistência Social — itens e entregas. */
  servicosAssistencia: 'gerenciar_assistencia',
  /** Seção Cursos & Capacitação — turmas e inscrições. */
  servicosCursos: 'gerenciar_cursos',
  /** @deprecated use servicosTalentos, servicosAssistencia ou servicosCursos */
  servicosGerenciar: 'gerenciar_talentos',
  eventos: 'ler_eventos',
  eventosWrite: 'criar_eventos',
  convidados: 'gerenciar_convidados',
  credenciamento: 'credenciamento',
  comunicacaoEvento: 'disparar_comunicacao',
  manageProfiles: 'manage_profiles',
  manageUsers: 'manage_users',
  manageTags: 'manage_tags',
  manageMacrotemas: 'manage_macrotemas',
  manageSlaAtend: 'manage_sla_atend',
  manageDocsConfig: 'manage_docs_config',
  manageAgendaCerimonial: 'manage_agenda_cerimonial',
  manageIntegrations: 'manage_integrations',
  manageComunicacao: 'manage_comunicacao',
} as const

/** Qualquer permissão de gestão em alguma seção de Serviços. */
export const SERVICOS_GERENCIAR_ANY = [
  PERMS.servicosTalentos,
  PERMS.servicosAssistencia,
  PERMS.servicosCursos,
] as const

export function hasGerenciamentoServicos(userPermissions: string[]): boolean {
  return SERVICOS_GERENCIAR_ANY.some(p => userPermissions.includes(p))
}

/** Qualquer permissão de seção em Configurações → Sistema. */
export const CONFIG_SECTION_PERMS = [
  PERMS.manageTags,
  PERMS.manageMacrotemas,
  PERMS.manageSlaAtend,
  PERMS.manageDocsConfig,
  PERMS.manageAgendaCerimonial,
  PERMS.manageIntegrations,
  PERMS.manageComunicacao,
  PERMS.manageUsers,
  PERMS.manageProfiles,
] as const

/**
 * Sinônimos legados (UI antiga em inglês) → codename canônico do backend.
 * hasPermission aceita qualquer entrada deste mapa.
 */
const PERM_CANONICAL: Record<string, string> = {
  create_crm: 'criar_crm',
  update_crm: 'editar_crm',
  delete_crm: 'excluir_crm',
  export_crm: 'exportar_crm',
  create_atendimentos: 'criar_atend',
  create_atendimento: 'criar_atend',
  delete_atendimento: 'excluir_atend',
  export_atendimentos: 'exportar_atend',
  change_status_atendimento: 'mudar_status',
  atribuir_atendimento: 'reatribuir',
  create_agenda: 'criar_agenda',
  delete_agenda: 'excluir_agenda',
}

/** Todas as strings que satisfazem a permissão canônica (para checagem). */
export function expandPermissionCodename(codename: string): string[] {
  const canonical = PERM_CANONICAL[codename] ?? codename
  const legacyKeys = Object.entries(PERM_CANONICAL)
    .filter(([, can]) => can === canonical)
    .map(([legacy]) => legacy)
  return [...new Set([canonical, codename, ...legacyKeys])]
}

export function permissionGranted(userPermissions: string[], required: string): boolean {
  if (!required) return true
  const accepted = expandPermissionCodename(required)
  return accepted.some(p => userPermissions.includes(p))
}
