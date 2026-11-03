import type { CategoriaDocumentoCidadao } from '@/constants/crmDocumentos'
import type { Rastreabilidade } from '@/utils/rastreabilidade'

export type { Rastreabilidade } from '@/utils/rastreabilidade'

// ==================== AUTH ====================
export interface Usuario {
  id: string
  nome: string
  email: string
  avatar?: string
  cargo: string
  tenantId: string
  permissions: string[]
  createdAt: string
}

export interface LoginCredentials {
  email: string
  senha: string
}

export interface AuthState {
  usuario: Usuario | null
  isAuthenticated: boolean
  token: string | null
}

// ==================== CRM ====================
export type ModuloTag = 'crm' | 'atendimentos'

/** Tipos de uso no CRM */
export type TipoTag = 'segmentacao' | 'contexto' | 'contexto_profissional' | 'ambos'

export interface Tag {
  id: string
  nome: string
  cor: string
  tipo: TipoTag
  modulos: ModuloTag[]  // Array de módulos onde a tag está disponível
  rastreabilidade?: Rastreabilidade | null
}

export interface PerfilProfissional {
  id: string
  instituicao: string  // Órgão/Empresa
  cargo: string
  tag_id: string       // Vinculação à tag de contexto (ex: Saúde, Liderança Comunitária)
}

/** Anexo no perfil do cidadão (CRM) */
export interface TagResumo {
  id: string
  nome: string
  cor: string
}

export interface CidadaoDocumento {
  id: string
  nome: string
  categoria: CategoriaDocumentoCidadao
  tipo: string
  tamanho: number
  dataUpload: string
  urlDownload: string
  etiquetas: TagResumo[]
}

export type StatusProcessoTalento =
  | 'triagem'
  | 'encaminhado'
  | 'entrevista'
  | 'contratado'
  | 'recusado'

export type StatusVagaEmprego = 'aberta' | 'pausada' | 'preenchida'

export interface EixoServico {
  id: string
  nome: string
  icone: string
  cor: string
  ativo: boolean
}

export interface VagaEmprego {
  id: string
  eixoId: string
  eixoNome?: string
  titulo: string
  empresaParceira: string
  descricao: string
  requisitos: string
  status: StatusVagaEmprego
  /** Tags de matchmaking (API: tags_alvo) */
  tagsAlvo: TagResumo[]
  tagsAlvoIds: string[]
  /** @deprecated use tagsAlvo — alias legado da API */
  etiquetas: TagResumo[]
  etiquetaIds: string[]
  createdAt: string
  updatedAt: string
  rastreabilidade?: Rastreabilidade | null
}

export interface SugestaoMatchmaking {
  score: number
  tagsCoincidentes: TagResumo[]
  cidadao: {
    id: string
    nome: string
    telefone: string
    email?: string
    bairro?: string
  }
}

export interface ItemBeneficio {
  id: string
  nome: string
  descricao: string
  exigeLaudo: boolean
  tagsAlvo: TagResumo[]
  tagsAlvoIds: string[]
  createdAt: string
  rastreabilidade?: Rastreabilidade | null
}

export interface EntregaBeneficio {
  id: string
  cidadaoId: string
  cidadaoNome?: string
  itemId: string
  itemNome?: string
  dataEntrega: string
  quantidade: number
  createdAt: string
  rastreabilidade?: Rastreabilidade | null
}

export type StatusTurmaCurso = 'aberta' | 'em_andamento' | 'encerrada'
export type StatusInscricaoCurso = 'inscrito' | 'lista_espera' | 'cancelado'

export interface TurmaCurso {
  id: string
  nomeCurso: string
  vagasTotais: number
  vagasOcupadas: number
  status: StatusTurmaCurso
  tagsAlvo: TagResumo[]
  tagsAlvoIds: string[]
  createdAt: string
  rastreabilidade?: Rastreabilidade | null
}

export interface InscricaoCurso {
  id: string
  turmaId: string
  turmaNome?: string
  cidadaoId: string
  cidadaoNome?: string
  status: StatusInscricaoCurso
  createdAt: string
  rastreabilidade?: Rastreabilidade | null
}

export interface CurriculoResumo {
  id: string
  nomeOriginal: string
  urlDownload: string
  createdAt?: string
  etiquetas?: TagResumo[]
}

export interface CandidaturaTalento {
  id: string
  vagaId: string
  vagaTitulo?: string
  candidatoId: string
  candidato: {
    id: string
    nome: string
    telefone: string
    email?: string
    bairro?: string
  }
  statusProcesso: StatusProcessoTalento
  observacoes: string
  curriculo: CurriculoResumo | null
  createdAt: string
  updatedAt: string
  rastreabilidade?: Rastreabilidade | null
}

export interface Cidadao {
  id: string
  nome: string
  nome_social?: string
  cpf?: string
  telefone: string
  email?: string
  avatar?: string
  perfis_profissionais?: PerfilProfissional[]
  /** Marcadores do cidadão (liderança, idoso, PCD…) — independente de perfil profissional */
  tag_ids?: string[]
  endereco?: Endereco
  bairro?: string
  observacoes?: string
  createdAt: string
  updatedAt: string
  rastreabilidade?: Rastreabilidade | null
}

export interface Endereco {
  logradouro: string
  numero: string
  complemento?: string
  bairro: string
  cidade: string
  estado: string
  cep: string
  latitude?: number | null
  longitude?: number | null
}

// ==================== ATENDIMENTOS ====================
export type StatusAtendimento = 'aberto' | 'em_andamento' | 'aguardando_terceiros' | 'concluido'

export interface Macrotema {
  id: string
  nome: string
  cor: string
  icone?: string
  rastreabilidade?: Rastreabilidade | null
}

export interface Atendimento {
  id: string
  protocolo: string
  cidadaoId: string
  cidadao: Cidadao
  perfil_ativo_id?: string  // ID do perfil profissional que está atuando no chamado
  assunto: string
  descricao: string
  macrotema: Macrotema
  tags: Tag[]  // Tags específicas do atendimento (ex: Tapa buraco, Consulta médica)
  status: StatusAtendimento
  responsavelId: string
  responsavel: Usuario
  prioridade: 'baixa' | 'media' | 'alta' | 'urgente'
  slaVencimento: string
  slaHoras?: number
  slaAtrasado: boolean
  despachos: Despacho[]
  anexos: Anexo[]
  createdAt: string
  updatedAt: string
  rastreabilidade?: Rastreabilidade | null
}

export interface Despacho {
  id: string
  atendimentoId: string
  autorId: string
  autor: Usuario
  tipo: 'nota_interna' | 'nota_publica' | 'mudanca_status' | 'reatribuicao'
  conteudo: string
  statusAnterior?: StatusAtendimento
  statusNovo?: StatusAtendimento
  responsavelAnteriorId?: string
  responsavelNovoId?: string
  anexos?: Anexo[]
  createdAt: string
}

export interface Anexo {
  id: string
  nome: string
  url: string
  tipo: string
  tamanho: number
  createdAt: string
}

// ==================== DASHBOARD ====================
export interface MetricaCard {
  label: string
  valor: number | string
  icone: string
  cor: string
  variacao?: {
    valor: number
    tipo: 'aumento' | 'reducao'
  }
}

export interface DadosGraficoMacrotema {
  macrotema: string
  quantidade: number
  cor: string
}

// ==================== DOCUMENTOS ====================
export type TipoDocumento = 'oficio' | 'memorando' | 'requerimento' | 'projeto_lei' | 'ata' | 'declaracao' | 'parecer' | 'relatorio' | 'mocao' | 'indicacao' | 'generico'
export type StatusDocumento = 'rascunho' | 'aguardando_assinatura' | 'finalizado'

export interface PastaDocumento {
  id: string
  nome: string
  icone?: string
  cor?: string
  parentId?: string // Para pastas aninhadas
  createdAt: string
}

export interface EtiquetaDocumento {
  id: string
  nome: string
  cor: string
}

export interface VersaoDocumento {
  id: string
  documentoId: string
  numeroVersao: number
  autorId: string
  autor: Usuario
  mudancas: string
  conteudo: string
  createdAt: string
}

export interface Documento {
  id: string
  titulo: string
  tipo: TipoDocumento
  status: StatusDocumento
  pastaId?: string
  pasta?: PastaDocumento
  conteudo: string // HTML do documento
  autorId: string
  autor: Usuario
  assinantes?: Usuario[] // Usuários que assinaram
  etiquetas: EtiquetaDocumento[]
  versoes: VersaoDocumento[]
  versaoAtual: number
  createdAt: string
  updatedAt: string
  finalizadoAt?: string
  rastreabilidade?: Rastreabilidade | null
}

// ==================== PAGINATION ====================
export interface PaginationMeta {
  currentPage: number
  perPage: number
  totalPages: number
  totalItems: number
}

export interface PaginatedResponse<T> {
  data: T[]
  meta: PaginationMeta
}
