import { apiFetch } from '@/services/api'
import type { UltimaAcaoTipo } from '@/utils/rastreabilidade'

export interface AuditoriaAlvo {
  appLabel: string
  model: string
  objectId: string
}

export interface EventoAuditoriaItem {
  id: number
  acao: UltimaAcaoTipo
  acaoLabel: string
  objectRepr: string
  usuarioId: number | null
  usuarioNome: string | null
  ocorridoEm: string
}

interface HistoricoAuditoriaApi {
  app_label: string
  model: string
  object_id: string
  total: number | null
  eventos: Array<{
    id: number
    acao: UltimaAcaoTipo
    acao_label: string
    object_repr: string
    usuario_id: number | null
    usuario_nome: string | null
    ocorrido_em: string
  }>
}

function mapEvento(item: HistoricoAuditoriaApi['eventos'][number]): EventoAuditoriaItem {
  return {
    id: item.id,
    acao: item.acao,
    acaoLabel: item.acao_label,
    objectRepr: item.object_repr,
    usuarioId: item.usuario_id,
    usuarioNome: item.usuario_nome,
    ocorridoEm: item.ocorrido_em,
  }
}

export async function fetchHistoricoAuditoria(
  alvo: AuditoriaAlvo,
  limit = 100,
): Promise<EventoAuditoriaItem[]> {
  const params = new URLSearchParams({
    app_label: alvo.appLabel,
    model: alvo.model,
    object_id: alvo.objectId,
    limit: String(limit),
  })
  const data = await apiFetch<HistoricoAuditoriaApi>(`/api/auditoria/historico/?${params}`)
  return (data.eventos ?? []).map(mapEvento)
}

/** Referências ContentType usadas no frontend (Django app_label + model). */
export const AUDITORIA_ALVO = {
  cidadao: (id: string): AuditoriaAlvo => ({ appLabel: 'crm', model: 'cidadao', objectId: id }),
  tag: (id: string): AuditoriaAlvo => ({ appLabel: 'crm', model: 'tag', objectId: id }),
  atendimento: (id: string): AuditoriaAlvo => ({
    appLabel: 'atendimentos',
    model: 'atendimento',
    objectId: id,
  }),
  macrotema: (id: string): AuditoriaAlvo => ({
    appLabel: 'atendimentos',
    model: 'macrotema',
    objectId: id,
  }),
  eventoAgenda: (id: string): AuditoriaAlvo => ({ appLabel: 'agenda', model: 'evento', objectId: id }),
  tipoEvento: (id: string): AuditoriaAlvo => ({ appLabel: 'agenda', model: 'tipoevento', objectId: id }),
  espaco: (id: string): AuditoriaAlvo => ({ appLabel: 'agenda', model: 'espaco', objectId: id }),
  documento: (id: string): AuditoriaAlvo => ({
    appLabel: 'documentos',
    model: 'documento',
    objectId: id,
  }),
  eventoCerimonial: (id: string): AuditoriaAlvo => ({
    appLabel: 'cerimonial',
    model: 'eventocerimonial',
    objectId: id,
  }),
  perfil: (id: string): AuditoriaAlvo => ({ appLabel: 'usuarios', model: 'perfil', objectId: id }),
  usuario: (id: string): AuditoriaAlvo => ({ appLabel: 'usuarios', model: 'user', objectId: id }),
  vagaEmprego: (id: string): AuditoriaAlvo => ({
    appLabel: 'servicos',
    model: 'vagaemprego',
    objectId: id,
  }),
  candidatura: (id: string): AuditoriaAlvo => ({
    appLabel: 'servicos',
    model: 'candidaturatalento',
    objectId: id,
  }),
  itemBeneficio: (id: string): AuditoriaAlvo => ({
    appLabel: 'servicos',
    model: 'itembeneficio',
    objectId: id,
  }),
  entregaBeneficio: (id: string): AuditoriaAlvo => ({
    appLabel: 'servicos',
    model: 'entregabeneficio',
    objectId: id,
  }),
  turmaCurso: (id: string): AuditoriaAlvo => ({
    appLabel: 'servicos',
    model: 'turmacurso',
    objectId: id,
  }),
  inscricaoCurso: (id: string): AuditoriaAlvo => ({
    appLabel: 'servicos',
    model: 'inscricaocurso',
    objectId: id,
  }),
} as const
