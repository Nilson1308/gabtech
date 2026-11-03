<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import type { Tag } from '@/types'
import { useRouter, useRoute } from 'vue-router'
import { useCerimonialStore } from '@/stores/cerimonial'
import { useCrmStore } from '@/stores/crm'
import { useAuthStore } from '@/stores/auth'
import { PERMS } from '@/constants/rbac'
import { useAlertDialog } from '@/composables/useAlertDialog'
import type { ItemChecklist } from '@/stores/cerimonial'
import GestaoConvidados from '@/components/cerimonial/GestaoConvidados.vue'
import RastreabilidadeMeta from '@/components/common/RastreabilidadeMeta.vue'
import { AUDITORIA_ALVO } from '@/services/auditoria'
import CredenciamentoPainel from '@/components/cerimonial/CredenciamentoPainel.vue'
import {
  ArrowLeft,
  Calendar,
  Clock,
  MapPin,
  Users,
  CheckCircle2,
  ClipboardList,
  UserCheck,
  QrCode,
  Info,
  Plus,
  Printer,
  X,
  Check,
  Trash2,
  Send,
  Mail,
  MessageCircle,
  Smartphone,
  Tag as TagIcon,
  Eye,
  Upload,
  Image as ImageIcon
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const cerimonialStore = useCerimonialStore()
const crmStore = useCrmStore()
const authStore = useAuthStore()
const { showSuccess, showError, showConfirm } = useAlertDialog()

const eventoId = computed(() => route.params.id as string)
const evento = computed(() => cerimonialStore.getEventoById(eventoId.value))
const abaSelecionada = ref<'geral' | 'logistica' | 'convidados' | 'credenciamento' | 'comunicacao'>('geral')
const itemPadraoSelecionadoId = ref('')
const linkLogisticaCopiado = ref(false)
const mostrarRelatorio = ref(false)
const mostrarFormulario = ref<string | null>(null)

const mostrarGestaoItens = ref(false)

// States para Comunicação
const canalSelecionado = ref<'email' | 'whatsapp' | 'sms'>('email')
const publicoConvidados = ref(true)
const tagsSelecionadas = ref<string[]>([])
const mensagemTexto = ref('')
const tagsCrmProntas = ref(false)
const erroTagsCrm = ref('')
const audienciaTagsTotal = ref(0)
const recalculandoAudienciaTags = ref(false)

// States para Upload de Imagem
const imagemArquivo = ref<File | null>(null)
const imagemPreview = ref<string | null>(null)
const imagemPosicao = ref<'corpo' | 'anexo'>('corpo')

/** Tags do módulo CRM (marcadores, contexto de perfil, currículo, etc.). */
const tagsComunicacao = computed((): Tag[] => {
  return [...crmStore.tagsParaComunicacao()].sort((a, b) =>
    a.nome.localeCompare(b.nome, 'pt-BR'),
  )
})

const audienciaEstimada = computed(() => {
  let total = 0
  if (publicoConvidados.value) {
    total += cerimonialStore.convidadosConfirmados(eventoId.value).length
  }
  total += audienciaTagsTotal.value
  return total
})

watch(
  tagsSelecionadas,
  async nomes => {
    recalculandoAudienciaTags.value = true
    try {
      let sum = 0
      for (const nome of nomes) {
        const tag = crmStore.tagsDisponiveis.find(t => t.nome === nome)
        if (tag) {
          sum += await crmStore.countCidadaosByTagIds([tag.id])
        }
      }
      audienciaTagsTotal.value = sum
    } catch {
      audienciaTagsTotal.value = 0
    } finally {
      recalculandoAudienciaTags.value = false
    }
  },
  { deep: true },
)

const mensagemPreview = computed(() => {
  let preview = mensagemTexto.value
  
  if (!evento.value) return preview
  
  const eventoData = evento.value
  
  preview = preview.replace(/\{\{Nome_Contato\}\}/g, 'João Silva')
  preview = preview.replace(/\{\{Titulo_Evento\}\}/g, eventoData.titulo)
  preview = preview.replace(/\{\{Data_Evento\}\}/g, formatarData(eventoData.data))
  preview = preview.replace(/\{\{Hora_Inicio\}\}/g, eventoData.horaInicio)
  preview = preview.replace(/\{\{Local\}\}/g, eventoData.local)
  preview = preview.replace(/\{\{Link_Credenciamento\}\}/g, `${window.location.origin}/evento/${eventoId.value}/credenciamento`)
  
  return preview
})

const historicoOrdenado = computed(() => {
  if (!evento.value) return []
  return [...evento.value.comunicacoes].sort((a, b) => 
    new Date(b.dataHora).getTime() - new Date(a.dataHora).getTime()
  )
})

/** Formulário ao adicionar item padrão ao evento (somente catálogo). */
const padraoForm = ref({
  responsavel: '',
  prazo: '',
})

/** Formulário do modal “Gerir itens padrão” (cadastro na base). */
const novoItem = ref({
  categoria: 'infraestrutura' as ItemChecklist['categoria'],
  descricao: '',
})

onMounted(async () => {
  try {
    await Promise.all([
      cerimonialStore.fetchChecklistPadrao(),
      cerimonialStore.fetchEventoDashboard(eventoId.value),
    ])
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Não foi possível carregar o evento.'
    showError(message)
  }

  if (!evento.value) {
    router.push('/eventos')
    return
  }

  await carregarTagsComunicacao()
})

async function carregarTagsComunicacao() {
  try {
    await crmStore.fetchTags()
    tagsCrmProntas.value = true
    erroTagsCrm.value = ''
  } catch {
    tagsCrmProntas.value = true
    erroTagsCrm.value = 'Não foi possível carregar as tags do CRM.'
  }
}

watch(abaSelecionada, aba => {
  if (aba === 'comunicacao' && (crmStore.tagsDisponiveis.length === 0 || erroTagsCrm.value)) {
    void carregarTagsComunicacao()
  }
})

const progresso = computed(() => {
  if (!evento.value) return { total: 0, providenciados: 0, percentual: 0 }
  return cerimonialStore.progressoChecklist(eventoId.value)
})

const checklistPorCategoria = computed(() => {
  if (!evento.value) return {}
  return cerimonialStore.checklistPorCategoria(eventoId.value)
})

const categoriasConfig = {
  infraestrutura: {
    nome: 'Infraestrutura',
    cor: '#3b82f6'
  },
  buffet: {
    nome: 'Buffet',
    cor: '#f59e0b'
  },
  cerimonial: {
    nome: 'Cerimonial',
    cor: '#8b5cf6'
  },
  comunicacao: {
    nome: 'Comunicação',
    cor: '#10b981'
  },
  seguranca: {
    nome: 'Segurança',
    cor: '#ef4444'
  },
  tecnologia: {
    nome: 'Tecnologia',
    cor: '#06b6d4'
  }
}

function voltar() {
  router.push('/eventos')
}

// Pode excluir: apenas se tem permissão
const podeExcluir = computed(() => {
  return authStore.hasPermission(PERMS.agendaDelete)
})

async function handleExcluir() {
  if (!evento.value || !podeExcluir.value) return

  const confirmed = await showConfirm(
    `Tem certeza que deseja excluir o evento "${evento.value.titulo}"? Esta ação não pode ser desfeita.`,
    'Excluir Evento'
  )

  if (!confirmed) return

  try {
    await cerimonialStore.excluirEvento(eventoId.value)
    showSuccess('Evento excluído com sucesso!')
    router.push('/eventos')
  } catch (error) {
    showError('Erro ao excluir evento.')
  }
}

function formatarData(data: string) {
  return new Date(data).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  })
}

async function toggleItem(itemId: string) {
  await cerimonialStore.toggleItemChecklist(eventoId.value, itemId)
}

function toggleFormularioCategoria(categoria: string) {
  if (mostrarFormulario.value === categoria) {
    mostrarFormulario.value = null
  } else {
    mostrarFormulario.value = categoria
    itemPadraoSelecionadoId.value = ''
    padraoForm.value = { responsavel: '', prazo: '' }
  }
}

async function adicionarItemPadrao(_categoria: string) {
  if (!itemPadraoSelecionadoId.value) return

  await cerimonialStore.adicionarItemPadraoAoEvento(
    eventoId.value,
    itemPadraoSelecionadoId.value,
    padraoForm.value.responsavel || undefined,
    padraoForm.value.prazo || undefined,
  )

  itemPadraoSelecionadoId.value = ''
  padraoForm.value = { responsavel: '', prazo: '' }
  mostrarFormulario.value = null
  showSuccess('Item adicionado à checklist.')
}

async function removerItem(itemId: string) {
  const ok = await showConfirm('Tem certeza que deseja remover este item?', 'Remover item')
  if (ok) {
    await cerimonialStore.removerItemChecklist(eventoId.value, itemId)
    showSuccess('Item removido.')
  }
}

async function adicionarNovoItemPadrao() {
  if (!novoItem.value.descricao.trim()) return

  await cerimonialStore.adicionarItemPadrao({
    categoria: novoItem.value.categoria as any,
    descricao: novoItem.value.descricao
  })

  // Reset
  novoItem.value.descricao = ''
}

async function removerItemPadraoConfirm(itemId: string) {
  const ok = await showConfirm(
    'Tem certeza que deseja remover este item padrão?',
    'Remover item padrão',
  )
  if (ok) {
    await cerimonialStore.removerItemPadrao(itemId)
    showSuccess('Item padrão removido.')
  }
}

async function ativarLinkLogisticaPublica() {
  try {
    const data = await cerimonialStore.ativarLinkLogistica(eventoId.value)
    await navigator.clipboard.writeText(cerimonialStore.urlLogisticaPublica(data.token))
    linkLogisticaCopiado.value = true
    showSuccess(
      'Novo link gerado e copiado. Após o colaborador enviar a checklist, o link expira até você gerar outro.',
    )
    setTimeout(() => {
      linkLogisticaCopiado.value = false
    }, 3000)
  } catch {
    showError('Não foi possível gerar o link público.')
  }
}

async function copiarLinkLogistica() {
  const token = evento.value?.tokenLogistica
  if (!token) return
  await navigator.clipboard.writeText(cerimonialStore.urlLogisticaPublica(token))
  linkLogisticaCopiado.value = true
  showSuccess('Link copiado.')
  setTimeout(() => {
    linkLogisticaCopiado.value = false
  }, 2500)
}

async function revogarLinkLogisticaPublica() {
  const ok = await showConfirm(
    'Colaboradores externos deixarão de acessar a checklist. Deseja revogar o link?',
    'Revogar link',
  )
  if (!ok) return
  await cerimonialStore.revogarLinkLogistica(eventoId.value)
  showSuccess('Link público revogado.')
}

function abrirRelatorio() {
  mostrarRelatorio.value = true
}

function imprimirRelatorio() {
  window.print()
}

function inserirVariavel(variavel: string) {
  mensagemTexto.value += `{{${variavel}}}`
}

function toggleTag(tag: string) {
  const index = tagsSelecionadas.value.indexOf(tag)
  if (index > -1) {
    tagsSelecionadas.value.splice(index, 1)
  } else {
    tagsSelecionadas.value.push(tag)
  }
}

// Funções de Upload de Imagem
function handleImagemUpload(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  
  if (!file) return
  
  // Validar tipo de arquivo
  if (!file.type.startsWith('image/')) {
    showError('Por favor, selecione apenas arquivos de imagem.')
    return
  }
  
  // Validar tamanho (máximo 5MB)
  if (file.size > 5 * 1024 * 1024) {
    showError('A imagem deve ter no máximo 5MB.')
    return
  }
  
  imagemArquivo.value = file
  
  // Criar preview
  const reader = new FileReader()
  reader.onload = (e) => {
    imagemPreview.value = e.target?.result as string
  }
  reader.readAsDataURL(file)
}

function removerImagem() {
  imagemArquivo.value = null
  imagemPreview.value = null
}

async function enviarMensagem() {
  if (!mensagemTexto.value.trim()) {
    showError('Por favor, escreva uma mensagem.')
    return
  }

  if (audienciaEstimada.value === 0) {
    showError('Por favor, selecione um público-alvo.')
    return
  }

  await cerimonialStore.enviarComunicacao(eventoId.value, {
    canal: canalSelecionado.value,
    publicoAlvo: {
      convidados: publicoConvidados.value,
      tagsCrm: tagsSelecionadas.value
    },
    mensagem: mensagemTexto.value,
    quantidadeEnvios: audienciaEstimada.value
  })

  // Reset form
  mensagemTexto.value = ''
  removerImagem()
  
  // Mostrar sucesso
  showSuccess('Mensagem enviada com sucesso! Acompanhe o status no histórico abaixo.')
}

function getCanalIcone(canal: string) {
  const icones: Record<string, any> = {
    email: Mail,
    whatsapp: MessageCircle,
    sms: Smartphone
  }
  return icones[canal] || Mail
}

function getCanalCor(canal: string) {
  const cores: Record<string, string> = {
    email: 'text-blue-600 dark:text-blue-400',
    whatsapp: 'text-green-600 dark:text-green-400',
    sms: 'text-purple-600 dark:text-purple-400'
  }
  return cores[canal] || 'text-gray-600'
}

function getStatusBadge(status: string) {
  const classes: Record<string, string> = {
    enviado: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
    processando: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
    falha: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
  }
  return classes[status] || 'bg-gray-100 text-gray-700'
}

function getStatusLabel(status: string) {
  const labels: Record<string, string> = {
    enviado: 'Enviado',
    processando: 'Processando',
    falha: 'Falha'
  }
  return labels[status] || status
}

</script>

<template>
  <div v-if="evento" class="space-y-6">
    <!-- Header do Evento -->
    <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      <!-- Botão Voltar -->
      <button
        @click="voltar"
        class="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors mb-4"
      >
        <ArrowLeft class="w-5 h-5" />
        Voltar para Agenda
      </button>

      <!-- Título e Info -->
      <div class="flex items-start justify-between mb-6">
        <div class="flex-1">
          <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            {{ evento.titulo }}
          </h1>
          
          <div class="flex flex-wrap items-center gap-4 text-gray-600 dark:text-gray-400">
            <div class="flex items-center gap-2">
              <Calendar class="w-5 h-5" />
              <span>{{ formatarData(evento.data) }}</span>
            </div>
            
            <div class="flex items-center gap-2">
              <Clock class="w-5 h-5" />
              <span>{{ evento.horaInicio }} - {{ evento.horaFim }}</span>
            </div>
            
            <div class="flex items-center gap-2">
              <MapPin class="w-5 h-5" />
              <span>{{ evento.local }}</span>
            </div>
          </div>

          <RastreabilidadeMeta
            v-if="evento"
            :rastreabilidade="evento.rastreabilidade"
            :alvo-auditoria="AUDITORIA_ALVO.eventoCerimonial(evento.id)"
            historico-titulo="Histórico do evento"
            show-criacao
            class="mt-3"
          />
        </div>

        <!-- Badge Status + Botão Excluir -->
        <div class="flex items-center gap-3">
          <!-- Badge Status -->
          <div
            :class="[
              evento.status === 'confirmado' && 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
              evento.status === 'planejamento' && 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
              evento.status === 'em_andamento' && 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
              evento.status === 'concluido' && 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
              'px-4 py-2 rounded-lg font-semibold uppercase text-sm'
            ]"
          >
            {{ evento.status.replace('_', ' ') }}
          </div>

          <!-- Botão Excluir (só aparece se podeExcluir) -->
          <button
            v-if="podeExcluir"
            @click="handleExcluir"
            class="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors"
            title="Excluir Evento"
          >
            <Trash2 class="w-5 h-5" />
            Excluir
          </button>
        </div>
      </div>

      <!-- Badges de Estatísticas -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div class="flex items-center gap-3 p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-900/30 rounded-lg border border-blue-200 dark:border-blue-800">
          <div class="p-3 bg-blue-500 dark:bg-blue-600 rounded-lg">
            <Users class="w-6 h-6 text-white" />
          </div>
          <div>
            <p class="text-2xl font-bold text-blue-900 dark:text-blue-100">{{ evento.totalConvidados }}</p>
            <p class="text-sm text-blue-700 dark:text-blue-300">Convidados</p>
          </div>
        </div>

        <div class="flex items-center gap-3 p-4 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-900/30 rounded-lg border border-green-200 dark:border-green-800">
          <div class="p-3 bg-green-500 dark:bg-green-600 rounded-lg">
            <CheckCircle2 class="w-6 h-6 text-white" />
          </div>
          <div>
            <p class="text-2xl font-bold text-green-900 dark:text-green-100">
              {{ progresso.providenciados }}/{{ progresso.total }}
            </p>
            <p class="text-sm text-green-700 dark:text-green-300">Checklist ({{ progresso.percentual }}%)</p>
          </div>
        </div>

        <div class="flex items-center gap-3 p-4 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-900/30 rounded-lg border border-purple-200 dark:border-purple-800">
          <div class="p-3 bg-purple-500 dark:bg-purple-600 rounded-lg">
            <ClipboardList class="w-6 h-6 text-white" />
          </div>
          <div>
            <p class="text-2xl font-bold text-purple-900 dark:text-purple-100">{{ evento.tipo.toUpperCase() }}</p>
            <p class="text-sm text-purple-700 dark:text-purple-300">Tipo de Evento</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Navegação por Abas -->
    <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
      <div class="border-b border-gray-200 dark:border-gray-700">
        <nav class="flex overflow-x-auto">
          <button
            @click="abaSelecionada = 'geral'"
            :class="[
              abaSelecionada === 'geral'
                ? 'border-primary-600 text-primary-600 dark:border-primary-400 dark:text-primary-400'
                : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600',
              'flex items-center gap-2 px-6 py-4 border-b-2 font-medium transition-colors whitespace-nowrap'
            ]"
          >
            <Info class="w-5 h-5" />
            Visão Geral
          </button>

          <button
            @click="abaSelecionada = 'logistica'"
            :class="[
              abaSelecionada === 'logistica'
                ? 'border-primary-600 text-primary-600 dark:border-primary-400 dark:text-primary-400'
                : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600',
              'flex items-center gap-2 px-6 py-4 border-b-2 font-medium transition-colors whitespace-nowrap'
            ]"
          >
            <ClipboardList class="w-5 h-5" />
            Logística (Checklist)
          </button>

          <button
            @click="abaSelecionada = 'convidados'"
            :class="[
              abaSelecionada === 'convidados'
                ? 'border-primary-600 text-primary-600 dark:border-primary-400 dark:text-primary-400'
                : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600',
              'flex items-center gap-2 px-6 py-4 border-b-2 font-medium transition-colors whitespace-nowrap'
            ]"
          >
            <UserCheck class="w-5 h-5" />
            Convidados & Precedência
          </button>

          <button
            @click="abaSelecionada = 'credenciamento'"
            :class="[
              abaSelecionada === 'credenciamento'
                ? 'border-primary-600 text-primary-600 dark:border-primary-400 dark:text-primary-400'
                : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600',
              'flex items-center gap-2 px-6 py-4 border-b-2 font-medium transition-colors whitespace-nowrap'
            ]"
          >
            <QrCode class="w-5 h-5" />
            Credenciamento (QR)
          </button>

          <button
            @click="abaSelecionada = 'comunicacao'"
            :class="[
              abaSelecionada === 'comunicacao'
                ? 'border-primary-600 text-primary-600 dark:border-primary-400 dark:text-primary-400'
                : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600',
              'flex items-center gap-2 px-6 py-4 border-b-2 font-medium transition-colors whitespace-nowrap'
            ]"
          >
            <Send class="w-5 h-5" />
            Comunicação & Mailing
          </button>
        </nav>
      </div>

      <!-- Conteúdo das Abas -->
      <div class="p-6">
        <!-- Aba: Visão Geral -->
        <div v-if="abaSelecionada === 'geral'" class="space-y-6">
          <!-- KPIs Principais -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <!-- Total Previsto -->
            <div class="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-900/30 rounded-xl p-6 border border-blue-200 dark:border-blue-800">
              <div class="flex items-center justify-between mb-3">
                <div class="p-3 bg-blue-500 dark:bg-blue-600 rounded-lg">
                  <Users class="w-6 h-6 text-white" />
                </div>
                <span class="text-xs font-medium text-blue-700 dark:text-blue-400 uppercase">Previsto</span>
              </div>
              <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ evento.totalConvidados }}</p>
              <p class="text-sm text-blue-700 dark:text-blue-300 mt-1">Convidados estimados</p>
            </div>

            <!-- Convidados Confirmados -->
            <div class="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-900/30 rounded-xl p-6 border border-green-200 dark:border-green-800">
              <div class="flex items-center justify-between mb-3">
                <div class="p-3 bg-green-500 dark:bg-green-600 rounded-lg">
                  <UserCheck class="w-6 h-6 text-white" />
                </div>
                <span class="text-xs font-medium text-green-700 dark:text-green-400 uppercase">Confirmados</span>
              </div>
              <p class="text-3xl font-bold text-green-900 dark:text-green-100">
                {{ cerimonialStore.convidadosConfirmados(eventoId).length }}
              </p>
              <p class="text-sm text-green-700 dark:text-green-300 mt-1">
                Convidados VIP/Autoridades
              </p>
            </div>

            <!-- Total Credenciados -->
            <div class="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-900/30 rounded-xl p-6 border border-purple-200 dark:border-purple-800">
              <div class="flex items-center justify-between mb-3">
                <div class="p-3 bg-purple-500 dark:bg-purple-600 rounded-lg">
                  <QrCode class="w-6 h-6 text-white" />
                </div>
                <span class="text-xs font-medium text-purple-700 dark:text-purple-400 uppercase">Credenciados</span>
              </div>
              <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">
                {{ cerimonialStore.totalCredenciados(eventoId) }}
              </p>
              <p class="text-sm text-purple-700 dark:text-purple-300 mt-1">
                Via formulário público
              </p>
            </div>

            <!-- Check-ins Realizados -->
            <div class="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-900/30 rounded-xl p-6 border border-orange-200 dark:border-orange-800">
              <div class="flex items-center justify-between mb-3">
                <div class="p-3 bg-orange-500 dark:bg-orange-600 rounded-lg">
                  <CheckCircle2 class="w-6 h-6 text-white" />
                </div>
                <span class="text-xs font-medium text-orange-700 dark:text-orange-400 uppercase">Presentes</span>
              </div>
              <p class="text-3xl font-bold text-orange-900 dark:text-orange-100">
                {{ cerimonialStore.totalPresentes(eventoId) }}
              </p>
              <p class="text-sm text-orange-700 dark:text-orange-300 mt-1">
                Com check-in automático
              </p>
            </div>
          </div>

          <!-- Progresso Geral -->
          <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Progresso do Evento</h3>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Logística -->
              <div>
                <div class="flex items-center justify-between mb-2">
                  <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Checklist Logístico</span>
                  <span class="text-sm font-bold text-gray-900 dark:text-gray-100">{{ progresso.percentual }}%</span>
                </div>
                <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div
                    class="h-full bg-gradient-to-r from-green-500 to-green-600 transition-all duration-300"
                    :style="{ width: progresso.percentual + '%' }"
                  />
                </div>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {{ progresso.providenciados }} de {{ progresso.total }} itens providenciados
                </p>
              </div>

              <!-- Taxa de Confirmação -->
              <div>
                <div class="flex items-center justify-between mb-2">
                  <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Taxa de Confirmação</span>
                  <span class="text-sm font-bold text-gray-900 dark:text-gray-100">
                    {{ Math.round((cerimonialStore.convidadosConfirmados(eventoId).length / Math.max(cerimonialStore.convidadosOrdenados(eventoId).length, 1)) * 100) }}%
                  </span>
                </div>
                <div class="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div
                    class="h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-300"
                    :style="{ width: Math.round((cerimonialStore.convidadosConfirmados(eventoId).length / Math.max(cerimonialStore.convidadosOrdenados(eventoId).length, 1)) * 100) + '%' }"
                  />
                </div>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {{ cerimonialStore.convidadosConfirmados(eventoId).length }} confirmados de {{ cerimonialStore.convidadosOrdenados(eventoId).length }} convidados
                </p>
              </div>
            </div>
          </div>

          <!-- Descrição e Informações -->
          <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Descrição do Evento</h3>
            <p class="text-gray-600 dark:text-gray-400 leading-relaxed">
              {{ evento.descricao || 'Sem descrição disponível.' }}
            </p>
          </div>

          <!-- Resumo Rápido -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 border border-gray-200 dark:border-gray-600">
              <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Status do Evento</p>
              <p class="text-lg font-semibold text-gray-900 dark:text-gray-100 capitalize">
                {{ evento.status.replace('_', ' ') }}
              </p>
            </div>

            <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 border border-gray-200 dark:border-gray-600">
              <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Tipo de Evento</p>
              <p class="text-lg font-semibold text-gray-900 dark:text-gray-100 capitalize">
                {{ evento.tipo }}
              </p>
            </div>

            <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 border border-gray-200 dark:border-gray-600">
              <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Local</p>
              <p class="text-lg font-semibold text-gray-900 dark:text-gray-100">
                {{ evento.local }}
              </p>
            </div>
          </div>
        </div>

        <!-- Aba: Logística e Checklist -->
        <div v-if="abaSelecionada === 'logistica'" class="space-y-6">
          <!-- Header da Aba -->
          <div class="flex items-center justify-between">
            <div>
              <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">Checklist Logístico</h3>
              <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                {{ progresso.providenciados }} de {{ progresso.total }} itens providenciados
              </p>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Adicione itens apenas do catálogo. O link externo permite ao colaborador revisar e enviar as atualizações de uma vez.
              </p>
            </div>

            <div class="flex flex-wrap items-center gap-2 justify-end">
              <button
                v-if="!evento?.logisticaPublicaAtiva"
                type="button"
                @click="ativarLinkLogisticaPublica"
                class="flex items-center gap-2 px-4 py-2 bg-emerald-100 hover:bg-emerald-200 dark:bg-emerald-900/30 dark:hover:bg-emerald-900/50 text-emerald-800 dark:text-emerald-300 rounded-lg font-medium transition-colors text-sm"
              >
                <QrCode class="w-4 h-4" />
                Gerar link externo
              </button>
              <template v-else>
                <button
                  type="button"
                  @click="copiarLinkLogistica"
                  class="flex items-center gap-2 px-4 py-2 bg-emerald-100 hover:bg-emerald-200 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-300 rounded-lg font-medium text-sm"
                >
                  {{ linkLogisticaCopiado ? 'Copiado!' : 'Copiar link externo' }}
                </button>
                <button
                  type="button"
                  @click="revogarLinkLogisticaPublica"
                  class="px-3 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg"
                >
                  Revogar
                </button>
              </template>

              <button
                @click="mostrarGestaoItens = true"
                class="flex items-center gap-2 px-4 py-2 bg-blue-100 hover:bg-blue-200 dark:bg-blue-900/30 dark:hover:bg-blue-900/50 text-blue-700 dark:text-blue-400 rounded-lg font-medium transition-colors text-sm"
              >
                <ClipboardList class="w-4 h-4" />
                Gerir Itens Padrão
              </button>

              <button
                @click="abrirRelatorio"
                class="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 dark:text-gray-100 rounded-lg font-medium transition-colors text-sm"
              >
                <Printer class="w-5 h-5" />
                Gerar Relatório
              </button>
            </div>
          </div>

          <div
            v-if="evento?.observacaoLogisticaExterna"
            class="p-4 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 text-sm text-blue-900 dark:text-blue-200"
          >
            <p class="font-medium mb-1">Última observação do colaborador externo:</p>
            <p class="whitespace-pre-wrap">{{ evento.observacaoLogisticaExterna }}</p>
          </div>

          <!-- Checklist por Categoria -->
          <div class="space-y-6">
            <div
              v-for="(items, categoria) in checklistPorCategoria"
              :key="categoria"
              class="bg-gray-50 dark:bg-gray-700/30 rounded-lg border border-gray-200 dark:border-gray-600 overflow-hidden"
            >
              <!-- Header da Categoria -->
              <div
                class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-600"
                :style="{ backgroundColor: categoriasConfig[categoria as keyof typeof categoriasConfig].cor + '15' }"
              >
                <div class="flex items-center gap-3">
                  <div
                    class="w-8 h-8 rounded-lg flex items-center justify-center"
                    :style="{ backgroundColor: categoriasConfig[categoria as keyof typeof categoriasConfig].cor }"
                  >
                    <div class="w-3 h-3 bg-white rounded-full"></div>
                  </div>
                  <div>
                    <h4 class="font-semibold text-gray-900 dark:text-gray-100">
                      {{ categoriasConfig[categoria as keyof typeof categoriasConfig].nome }}
                    </h4>
                    <p class="text-sm text-gray-600 dark:text-gray-400">
                      {{ (items as ItemChecklist[]).length }} item(ns)
                    </p>
                  </div>
                </div>

                <button
                  @click="toggleFormularioCategoria(categoria)"
                  class="p-2 hover:bg-white dark:hover:bg-gray-600 rounded-lg transition-colors"
                  :title="'Adicionar item em ' + categoriasConfig[categoria as keyof typeof categoriasConfig].nome"
                >
                  <Plus class="w-5 h-5 text-gray-600 dark:text-gray-400" />
                </button>
              </div>

              <!-- Formulário Inline -->
              <Transition
                enter-active-class="transition ease-out duration-200"
                enter-from-class="opacity-0 -translate-y-2"
                enter-to-class="opacity-100 translate-y-0"
                leave-active-class="transition ease-in duration-150"
                leave-from-class="opacity-100 translate-y-0"
                leave-to-class="opacity-0 -translate-y-2"
              >
                <div
                  v-if="mostrarFormulario === categoria"
                  class="p-4 bg-white dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600 space-y-4"
                >
                  <!-- Itens Padrão -->
                  <div class="space-y-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-800/80 border border-gray-200 dark:border-gray-600">
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Adicionar item padrão
                    </label>
                    <select
                      v-model="itemPadraoSelecionadoId"
                      class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
                    >
                      <option value="">-- Escolher item padrão --</option>
                      <option
                        v-for="itemPadrao in cerimonialStore.itensPadraoPorCategoria[categoria]"
                        :key="itemPadrao.id"
                        :value="itemPadrao.id"
                      >
                        {{ itemPadrao.descricao }}
                      </option>
                    </select>
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <input
                        v-model="padraoForm.responsavel"
                        type="text"
                        placeholder="Responsável (opcional)"
                        class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                      />
                      <input
                        v-model="padraoForm.prazo"
                        type="date"
                        class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                      />
                    </div>
                    <div class="flex items-center gap-2">
                      <button
                        type="button"
                        @click="adicionarItemPadrao(categoria)"
                        :disabled="!itemPadraoSelecionadoId"
                        class="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium disabled:opacity-50"
                      >
                        <Check class="w-4 h-4" />
                        Adicionar à checklist
                      </button>
                      <button
                        type="button"
                        @click="mostrarFormulario = null"
                        class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 rounded-lg"
                      >
                        Cancelar
                      </button>
                    </div>
                  </div>
                </div>
              </Transition>

              <!-- Lista de Itens -->
              <div class="divide-y divide-gray-200 dark:divide-gray-600">
                <div
                  v-for="item in (items as ItemChecklist[])"
                  :key="item.id"
                  class="p-4 hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-colors group"
                >
                  <div class="flex items-start gap-3">
                    <!-- Checkbox -->
                    <button
                      @click="toggleItem(item.id)"
                      :class="[
                        item.status === 'providenciado'
                          ? 'bg-green-500 border-green-500'
                          : 'bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600',
                        'w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 mt-0.5 transition-colors'
                      ]"
                    >
                      <Check
                        v-if="item.status === 'providenciado'"
                        class="w-3 h-3 text-white"
                      />
                    </button>

                    <!-- Conteúdo -->
                    <div class="flex-1 min-w-0">
                      <p
                        :class="[
                          item.status === 'providenciado'
                            ? 'line-through text-gray-500 dark:text-gray-500'
                            : 'text-gray-900 dark:text-gray-100',
                          'font-medium'
                        ]"
                      >
                        {{ item.descricao }}
                      </p>
                      
                      <div class="flex flex-wrap items-center gap-x-4 gap-y-1 mt-1 text-sm text-gray-500 dark:text-gray-400">
                        <span v-if="item.responsavel">
                          👤 {{ item.responsavel }}
                        </span>
                        <span v-if="item.prazo">
                          📅 {{ new Date(item.prazo).toLocaleDateString('pt-BR') }}
                        </span>
                      </div>
                    </div>

                    <!-- Botão Remover -->
                    <button
                      @click="removerItem(item.id)"
                      class="opacity-0 group-hover:opacity-100 p-1 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-all"
                      title="Remover item"
                    >
                      <Trash2 class="w-4 h-4" />
                    </button>
                  </div>
                </div>

                <div
                  v-if="(items as ItemChecklist[]).length === 0"
                  class="p-8 text-center text-gray-500 dark:text-gray-400"
                >
                  Nenhum item nesta categoria
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Aba: Convidados -->
        <div v-if="abaSelecionada === 'convidados'">
          <GestaoConvidados :evento-id="eventoId" />
        </div>

        <!-- Aba: Credenciamento -->
        <div v-if="abaSelecionada === 'credenciamento'">
          <CredenciamentoPainel :evento-id="eventoId" />
        </div>

        <!-- Aba: Comunicação & Mailing -->
        <div v-if="abaSelecionada === 'comunicacao'" class="space-y-6">
          <!-- Header -->
          <div class="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white">
            <h3 class="text-xl font-bold mb-2">Comunicação & Mailing</h3>
            <p class="text-blue-100">Mobilize seu público através de múltiplos canais integrados ao CRM</p>
          </div>

          <!-- Público-Alvo (Segmentação) -->
          <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
            <h4 class="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Users class="w-5 h-5 text-primary-600 dark:text-primary-400" />
              Público-Alvo (Mailing)
            </h4>

            <div class="space-y-4">
              <!-- Checkbox Convidados -->
              <label class="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-900/50 rounded-lg border border-gray-200 dark:border-gray-700 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
                <input
                  v-model="publicoConvidados"
                  type="checkbox"
                  class="w-5 h-5 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <div class="flex-1">
                  <span class="font-medium text-gray-900 dark:text-white">Convidados Confirmados</span>
                  <p class="text-sm text-gray-600 dark:text-gray-400">
                    {{ cerimonialStore.convidadosConfirmados(eventoId).length }} autoridades da Aba 3
                  </p>
                </div>
              </label>

              <!-- Tags do CRM -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Filtros por Tags do CRM
                </label>
                <p
                  v-if="!tagsCrmProntas && !erroTagsCrm"
                  class="text-sm text-gray-500 dark:text-gray-400"
                >
                  Carregando tags do CRM…
                </p>
                <p v-else-if="erroTagsCrm" class="text-sm text-red-600 dark:text-red-400 mt-2">
                  {{ erroTagsCrm }}
                </p>
                <div v-else class="flex flex-wrap gap-2">
                  <button
                    v-for="tag in tagsComunicacao"
                    :key="tag.id"
                    type="button"
                    @click="toggleTag(tag.nome)"
                    :class="[
                      tagsSelecionadas.includes(tag.nome)
                        ? 'ring-2 ring-offset-1 ring-primary-500 text-gray-900 dark:text-gray-100'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600',
                      'px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex items-center gap-2'
                    ]"
                    :style="
                      tagsSelecionadas.includes(tag.nome)
                        ? { backgroundColor: `${tag.cor}33`, borderColor: tag.cor }
                        : undefined
                    "
                  >
                    <TagIcon class="w-3 h-3" :style="{ color: tag.cor }" />
                    {{ tag.nome }}
                  </button>
                </div>
                <p
                  v-if="tagsCrmProntas && !erroTagsCrm && tagsComunicacao.length === 0"
                  class="text-sm text-gray-500 dark:text-gray-400 mt-2"
                >
                  Nenhuma tag cadastrada no CRM. Crie em Configurações → Classificações.
                </p>
              </div>

              <!-- Contador de Audiência -->
              <div class="mt-4 p-4 bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                <div class="flex items-center justify-between">
                  <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Audiência Estimada:</span>
                  <span class="text-2xl font-bold text-purple-900 dark:text-purple-100">
                    <template v-if="recalculandoAudienciaTags">…</template>
                    <template v-else>{{ audienciaEstimada }} contatos</template>
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Canais & Editor -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- Lado Esquerdo: Canais e Editor -->
            <div class="space-y-6">
              <!-- Seletor de Canais -->
              <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
                <h4 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Canal de Disparo</h4>
                
                <div class="grid grid-cols-3 gap-3">
                  <!-- Email -->
                  <button
                    @click="canalSelecionado = 'email'"
                    :class="[
                      canalSelecionado === 'email'
                        ? 'bg-blue-100 dark:bg-blue-900/30 border-blue-500 dark:border-blue-400'
                        : 'bg-gray-50 dark:bg-gray-900/50 border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800',
                      'p-4 rounded-lg border-2 transition-all cursor-pointer'
                    ]"
                  >
                    <Mail :class="[canalSelecionado === 'email' ? 'text-blue-600 dark:text-blue-400' : 'text-gray-600 dark:text-gray-400', 'w-8 h-8 mx-auto mb-2']" />
                    <p class="text-sm font-medium text-gray-900 dark:text-white">E-mail</p>
                  </button>

                  <!-- WhatsApp -->
                  <button
                    @click="canalSelecionado = 'whatsapp'"
                    :class="[
                      canalSelecionado === 'whatsapp'
                        ? 'bg-green-100 dark:bg-green-900/30 border-green-500 dark:border-green-400'
                        : 'bg-gray-50 dark:bg-gray-900/50 border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800',
                      'p-4 rounded-lg border-2 transition-all cursor-pointer'
                    ]"
                  >
                    <MessageCircle :class="[canalSelecionado === 'whatsapp' ? 'text-green-600 dark:text-green-400' : 'text-gray-600 dark:text-gray-400', 'w-8 h-8 mx-auto mb-2']" />
                    <p class="text-sm font-medium text-gray-900 dark:text-white">WhatsApp</p>
                  </button>

                  <!-- SMS -->
                  <button
                    @click="canalSelecionado = 'sms'"
                    :class="[
                      canalSelecionado === 'sms'
                        ? 'bg-purple-100 dark:bg-purple-900/30 border-purple-500 dark:border-purple-400'
                        : 'bg-gray-50 dark:bg-gray-900/50 border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-800',
                      'p-4 rounded-lg border-2 transition-all cursor-pointer'
                    ]"
                  >
                    <Smartphone :class="[canalSelecionado === 'sms' ? 'text-purple-600 dark:text-purple-400' : 'text-gray-600 dark:text-gray-400', 'w-8 h-8 mx-auto mb-2']" />
                    <p class="text-sm font-medium text-gray-900 dark:text-white">SMS</p>
                  </button>
                </div>

                <!-- Aviso de Configuração -->
                <div class="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                  <p class="text-xs text-blue-700 dark:text-blue-300">
                    <strong>Info:</strong> Integração via API padrão. Configure credenciais em Configurações › Integrações.
                  </p>
                </div>
              </div>

              <!-- Editor de Mensagem -->
              <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
                <h4 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Mensagem</h4>

                <!-- Variáveis Dinâmicas -->
                <div class="mb-3">
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Variáveis Dinâmicas
                  </label>
                  <div class="flex flex-wrap gap-2">
                    <button
                      @click="inserirVariavel('Nome_Contato')"
                      class="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 rounded border border-gray-300 dark:border-gray-600 transition-colors"
                    >
                      Nome_Contato
                    </button>
                    <button
                      @click="inserirVariavel('Titulo_Evento')"
                      class="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 rounded border border-gray-300 dark:border-gray-600 transition-colors"
                    >
                      Titulo_Evento
                    </button>
                    <button
                      @click="inserirVariavel('Data_Evento')"
                      class="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 rounded border border-gray-300 dark:border-gray-600 transition-colors"
                    >
                      Data_Evento
                    </button>
                    <button
                      @click="inserirVariavel('Hora_Inicio')"
                      class="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 rounded border border-gray-300 dark:border-gray-600 transition-colors"
                    >
                      Hora_Inicio
                    </button>
                    <button
                      @click="inserirVariavel('Local')"
                      class="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 rounded border border-gray-300 dark:border-gray-600 transition-colors"
                    >
                      Local
                    </button>
                    <button
                      @click="inserirVariavel('Link_Credenciamento')"
                      class="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 rounded border border-gray-300 dark:border-gray-600 transition-colors"
                    >
                      Link_Credenciamento
                    </button>
                  </div>
                </div>

                <!-- Upload de Imagem -->
                <div class="mb-3">
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Imagem (Opcional)
                  </label>
                  
                  <!-- Preview da Imagem -->
                  <div v-if="imagemPreview" class="mb-3 relative">
                    <img 
                      :src="imagemPreview" 
                      alt="Preview" 
                      class="w-full h-48 object-cover rounded-lg border-2 border-gray-300 dark:border-gray-600"
                    />
                    <button
                      @click="removerImagem"
                      class="absolute top-2 right-2 p-2 bg-red-600 hover:bg-red-700 text-white rounded-full shadow-lg transition-colors"
                    >
                      <X class="w-4 h-4" />
                    </button>
                  </div>

                  <!-- Upload Button -->
                  <label 
                    v-if="!imagemPreview"
                    class="flex items-center justify-center gap-2 px-4 py-3 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg border-2 border-dashed border-gray-300 dark:border-gray-600 cursor-pointer transition-colors"
                  >
                    <Upload class="w-5 h-5" />
                    <span class="text-sm font-medium">Adicionar Imagem (máx. 5MB)</span>
                    <input 
                      type="file" 
                      accept="image/*" 
                      class="hidden" 
                      @change="handleImagemUpload"
                    />
                  </label>

                  <!-- Opção: Corpo ou Anexo -->
                  <div v-if="imagemPreview" class="mt-2 flex items-center gap-4">
                    <label class="flex items-center gap-2 cursor-pointer">
                      <input 
                        type="radio" 
                        v-model="imagemPosicao" 
                        value="corpo"
                        class="w-4 h-4 text-primary-600 focus:ring-primary-500"
                      />
                      <span class="text-sm text-gray-700 dark:text-gray-300">No corpo da mensagem</span>
                    </label>
                    <label class="flex items-center gap-2 cursor-pointer">
                      <input 
                        type="radio" 
                        v-model="imagemPosicao" 
                        value="anexo"
                        class="w-4 h-4 text-primary-600 focus:ring-primary-500"
                      />
                      <span class="text-sm text-gray-700 dark:text-gray-300">Como anexo</span>
                    </label>
                  </div>
                </div>

                <!-- Textarea -->
                <textarea
                  v-model="mensagemTexto"
                  rows="8"
                  placeholder="Escreva sua mensagem aqui..."
                  class="w-full px-4 py-3 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all text-gray-900 dark:text-white resize-none"
                ></textarea>

                <!-- Botão Enviar -->
                <button
                  @click="enviarMensagem"
                  class="mt-4 w-full flex items-center justify-center gap-2 px-6 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all transform hover:scale-[1.02]"
                >
                  <Send class="w-5 h-5" />
                  Enviar Mensagem para {{ audienciaEstimada }} Contatos
                </button>
              </div>
            </div>

            <!-- Lado Direito: Preview Smartphone -->
            <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
              <h4 class="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <Eye class="w-5 h-5 text-primary-600 dark:text-primary-400" />
                Preview em Tempo Real
              </h4>

              <!-- Mockup de Smartphone -->
              <div class="mx-auto max-w-sm">
                <div class="bg-gray-900 rounded-[2.5rem] p-3 shadow-2xl">
                  <!-- Tela do Smartphone -->
                  <div class="bg-white rounded-[2rem] overflow-hidden">
                    <!-- Header do App -->
                    <div class="bg-gray-100 px-4 py-3 border-b border-gray-200">
                      <div class="flex items-center gap-2">
                        <component :is="getCanalIcone(canalSelecionado)" :class="['w-5 h-5', getCanalCor(canalSelecionado)]" />
                        <span class="text-sm font-medium text-gray-900">
                          {{ canalSelecionado === 'email' ? 'Nova Mensagem' : canalSelecionado === 'whatsapp' ? 'Gabinete' : 'SMS Recebido' }}
                        </span>
                      </div>
                    </div>

                    <!-- Conteúdo da Mensagem -->
                    <div class="p-4 min-h-[400px] bg-gray-50">
                      <div :class="[
                        canalSelecionado === 'whatsapp' ? 'bg-green-100 border-green-200' : 'bg-white border-gray-200',
                        'p-4 rounded-lg border shadow-sm'
                      ]">
                        <!-- Imagem (se estiver no corpo) -->
                        <img 
                          v-if="imagemPreview && imagemPosicao === 'corpo'" 
                          :src="imagemPreview" 
                          alt="Imagem da mensagem"
                          class="w-full rounded-lg mb-3"
                        />
                        
                        <!-- Texto da mensagem -->
                        <p v-if="mensagemPreview" class="text-sm text-gray-900 whitespace-pre-wrap">
                          {{ mensagemPreview }}
                        </p>
                        <p v-else class="text-sm text-gray-400 italic">
                          Escreva uma mensagem para ver o preview...
                        </p>
                        
                        <!-- Anexo (se estiver como anexo) -->
                        <div 
                          v-if="imagemPreview && imagemPosicao === 'anexo'" 
                          class="mt-3 flex items-center gap-2 p-2 bg-gray-100 rounded border border-gray-300"
                        >
                          <ImageIcon class="w-4 h-4 text-gray-600" />
                          <span class="text-xs text-gray-700">{{ imagemArquivo?.name || 'imagem.jpg' }}</span>
                        </div>
                        
                        <p class="text-xs text-gray-500 mt-2">
                          {{ new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) }}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Histórico de Comunicações -->
          <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h4 class="text-lg font-semibold text-gray-900 dark:text-white">Histórico de Comunicações</h4>
            </div>

            <div class="overflow-x-auto">
              <table class="w-full">
                <thead class="bg-gray-50 dark:bg-gray-700/50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Data/Hora</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Canal</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Público-Alvo</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Envios</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Status</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                  <tr
                    v-for="comunicacao in historicoOrdenado"
                    :key="comunicacao.id"
                    class="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                  >
                    <td class="px-6 py-4 text-sm text-gray-900 dark:text-gray-100">
                      {{ new Date(comunicacao.dataHora).toLocaleString('pt-BR') }}
                    </td>
                    <td class="px-6 py-4">
                      <div class="flex items-center gap-2">
                        <component :is="getCanalIcone(comunicacao.canal)" :class="['w-5 h-5', getCanalCor(comunicacao.canal)]" />
                        <span class="text-sm text-gray-900 dark:text-gray-100 capitalize">{{ comunicacao.canal }}</span>
                      </div>
                    </td>
                    <td class="px-6 py-4">
                      <div class="text-sm text-gray-900 dark:text-gray-100">
                        <span v-if="comunicacao.publicoAlvo.convidados">Convidados</span>
                        <span v-if="comunicacao.publicoAlvo.convidados && comunicacao.publicoAlvo.tagsCrm.length > 0"> + </span>
                        <span v-if="comunicacao.publicoAlvo.tagsCrm.length > 0">
                          Tags: {{ comunicacao.publicoAlvo.tagsCrm.join(', ') }}
                        </span>
                      </div>
                    </td>
                    <td class="px-6 py-4 text-sm font-medium text-gray-900 dark:text-gray-100">
                      {{ comunicacao.quantidadeEnvios }}
                    </td>
                    <td class="px-6 py-4">
                      <span
                        :class="[
                          getStatusBadge(comunicacao.status),
                          'px-2.5 py-1 rounded-full text-xs font-medium'
                        ]"
                      >
                        {{ getStatusLabel(comunicacao.status) }}
                      </span>
                    </td>
                  </tr>

                  <tr v-if="historicoOrdenado.length === 0">
                    <td colspan="5" class="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
                      Nenhuma comunicação enviada ainda
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de Relatório para Impressão -->
    <Transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="mostrarRelatorio"
        class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 print:bg-white print:relative print:block"
        @click.self="mostrarRelatorio = false"
      >
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col print:max-w-none print:shadow-none print:max-h-none">
          <!-- Header do Modal (oculto na impressão) -->
          <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 print:hidden">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Relatório da Equipe de Apoio
            </h3>
            <div class="flex items-center gap-2">
              <button
                @click="imprimirRelatorio"
                class="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors"
              >
                <Printer class="w-4 h-4" />
                Imprimir
              </button>
              <button
                @click="mostrarRelatorio = false"
                class="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded transition-colors"
              >
                <X class="w-5 h-5" />
              </button>
            </div>
          </div>

          <!-- Conteúdo do Relatório -->
          <div class="flex-1 overflow-y-auto p-8 print:p-0 print:overflow-visible">
            <!-- Header do Relatório (visível na impressão) -->
            <div class="mb-8 print:mb-6">
              <h1 class="text-3xl font-bold text-gray-900 mb-2 print:text-2xl">
                Checklist Logístico
              </h1>
              <h2 class="text-xl text-gray-600 mb-4 print:text-lg">
                {{ evento?.titulo }}
              </h2>
              <div class="grid grid-cols-2 gap-4 text-sm print:text-xs">
                <div>
                  <span class="font-semibold">Data:</span> {{ evento ? formatarData(evento.data) : '' }}
                </div>
                <div>
                  <span class="font-semibold">Horário:</span> {{ evento?.horaInicio }} - {{ evento?.horaFim }}
                </div>
                <div>
                  <span class="font-semibold">Local:</span> {{ evento?.local }}
                </div>
                <div>
                  <span class="font-semibold">Convidados:</span> {{ evento?.totalConvidados }}
                </div>
              </div>
            </div>

            <!-- Checklist por Categoria -->
            <div class="space-y-6 print:space-y-4">
              <div
                v-for="(items, categoria) in checklistPorCategoria"
                :key="categoria"
                class="break-inside-avoid"
              >
                <h3 class="text-lg font-bold text-gray-900 mb-3 pb-2 border-b-2 border-gray-300 print:text-base flex items-center gap-2">
                  <div
                    class="w-4 h-4 rounded"
                    :style="{ backgroundColor: categoriasConfig[categoria as keyof typeof categoriasConfig].cor }"
                  ></div>
                  {{ categoriasConfig[categoria as keyof typeof categoriasConfig].nome }}
                </h3>
                
                <div class="space-y-2 print:space-y-1">
                  <div
                    v-for="item in (items as ItemChecklist[])"
                    :key="item.id"
                    class="flex items-start gap-3 print:text-sm"
                  >
                    <div
                      :class="[
                        item.status === 'providenciado' ? 'border-gray-400' : 'border-gray-300',
                        'w-4 h-4 border-2 rounded flex-shrink-0 mt-0.5'
                      ]"
                    >
                      <div v-if="item.status === 'providenciado'" class="w-full h-full flex items-center justify-center">
                        <span class="text-xs">✓</span>
                      </div>
                    </div>
                    
                    <div class="flex-1">
                      <p class="text-gray-900">{{ item.descricao }}</p>
                      <p v-if="item.responsavel || item.prazo" class="text-xs text-gray-600 mt-0.5">
                        <span v-if="item.responsavel">Resp.: {{ item.responsavel }}</span>
                        <span v-if="item.responsavel && item.prazo"> • </span>
                        <span v-if="item.prazo">Prazo: {{ new Date(item.prazo).toLocaleDateString('pt-BR') }}</span>
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Rodapé do Relatório -->
            <div class="mt-8 pt-4 border-t border-gray-300 text-sm text-gray-600 print:mt-6">
              <p>Gerado em: {{ new Date().toLocaleString('pt-BR') }}</p>
              <p class="mt-2">
                <strong>Observações:</strong> _____________________________________________
              </p>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Modal: Gestão de Itens Padrão -->
    <Transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="mostrarGestaoItens"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
        @click.self="mostrarGestaoItens = false"
      >
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
          <!-- Header Modal -->
          <div class="sticky top-0 bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-4 flex items-center justify-between">
            <h2 class="text-xl font-bold text-white">Gestão de Itens Padrão</h2>
            <button
              @click="mostrarGestaoItens = false"
              class="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
            >
              <X class="w-5 h-5" />
            </button>
          </div>

          <!-- Conteúdo -->
          <div class="p-6 space-y-6">
            <!-- Info -->
            <div class="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
              <p class="text-sm text-blue-700 dark:text-blue-300">
                <strong>Itens padrão</strong> são modelos reutilizáveis que podem ser adicionados rapidamente ao checklist de qualquer evento. Cadastre aqui os itens mais comuns da sua operação.
              </p>
            </div>

            <!-- Formulário Adicionar -->
            <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 border border-gray-200 dark:border-gray-600">
              <h3 class="font-semibold text-gray-900 dark:text-gray-100 mb-3">Adicionar Novo Item Padrão</h3>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                <select
                  v-model="novoItem.categoria"
                  class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                >
                  <option value="infraestrutura">Infraestrutura</option>
                  <option value="buffet">Buffet</option>
                  <option value="cerimonial">Cerimonial</option>
                  <option value="comunicacao">Comunicação</option>
                  <option value="seguranca">Segurança</option>
                  <option value="tecnologia">Tecnologia</option>
                </select>

                <input
                  v-model="novoItem.descricao"
                  type="text"
                  placeholder="Descrição do item..."
                  class="col-span-2 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                  @keydown.enter="adicionarNovoItemPadrao"
                />

                <button
                  @click="adicionarNovoItemPadrao"
                  class="md:col-span-3 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  <Plus class="w-4 h-4" />
                  Adicionar Item Padrão
                </button>
              </div>
            </div>

            <!-- Lista por Categoria -->
            <div
              v-for="(items, categoria) in cerimonialStore.itensPadraoPorCategoria"
              :key="categoria"
              class="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
            >
              <div
                class="px-4 py-3 flex items-center gap-3 border-b border-gray-200 dark:border-gray-700"
                :style="{ backgroundColor: categoriasConfig[categoria as keyof typeof categoriasConfig].cor + '15' }"
              >
                <div
                  class="w-6 h-6 rounded flex items-center justify-center"
                  :style="{ backgroundColor: categoriasConfig[categoria as keyof typeof categoriasConfig].cor }"
                >
                  <div class="w-2 h-2 bg-white rounded-full"></div>
                </div>
                <h4 class="font-semibold text-gray-900 dark:text-gray-100">
                  {{ categoriasConfig[categoria as keyof typeof categoriasConfig].nome }}
                </h4>
                <span class="text-xs text-gray-500 dark:text-gray-400">
                  ({{ items.length }} itens)
                </span>
              </div>

              <div class="divide-y divide-gray-200 dark:divide-gray-700">
                <div
                  v-for="item in items"
                  :key="item.id"
                  class="px-4 py-3 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                >
                  <span class="text-sm text-gray-900 dark:text-gray-100">
                    {{ item.descricao }}
                  </span>
                  <button
                    @click="removerItemPadraoConfirm(item.id)"
                    class="p-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                    title="Remover item padrão"
                  >
                    <Trash2 class="w-4 h-4" />
                  </button>
                </div>

                <div v-if="items.length === 0" class="px-4 py-6 text-center text-sm text-gray-500 dark:text-gray-400">
                  Nenhum item padrão nesta categoria
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>

  <!-- Fallback se evento não existir -->
  <div v-else class="flex items-center justify-center h-64">
    <div class="text-center">
      <Calendar class="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
      <p class="text-gray-500 dark:text-gray-400">Evento não encontrado</p>
    </div>
  </div>
</template>

<style scoped>
@media print {
  body {
    print-color-adjust: exact;
    -webkit-print-color-adjust: exact;
  }
}
</style>
