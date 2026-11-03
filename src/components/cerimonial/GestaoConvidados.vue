<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useCerimonialStore } from '@/stores/cerimonial'
import { useCrmStore } from '@/stores/crm'
import type { Convidado } from '@/stores/cerimonial'
import type { Cidadao } from '@/types'
import { ApiError } from '@/services/api'
import { useAlertDialog } from '@/composables/useAlertDialog'
import CidadaoModal from '@/components/crm/CidadaoModal.vue'
import draggable from 'vuedraggable'
import {
  UserPlus,
  Search,
  Star,
  Trash2,
  X,
  Crown,
  Printer,
  GripVertical,
  FileText,
  SquarePen
} from 'lucide-vue-next'

interface Props {
  eventoId: string
}

const props = defineProps<Props>()

const cerimonialStore = useCerimonialStore()
const crmStore = useCrmStore()
const { showConfirm, showSuccess, showError } = useAlertDialog()

const buscaCidadao = ref('')
const mostrarResultados = ref(false)
const resultadosBusca = ref<Cidadao[]>([])
const buscandoCrm = ref(false)
const erroBuscaCrm = ref('')
let debounceBuscaCrm: ReturnType<typeof setTimeout> | undefined
let buscaCrmSeq = 0
const mostrarPrismas = ref(false)
const mostrarFichaCerimonialista = ref(false)
const mostrarCidadaoModal = ref(false)
const cidadaoEditando = ref<any>(null)
const drag = ref(false)

// Seleção de perfil para cidadão com múltiplos perfis
const cidadaoSelecionado = ref<string | null>(null)
const mostrarSeletorPerfil = ref(false)
const perfilSelecionado = ref<string>('')

const convidados = computed(() => {
  return cerimonialStore.convidadosOrdenados(props.eventoId)
})

const convidadosLocal = ref<Convidado[]>([])

watch(
  convidados,
  list => {
    if (!drag.value) {
      convidadosLocal.value = [...list]
    }
  },
  { immediate: true },
)

async function onDragEnd() {
  drag.value = false
  try {
    await cerimonialStore.salvarOrdemConvidados(props.eventoId, convidadosLocal.value)
    showSuccess('Ordem de precedência atualizada.')
  } catch {
    showError('Não foi possível salvar a nova ordem.')
    convidadosLocal.value = [...convidados.value]
  }
}

const convidadosConfirmados = computed(() => {
  return cerimonialStore.convidadosConfirmados(props.eventoId)
})

function mensagemErroBuscaCrm(e: unknown): string {
  if (e instanceof ApiError) {
    if (e.status === 403) return 'Sem permissão para consultar cidadãos no CRM.'
    if (e.status === 401) return 'Sessão expirada. Faça login novamente.'
  }
  return 'Não foi possível buscar no CRM.'
}

watch(buscaCidadao, valor => {
  clearTimeout(debounceBuscaCrm)
  const trimmed = valor.trim()
  if (trimmed.length < 2) {
    resultadosBusca.value = []
    erroBuscaCrm.value = ''
    buscandoCrm.value = false
    mostrarResultados.value = false
    return
  }
  mostrarResultados.value = true
  buscandoCrm.value = true
  erroBuscaCrm.value = ''
  const seq = ++buscaCrmSeq
  debounceBuscaCrm = setTimeout(async () => {
    try {
      const lista = await crmStore.searchCidadaos(trimmed, 15)
      if (seq !== buscaCrmSeq) return
      resultadosBusca.value = lista
    } catch (e) {
      if (seq !== buscaCrmSeq) return
      resultadosBusca.value = []
      erroBuscaCrm.value = mensagemErroBuscaCrm(e)
    } finally {
      if (seq === buscaCrmSeq) buscandoCrm.value = false
    }
  }, 300)
})

function getCidadaoInfo(cidadaoId: string) {
  // Busca direta no array de cidadãos (síncrono)
  return crmStore.cidadaos.find(c => c.id === cidadaoId)
}

function subtituloCidadaoBusca(c: Cidadao): string {
  const partes = [c.telefone, c.cpf, c.bairro].filter(Boolean)
  return partes.join(' · ') || 'Sem contato cadastrado'
}

function getCidadaoCargo(cidadaoId: string, perfilAtivoId?: string): string {
  const cidadao = getCidadaoInfo(cidadaoId)
  if (!cidadao) return 'Sem cargo'
  
  // Se tem perfil ativo especificado, busca esse perfil
  if (perfilAtivoId && cidadao.perfis_profissionais) {
    const perfil = cidadao.perfis_profissionais.find(p => p.id === perfilAtivoId)
    if (perfil) return perfil.cargo
  }
  
  // Retorna o primeiro perfil profissional ou string padrão
  if (cidadao.perfis_profissionais && cidadao.perfis_profissionais.length > 0) {
    return cidadao.perfis_profissionais[0].cargo
  }
  
  return 'Sem cargo'
}

function getCidadaoInstituicao(cidadaoId: string, perfilAtivoId?: string): string {
  const cidadao = getCidadaoInfo(cidadaoId)
  if (!cidadao) return ''
  
  // Se tem perfil ativo especificado, busca esse perfil
  if (perfilAtivoId && cidadao.perfis_profissionais) {
    const perfil = cidadao.perfis_profissionais.find(p => p.id === perfilAtivoId)
    if (perfil) return perfil.instituicao
  }
  
  // Retorna a primeira instituição ou string vazia
  if (cidadao.perfis_profissionais && cidadao.perfis_profissionais.length > 0) {
    return cidadao.perfis_profissionais[0].instituicao
  }
  
  return ''
}

/** Dados vindos do cerimonial (API); CRM só como fallback (busca/edição). */
function convidadoNome(convidado: Convidado): string {
  const fromApi = convidado.cidadao?.nome?.trim()
  if (fromApi) return fromApi
  return getCidadaoInfo(convidado.cidadaoId)?.nome?.trim() || 'Convidado'
}

function convidadoCargo(convidado: Convidado): string {
  const fromApi = convidado.perfilAtivo?.cargo?.trim()
  if (fromApi) return fromApi
  const fromCrm = getCidadaoCargo(convidado.cidadaoId, convidado.perfil_ativo_id)
  return fromCrm === 'Sem cargo' && !getCidadaoInfo(convidado.cidadaoId) ? 'Sem cargo' : fromCrm
}

function convidadoInstituicao(convidado: Convidado): string {
  const fromApi = convidado.perfilAtivo?.instituicao?.trim()
  if (fromApi) return fromApi
  return getCidadaoInstituicao(convidado.cidadaoId, convidado.perfil_ativo_id)
}

function convidadoEmail(convidado: Convidado): string {
  return convidado.cidadao?.email?.trim() || getCidadaoInfo(convidado.cidadaoId)?.email?.trim() || '-'
}

function convidadoTelefone(convidado: Convidado): string {
  return convidado.cidadao?.telefone?.trim() || getCidadaoInfo(convidado.cidadaoId)?.telefone?.trim() || '-'
}

async function selecionarCidadao(cidadaoOrId: Cidadao | string) {
  const cidadao =
    typeof cidadaoOrId === 'string'
      ? getCidadaoInfo(cidadaoOrId) ?? (await crmStore.getCidadaoById(cidadaoOrId))
      : cidadaoOrId
  if (!cidadao) return
  const cidadaoId = cidadao.id
  
  // Verificar se tem múltiplos perfis
  if (cidadao.perfis_profissionais && cidadao.perfis_profissionais.length > 1) {
    // Mostrar seletor de perfil
    cidadaoSelecionado.value = cidadaoId
    perfilSelecionado.value = '' // Reset
    mostrarSeletorPerfil.value = true
    mostrarResultados.value = false
  } else {
    // Adicionar diretamente (com o primeiro perfil se houver)
    const perfilId = cidadao.perfis_profissionais && cidadao.perfis_profissionais.length > 0
      ? cidadao.perfis_profissionais[0].id
      : undefined
    await adicionarConvidadoComPerfil(cidadaoId, perfilId)
  }
}

async function confirmarSelecaoPerfil() {
  if (!cidadaoSelecionado.value || !perfilSelecionado.value) {
    showError('Selecione um perfil para continuar')
    return
  }
  
  await adicionarConvidadoComPerfil(cidadaoSelecionado.value, perfilSelecionado.value)
  
  // Reset
  mostrarSeletorPerfil.value = false
  cidadaoSelecionado.value = null
  perfilSelecionado.value = ''
}

function cancelarSelecaoPerfil() {
  mostrarSeletorPerfil.value = false
  cidadaoSelecionado.value = null
  perfilSelecionado.value = ''
  mostrarResultados.value = true
}

async function adicionarConvidadoComPerfil(cidadaoId: string, perfilAtivoId?: string) {
  try {
    await cerimonialStore.adicionarConvidado(props.eventoId, cidadaoId, perfilAtivoId)
    buscaCidadao.value = ''
    mostrarResultados.value = false
    showSuccess('Convidado adicionado com sucesso!')
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Erro ao adicionar convidado'
    showError(message)
  }
}

// Função legada - redireciona para selecionarCidadao
// async function adicionarConvidado(cidadaoId: string) {
//   await selecionarCidadao(cidadaoId)
// }

// Abrir modal para criar novo cidadão
function abrirModalNovoCidadao() {
  cidadaoEditando.value = null
  mostrarCidadaoModal.value = true
}

// Abrir modal para editar cidadão existente
async function editarCidadao(cidadaoId: string) {
  const cidadao = getCidadaoInfo(cidadaoId) ?? (await crmStore.getCidadaoById(cidadaoId))
  if (cidadao) {
    cidadaoEditando.value = cidadao
    mostrarCidadaoModal.value = true
  }
}

// Callback após criar/editar cidadão
async function handleCidadaoCriado(criado?: Cidadao) {
  if (!cidadaoEditando.value) {
    const ultimoCidadao = criado ?? crmStore.cidadaos[0]
    if (ultimoCidadao) {
      await selecionarCidadao(ultimoCidadao)
    }
  }
  // Se for edição, os dados do convidado já estão atualizados automaticamente via referência
  cidadaoEditando.value = null
  mostrarCidadaoModal.value = false
}

async function atualizarStatus(convidado: Convidado, novoStatus: Convidado['statusConfirmacao']) {
  await cerimonialStore.atualizarConvidado(props.eventoId, convidado.id, {
    statusConfirmacao: novoStatus
  })
}

async function toggleVip(convidado: Convidado) {
  await cerimonialStore.atualizarConvidado(props.eventoId, convidado.id, {
    isVip: !convidado.isVip
  })
}

function abrirFichaCerimonialista() {
  mostrarFichaCerimonialista.value = true
}

function imprimirFicha() {
  window.print()
}

async function removerConvidado(convidado: Convidado) {
  const confirmed = await showConfirm(`Remover ${convidadoNome(convidado)} da lista?`)
  
  if (confirmed) {
    await cerimonialStore.removerConvidado(props.eventoId, convidado.id)
    showSuccess('Convidado removido com sucesso!')
  }
}

function getStatusColor(status: Convidado['statusConfirmacao']) {
  const colors = {
    pendente: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
    confirmado: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
    recusado: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
  }
  return colors[status]
}

function abrirPrismas() {
  if (convidadosConfirmados.value.length === 0) {
    showError('Não há convidados confirmados para gerar prismas')
    return
  }
  mostrarPrismas.value = true
}

function imprimirPrismas() {
  window.print()
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header e Botão de Prismas -->
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
          Lista de Convidados
        </h3>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
          {{ convidados.length }} convidado(s) • {{ convidadosConfirmados.length }} confirmado(s)
        </p>
      </div>

      <button
        v-if="convidadosConfirmados.length > 0"
        @click="abrirFichaCerimonialista"
        class="flex items-center gap-2 px-4 py-2 bg-blue-100 hover:bg-blue-200 dark:bg-blue-900/30 dark:hover:bg-blue-900/50 text-blue-700 dark:text-blue-400 rounded-lg font-medium transition-colors"
      >
        <FileText class="w-5 h-5" />
        Ficha do Cerimonial
      </button>

      <button
        v-if="convidadosConfirmados.length > 0"
        @click="abrirPrismas"
        class="flex items-center gap-2 px-4 py-2 bg-purple-100 hover:bg-purple-200 dark:bg-purple-900/30 dark:hover:bg-purple-900/50 text-purple-700 dark:text-purple-400 rounded-lg font-medium transition-colors"
      >
        <Printer class="w-5 h-5" />
        Gerar Prismas de Mesa
      </button>
    </div>

    <!-- Busca e Adicionar Convidado -->
    <div class="bg-gray-50 dark:bg-gray-700/30 rounded-lg border border-gray-200 dark:border-gray-600 p-4">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Adicionar Convidado
      </label>
      
      <div class="flex gap-2">
        <div class="relative flex-1">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            v-model="buscaCidadao"
            type="text"
            placeholder="Nome, CPF ou telefone (mín. 2 caracteres)"
            class="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400"
            @focus="mostrarResultados = buscaCidadao.trim().length >= 2"
          />

          <!-- Resultados de Busca -->
        <Transition
          enter-active-class="transition ease-out duration-200"
          enter-from-class="opacity-0 -translate-y-2"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition ease-in duration-150"
          leave-from-class="opacity-100 translate-y-0"
          leave-to-class="opacity-0 -translate-y-2"
        >
          <div
            v-if="mostrarResultados && buscaCidadao.trim().length >= 2"
            class="absolute z-10 mt-2 w-full bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 max-h-60 overflow-y-auto"
          >
            <p
              v-if="buscandoCrm"
              class="px-4 py-3 text-sm text-gray-500 dark:text-slate-400"
            >
              Buscando no CRM…
            </p>
            <p
              v-else-if="erroBuscaCrm"
              class="px-4 py-3 text-sm text-red-600 dark:text-red-400"
            >
              {{ erroBuscaCrm }}
            </p>
            <p
              v-else-if="resultadosBusca.length === 0"
              class="px-4 py-3 text-sm text-gray-500 dark:text-slate-400"
            >
              Nenhum cidadão encontrado. Use «Novo» para cadastrar.
            </p>
            <template v-else>
              <button
                v-for="cidadao in resultadosBusca"
                :key="cidadao.id"
                type="button"
                @click="selecionarCidadao(cidadao)"
                class="w-full flex items-center gap-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors text-left border-b border-gray-100 dark:border-gray-700 last:border-0"
              >
                <UserPlus class="w-5 h-5 text-primary-600 dark:text-primary-400 flex-shrink-0" />
                <div class="flex-1 min-w-0">
                  <p class="font-medium text-gray-900 dark:text-gray-100">
                    {{ cidadao.nome }}
                  </p>
                  <p class="text-sm text-gray-500 dark:text-gray-400 truncate">
                    {{ subtituloCidadaoBusca(cidadao) }}
                  </p>
                </div>
              </button>
            </template>
          </div>
        </Transition>
        </div>

        <!-- Botão Novo Cidadão -->
        <button
          @click="abrirModalNovoCidadao"
          type="button"
          class="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors whitespace-nowrap h-[42px]"
        >
          <UserPlus class="w-5 h-5" />
          Novo
        </button>
      </div>
    </div>

    <!-- Lista Drag-and-Drop de Convidados -->
    <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
      <div class="mb-4 flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
        <GripVertical class="w-4 h-4" />
        <span>Arraste e solte para reordenar a precedência</span>
      </div>

      <draggable
        v-model="convidadosLocal"
        item-key="id"
        :animation="200"
        handle=".drag-handle"
        ghost-class="opacity-50"
        @start="drag = true"
        @end="onDragEnd"
        class="space-y-2"
      >
        <template #item="{ element: convidado, index }">
          <div
            :class="[
              'flex items-center gap-4 p-4 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-600 rounded-lg transition-all',
              drag ? 'cursor-grabbing' : 'hover:border-primary-400 dark:hover:border-primary-600'
            ]"
          >
            <!-- Drag Handle -->
            <div class="drag-handle cursor-grab active:cursor-grabbing flex items-center gap-2">
              <GripVertical class="w-5 h-5 text-gray-400" />
              <span class="text-sm font-bold text-gray-700 dark:text-gray-300 w-6">
                {{ index + 1 }}º
              </span>
            </div>

            <!-- Info Convidado -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <Crown
                  v-if="convidado.isVip"
                  class="w-5 h-5 text-yellow-500 fill-current"
                  title="VIP"
                />
                <span class="font-semibold text-gray-900 dark:text-gray-100">
                  {{ convidadoNome(convidado) }}
                </span>
              </div>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                {{ convidadoCargo(convidado) }}
                <span v-if="convidadoInstituicao(convidado)" class="ml-1">
                  - {{ convidadoInstituicao(convidado) }}
                </span>
              </p>
            </div>

            <!-- Status -->
            <select
              :value="convidado.statusConfirmacao"
              @change="atualizarStatus(convidado, ($event.target as HTMLSelectElement).value as Convidado['statusConfirmacao'])"
              :class="[
                getStatusColor(convidado.statusConfirmacao),
                'px-3 py-1.5 rounded-full text-xs font-medium focus:outline-none focus:ring-2 focus:ring-primary-500 cursor-pointer'
              ]"
            >
              <option value="pendente" class="bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">Pendente</option>
              <option value="confirmado" class="bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">Confirmado</option>
              <option value="recusado" class="bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">Recusado</option>
            </select>

            <!-- Botão VIP -->
            <button
              @click="toggleVip(convidado)"
              :class="[
                convidado.isVip
                  ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
                  : 'bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-400',
                'p-2 rounded-lg transition-colors hover:opacity-80'
              ]"
              :title="convidado.isVip ? 'Remover VIP' : 'Marcar como VIP'"
            >
              <Star
                :class="[
                  convidado.isVip ? 'fill-current' : '',
                  'w-5 h-5'
                ]"
              />
            </button>

            <!-- Botão Editar -->
            <button
              @click="editarCidadao(convidado.cidadaoId)"
              class="p-2 text-primary-600 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/20 rounded-lg transition-colors"
              title="Editar dados do convidado"
            >
              <SquarePen class="w-5 h-5" />
            </button>

            <!-- Botão Remover -->
            <button
              @click="removerConvidado(convidado)"
              class="p-2 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
              title="Remover convidado"
            >
              <Trash2 class="w-5 h-5" />
            </button>
          </div>
        </template>
      </draggable>

      <!-- Estado Vazio -->
      <div v-if="convidados.length === 0" class="text-center py-16">
        <UserPlus class="w-12 h-12 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
        <p class="text-gray-500 dark:text-gray-400">
          Nenhum convidado adicionado ainda
        </p>
      </div>
    </div>

    <!-- Modal de Prismas de Mesa -->
    <Transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="mostrarPrismas"
        class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 print:bg-white print:relative print:block"
        @click.self="mostrarPrismas = false"
      >
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col print:max-w-none print:shadow-none print:max-h-none">
          <!-- Header do Modal (oculto na impressão) -->
          <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 print:hidden">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
              Prismas de Mesa
            </h3>
            <div class="flex items-center gap-2">
              <button
                @click="imprimirPrismas"
                class="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors"
              >
                <Printer class="w-4 h-4" />
                Imprimir
              </button>
              <button
                @click="mostrarPrismas = false"
                class="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded transition-colors"
              >
                <X class="w-5 h-5" />
              </button>
            </div>
          </div>

          <!-- Conteúdo dos Prismas (otimizado para impressão) -->
          <div class="flex-1 overflow-y-auto p-8 print:p-0 print:overflow-visible">
            <div
              v-for="convidado in convidadosConfirmados"
              :key="convidado.id"
              class="page-break mb-8 print:mb-0"
            >
              <!-- Prisma (formato A4 dobrado ao meio) -->
              <div class="bg-white h-[297mm] w-[210mm] mx-auto flex flex-col print:h-[297mm] print:w-[210mm]">
                <!-- Lado 1 (Normal) -->
                <div class="flex-1 flex flex-col items-center justify-center p-8 border-b-2 border-dashed border-gray-300">
                  <h1 class="text-7xl font-bold text-gray-900 text-center mb-4 leading-tight">
                    {{ convidadoNome(convidado) }}
                  </h1>
                  <p class="text-3xl text-gray-600 text-center">
                    {{ convidadoCargo(convidado) }}
                  </p>
                  <p v-if="convidadoInstituicao(convidado)" class="text-2xl text-gray-500 text-center mt-2">
                    {{ convidadoInstituicao(convidado) }}
                  </p>
                  <Crown
                    v-if="convidado.isVip"
                    class="w-16 h-16 text-yellow-500 mt-6"
                  />
                </div>

                <!-- Lado 2 (Rotacionado 180°) -->
                <div class="flex-1 flex flex-col items-center justify-center p-8 transform rotate-180">
                  <h1 class="text-7xl font-bold text-gray-900 text-center mb-4 leading-tight">
                    {{ convidadoNome(convidado) }}
                  </h1>
                  <p class="text-3xl text-gray-600 text-center">
                    {{ convidadoCargo(convidado) }}
                  </p>
                  <p v-if="convidadoInstituicao(convidado)" class="text-2xl text-gray-500 text-center mt-2">
                    {{ convidadoInstituicao(convidado) }}
                  </p>
                  <Crown
                    v-if="convidado.isVip"
                    class="w-16 h-16 text-yellow-500 mt-6"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Modal: Ficha do Cerimonialista -->
    <Transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="mostrarFichaCerimonialista"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm print:hidden"
        @click.self="mostrarFichaCerimonialista = false"
      >
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
          <!-- Header Modal -->
          <div class="sticky top-0 bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-4 flex items-center justify-between print:hidden">
            <h2 class="text-xl font-bold text-white">Ficha do Cerimonial</h2>
            <div class="flex items-center gap-2">
              <button
                @click="imprimirFicha"
                class="px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg transition-colors flex items-center gap-2"
              >
                <Printer class="w-4 h-4" />
                Imprimir
              </button>
              <button
                @click="mostrarFichaCerimonialista = false"
                class="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
              >
                <X class="w-5 h-5" />
              </button>
            </div>
          </div>

          <!-- Cards de Autoridades VIP -->
          <div class="p-6 space-y-6">
            <div class="print:block">
              <div
                v-for="(convidado, index) in convidadosConfirmados.filter(c => c.isVip)"
                :key="convidado.id"
                :class="['page-break', index > 0 ? 'mt-6' : '']"
              >
                <div class="bg-white border-4 border-primary-600 rounded-xl p-8 shadow-2xl">
                  <div class="flex items-start gap-6">
                    <div class="flex-shrink-0">
                      <div class="w-24 h-24 bg-gradient-to-br from-primary-500 to-purple-600 rounded-full flex items-center justify-center">
                        <Crown class="w-12 h-12 text-white fill-current" />
                      </div>
                    </div>

                    <div class="flex-1">
                      <div class="flex items-center gap-3 mb-3">
                        <span class="text-6xl font-bold text-primary-600">{{ index + 1 }}º</span>
                        <div>
                          <h3 class="text-4xl font-bold text-gray-900 leading-tight">
                            {{ convidadoNome(convidado) }}
                          </h3>
                          <p class="text-2xl text-gray-600 mt-1">
                            {{ convidadoCargo(convidado) }}
                            <span v-if="convidadoInstituicao(convidado)" class="ml-2 text-gray-500">
                              - {{ convidadoInstituicao(convidado) }}
                            </span>
                          </p>
                        </div>
                      </div>

                      <!-- Mini-bio do CRM -->
                      <div class="mt-4 p-4 bg-gray-50 rounded-lg">
                        <h4 class="text-sm font-semibold text-gray-700 mb-2">INFORMAÇÕES PARA APRESENTAÇÃO:</h4>
                        <p class="text-base text-gray-700 leading-relaxed">
                          {{ getCidadaoInfo(convidado.cidadaoId)?.observacoes || 'Sem informações adicionais cadastradas.' }}
                        </p>
                      </div>

                      <!-- Dados de contato (se precisar) -->
                      <div class="mt-4 grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span class="font-medium text-gray-600">Email:</span>
                          <p class="text-gray-900">{{ convidadoEmail(convidado) }}</p>
                        </div>
                        <div>
                          <span class="font-medium text-gray-600">Telefone:</span>
                          <p class="text-gray-900">{{ convidadoTelefone(convidado) }}</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Badge VIP -->
                  <div class="absolute top-4 right-4 px-4 py-2 bg-yellow-500 text-white font-bold rounded-full shadow-lg print:hidden">
                    ★ VIP ★
                  </div>
                </div>
              </div>

              <!-- Estado vazio -->
              <div v-if="convidadosConfirmados.filter(c => c.isVip).length === 0" class="text-center py-16">
                <Crown class="w-16 h-16 mx-auto text-gray-300 mb-4" />
                <p class="text-gray-500 text-lg">
                  Nenhuma autoridade VIP confirmada ainda
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>

  <!-- Modal de Criação/Edição de Cidadão (Cross-Module) -->
  <!-- Modal de Seleção de Perfil -->
  <Transition
    enter-active-class="transition-opacity duration-200"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition-opacity duration-200"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div v-if="mostrarSeletorPerfil" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[100] p-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          Selecione o Perfil Atuante
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
          {{ cidadaoSelecionado ? getCidadaoInfo(cidadaoSelecionado)?.nome : '' }} possui múltiplos perfis. Selecione qual perfil será usado neste evento:
        </p>

        <div class="space-y-2 mb-6">
          <label
            v-for="perfil in cidadaoSelecionado ? getCidadaoInfo(cidadaoSelecionado)?.perfis_profissionais : []"
            :key="perfil.id"
            class="flex items-start gap-3 p-3 border-2 rounded-lg cursor-pointer transition-colors"
            :class="[
              perfilSelecionado === perfil.id
                ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
            ]"
          >
            <input
              type="radio"
              :value="perfil.id"
              v-model="perfilSelecionado"
              class="mt-1"
            />
            <div class="flex-1">
              <p class="font-medium text-gray-900 dark:text-gray-100">
                {{ perfil.cargo }}
              </p>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                em {{ perfil.instituicao }}
              </p>
              <span
                v-if="perfil.tag_id"
                :style="{
                  backgroundColor: crmStore.tagsDisponiveis.find(t => t.id === perfil.tag_id)?.cor + '20' || '#e5e7eb',
                  color: crmStore.tagsDisponiveis.find(t => t.id === perfil.tag_id)?.cor || '#6b7280'
                }"
                class="inline-block mt-1 px-2 py-0.5 rounded text-xs font-medium"
              >
                {{ crmStore.tagsDisponiveis.find(t => t.id === perfil.tag_id)?.nome || 'Sem Tag' }}
              </span>
            </div>
          </label>
        </div>

        <div class="flex justify-end gap-3">
          <button
            @click="cancelarSelecaoPerfil"
            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            Cancelar
          </button>
          <button
            @click="confirmarSelecaoPerfil"
            :disabled="!perfilSelecionado"
            class="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:bg-gray-300 dark:disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg transition-colors"
          >
            Confirmar
          </button>
        </div>
      </div>
    </div>
  </Transition>

  <!-- Modal de Criar/Editar Cidadão -->
  <CidadaoModal
    v-model="mostrarCidadaoModal"
    :cidadao="cidadaoEditando"
    @success="handleCidadaoCriado"
  />
</template>

<style scoped>
@media print {
  body {
    print-color-adjust: exact;
    -webkit-print-color-adjust: exact;
  }

  .page-break {
    page-break-after: always;
  }

  .page-break:last-child {
    page-break-after: auto;
  }
}
</style>
