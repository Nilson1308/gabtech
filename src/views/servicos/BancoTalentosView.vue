<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import draggable from 'vuedraggable'
import { useServicosStore } from '@/stores/servicos'
import { useCrmStore } from '@/stores/crm'
import { useAuthStore } from '@/stores/auth'
import { PERMS } from '@/constants/rbac'
import type { CandidaturaTalento, StatusProcessoTalento } from '@/types'
import Button from '@/components/common/Button.vue'
import NovaCandidaturaModal from '@/components/servicos/NovaCandidaturaModal.vue'
import TagsAlvoSelect from '@/components/servicos/TagsAlvoSelect.vue'
import ServicosCrudMenu from '@/components/servicos/ServicosCrudMenu.vue'
import RastreabilidadeMeta from '@/components/common/RastreabilidadeMeta.vue'
import { AUDITORIA_ALVO } from '@/services/auditoria'
import { useAlertDialog } from '@/composables/useAlertDialog'
import type { StatusVagaEmprego, VagaEmprego } from '@/types'
import { ExternalLink, FileText, Plus, UserPlus } from 'lucide-vue-next'

const servicosStore = useServicosStore()
const crmStore = useCrmStore()
const authStore = useAuthStore()
const { showConfirm, showError } = useAlertDialog()

const podeGerenciar = computed(() => authStore.hasPermission(PERMS.servicosTalentos))

const STATUS_VAGA: Array<{ value: StatusVagaEmprego; label: string }> = [
  { value: 'aberta', label: 'Aberta' },
  { value: 'pausada', label: 'Pausada' },
  { value: 'preenchida', label: 'Preenchida' },
]

const vagaSelecionadaId = ref<string | null>(null)

const colunas: Array<{ titulo: string; status: StatusProcessoTalento; cor: string }> = [
  { titulo: 'Triagem', status: 'triagem', cor: '#6b7280' },
  { titulo: 'Encaminhado', status: 'encaminhado', cor: '#3b82f6' },
  { titulo: 'Entrevista', status: 'entrevista', cor: '#f59e0b' },
  { titulo: 'Contratado', status: 'contratado', cor: '#10b981' },
  { titulo: 'Recusado', status: 'recusado', cor: '#ef4444' },
]

const listas = ref<Record<StatusProcessoTalento, CandidaturaTalento[]>>({
  triagem: [],
  encaminhado: [],
  entrevista: [],
  contratado: [],
  recusado: [],
})

function sincronizarListas() {
  const base = vagaSelecionadaId.value
    ? servicosStore.candidaturas.filter(c => c.vagaId === vagaSelecionadaId.value)
    : servicosStore.candidaturas

  for (const col of colunas) {
    listas.value[col.status] = base.filter(c => c.statusProcesso === col.status)
  }
}

watch(() => servicosStore.candidaturas, sincronizarListas, { deep: true, immediate: true })
watch(vagaSelecionadaId, sincronizarListas)

onMounted(async () => {
  await crmStore.fetchTags()
  await servicosStore.carregarBancoTalentos()
  if (servicosStore.vagas.length > 0) {
    vagaSelecionadaId.value = servicosStore.vagas[0].id
  }
})

const vagasFiltradas = computed(() => servicosStore.vagas)

async function handleDragChange(
  event: { added?: { element: CandidaturaTalento } },
  statusColuna: StatusProcessoTalento,
) {
  if (!event.added || !podeGerenciar.value) {
    if (event.added) sincronizarListas()
    return
  }
  const item = event.added.element
  if (item.statusProcesso === statusColuna) return

  const ok = await servicosStore.updateStatusCandidatura(item.id, statusColuna)
  if (!ok) {
    await servicosStore.fetchCandidaturas(vagaSelecionadaId.value ?? undefined)
    return
  }
  item.statusProcesso = statusColuna
}

const mostrarNovaCandidatura = ref(false)

const vagaSelecionada = computed(() =>
  servicosStore.vagas.find(v => v.id === vagaSelecionadaId.value) ?? null,
)

const idsCandidatosNaVaga = computed(() => {
  if (!vagaSelecionadaId.value) return []
  return servicosStore.candidaturas
    .filter(c => c.vagaId === vagaSelecionadaId.value)
    .map(c => c.candidatoId)
})

async function aoVincularCandidato() {
  if (vagaSelecionadaId.value) {
    await servicosStore.fetchCandidaturas(vagaSelecionadaId.value)
  }
}

const mostrarFormVaga = ref(false)
const vagaEmEdicaoId = ref<string | null>(null)
const formVagaTitulo = ref('')
const formVagaEmpresa = ref('')
const formVagaDescricao = ref('')
const formVagaRequisitos = ref('')
const formVagaStatus = ref<StatusVagaEmprego>('aberta')
const formVagaTagsAlvoIds = ref<string[]>([])
const formVagaErro = ref('')

function limparFormVaga() {
  vagaEmEdicaoId.value = null
  formVagaTitulo.value = ''
  formVagaEmpresa.value = ''
  formVagaDescricao.value = ''
  formVagaRequisitos.value = ''
  formVagaStatus.value = 'aberta'
  formVagaTagsAlvoIds.value = []
  formVagaErro.value = ''
}

function abrirNovaVaga() {
  limparFormVaga()
  mostrarFormVaga.value = true
}

function abrirEditarVaga(vaga: VagaEmprego) {
  vagaEmEdicaoId.value = vaga.id
  formVagaTitulo.value = vaga.titulo
  formVagaEmpresa.value = vaga.empresaParceira
  formVagaDescricao.value = vaga.descricao ?? ''
  formVagaRequisitos.value = vaga.requisitos ?? ''
  formVagaStatus.value = vaga.status
  formVagaTagsAlvoIds.value = [...vaga.tagsAlvoIds]
  mostrarFormVaga.value = true
  formVagaErro.value = ''
}

async function salvarFormVaga() {
  formVagaErro.value = ''
  if (!formVagaTitulo.value.trim()) {
    formVagaErro.value = 'Informe o título da vaga.'
    return
  }
  if (vagaEmEdicaoId.value) {
    const { vaga, erro } = await servicosStore.updateVaga(vagaEmEdicaoId.value, {
      titulo: formVagaTitulo.value.trim(),
      empresaParceira: formVagaEmpresa.value.trim() || 'Parceiro',
      descricao: formVagaDescricao.value.trim(),
      requisitos: formVagaRequisitos.value.trim(),
      status: formVagaStatus.value,
      tagsAlvoIds: [...formVagaTagsAlvoIds.value],
    })
    if (erro) formVagaErro.value = erro
    else if (vaga) {
      mostrarFormVaga.value = false
      limparFormVaga()
    }
    return
  }
  const eixo = servicosStore.eixos.find(e => e.nome === 'Banco de Talentos') ?? servicosStore.eixos[0]
  if (!eixo) return
  const vaga = await servicosStore.createVaga({
    eixoId: eixo.id,
    titulo: formVagaTitulo.value.trim(),
    empresaParceira: formVagaEmpresa.value.trim() || 'Parceiro',
    descricao: formVagaDescricao.value.trim(),
    requisitos: formVagaRequisitos.value.trim(),
    status: formVagaStatus.value,
    tagsAlvoIds: [...formVagaTagsAlvoIds.value],
  })
  if (vaga) {
    vagaSelecionadaId.value = vaga.id
    mostrarFormVaga.value = false
    limparFormVaga()
    await servicosStore.fetchCandidaturas(vaga.id)
  } else {
    formVagaErro.value = 'Não foi possível criar a vaga.'
  }
}

async function excluirVaga(vaga: VagaEmprego) {
  const ok = await showConfirm(
    `Excluir a vaga «${vaga.titulo}»? Todas as candidaturas serão removidas.`,
    'Excluir vaga',
  )
  if (!ok) return
  const { ok: done, erro } = await servicosStore.deleteVaga(vaga.id)
  if (!done) await showError(erro ?? 'Erro ao excluir.')
  else if (vagaSelecionadaId.value === vaga.id) {
    vagaSelecionadaId.value = servicosStore.vagas[0]?.id ?? null
  }
}

const candidaturaEditandoObs = ref<string | null>(null)
const obsRascunho = ref('')

function editarObservacoes(c: CandidaturaTalento) {
  candidaturaEditandoObs.value = c.id
  obsRascunho.value = c.observacoes ?? ''
}

async function salvarObservacoes(c: CandidaturaTalento) {
  const { erro } = await servicosStore.updateCandidatura(c.id, { observacoes: obsRascunho.value.trim() })
  if (erro) await showError(erro)
  candidaturaEditandoObs.value = null
}

async function removerCandidatura(c: CandidaturaTalento) {
  const ok = await showConfirm(
    `Remover ${c.candidato.nome} desta vaga?`,
    'Remover candidatura',
  )
  if (!ok) return
  const { ok: done, erro } = await servicosStore.deleteCandidatura(c.id)
  if (!done) await showError(erro ?? 'Erro ao remover.')
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
      <p class="text-sm text-gray-600 dark:text-slate-400 max-w-xl">
        Vagas, tags alvo e pipeline de candidatos vinculados ao CRM.
      </p>
      <div v-if="podeGerenciar" class="flex flex-wrap gap-2">
        <Button
          variant="secondary"
          :disabled="!vagaSelecionadaId"
          @click="mostrarNovaCandidatura = true"
        >
          <UserPlus class="w-4 h-4" />
          Vincular candidato
        </Button>
        <Button variant="primary" @click="abrirNovaVaga">
          <Plus class="w-4 h-4" />
          Nova vaga
        </Button>
      </div>
    </div>

    <div v-if="mostrarFormVaga && podeGerenciar" class="card space-y-3">
      <h4 class="text-sm font-semibold">
        {{ vagaEmEdicaoId ? 'Editar vaga' : 'Nova vaga' }}
      </h4>
      <div class="grid gap-3 md:grid-cols-2">
        <input v-model="formVagaTitulo" type="text" placeholder="Título da vaga" class="input" />
        <input v-model="formVagaEmpresa" type="text" placeholder="Empresa parceira" class="input" />
        <select v-model="formVagaStatus" class="input">
          <option v-for="s in STATUS_VAGA" :key="s.value" :value="s.value">{{ s.label }}</option>
        </select>
      </div>
      <textarea v-model="formVagaDescricao" rows="2" class="input" placeholder="Descrição" />
      <textarea v-model="formVagaRequisitos" rows="2" class="input" placeholder="Requisitos" />
      <TagsAlvoSelect v-model="formVagaTagsAlvoIds" />
      <div class="flex flex-wrap gap-2">
        <Button variant="secondary" @click="salvarFormVaga">Salvar</Button>
        <Button variant="ghost" @click="mostrarFormVaga = false; limparFormVaga()">Cancelar</Button>
      </div>
      <p v-if="formVagaErro" class="text-sm text-red-600">{{ formVagaErro }}</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6 items-start">
      <!-- Vagas -->
      <div class="card lg:col-span-1 space-y-2">
        <h3 class="font-semibold text-gray-900 dark:text-slate-100">Vagas abertas</h3>
        <div
          v-for="vaga in vagasFiltradas"
          :key="vaga.id"
          class="w-full text-left p-3 rounded-lg border transition-colors flex gap-2"
          :class="
            vagaSelecionadaId === vaga.id
              ? 'border-indigo-500 bg-indigo-50 dark:bg-indigo-900/20'
              : 'border-gray-200 dark:border-slate-700 hover:border-indigo-300'
          "
        >
          <button
            type="button"
            class="flex-1 min-w-0 text-left"
            @click="vagaSelecionadaId = vaga.id; servicosStore.fetchCandidaturas(vaga.id)"
          >
          <p class="font-medium text-sm text-gray-900 dark:text-slate-100">{{ vaga.titulo }}</p>
          <p class="text-xs text-gray-500 dark:text-slate-400">
            {{ vaga.empresaParceira }} · {{ STATUS_VAGA.find(s => s.value === vaga.status)?.label ?? vaga.status }}
          </p>
          <RastreabilidadeMeta
            :rastreabilidade="vaga.rastreabilidade"
            :alvo-auditoria="AUDITORIA_ALVO.vagaEmprego(vaga.id)"
            historico-titulo="Histórico da vaga"
            compact
            class="mt-1"
          />
          <div v-if="vaga.tagsAlvo.length" class="flex flex-wrap gap-1 mt-1.5">
            <span
              v-for="tag in vaga.tagsAlvo"
              :key="tag.id"
              class="text-[10px] px-1.5 py-0.5 rounded-full"
              :style="{ backgroundColor: tag.cor + '22', color: tag.cor }"
            >
              {{ tag.nome }}
            </span>
          </div>
          </button>
          <ServicosCrudMenu
            v-if="podeGerenciar"
            @edit="abrirEditarVaga(vaga)"
            @delete="excluirVaga(vaga)"
          />
        </div>
        <p v-if="vagasFiltradas.length === 0" class="text-sm text-gray-500">Nenhuma vaga cadastrada.</p>
      </div>

      <!-- Kanban -->
      <div class="lg:col-span-3">
        <div v-if="servicosStore.loading" class="py-12 text-center text-gray-500">Carregando…</div>
        <div
          v-else
          class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-3 items-start"
        >
          <div
            v-for="coluna in colunas"
            :key="coluna.status"
            class="bg-gray-50 dark:bg-slate-800 rounded-lg p-3 min-h-[200px]"
          >
            <div
              class="flex items-center justify-between mb-3 pb-2 border-b-2"
              :style="{ borderColor: coluna.cor }"
            >
              <span class="text-sm font-semibold text-gray-900 dark:text-slate-100">{{ coluna.titulo }}</span>
              <span
                class="text-xs px-2 py-0.5 rounded-full"
                :style="{ backgroundColor: coluna.cor + '22', color: coluna.cor }"
              >
                {{ listas[coluna.status].length }}
              </span>
            </div>

            <draggable
              :list="listas[coluna.status]"
              group="candidaturas-talento"
              item-key="id"
              class="space-y-2 min-h-[80px]"
              ghost-class="opacity-50"
              :disabled="!podeGerenciar"
              @change="(evt: { added?: { element: CandidaturaTalento } }) => handleDragChange(evt, coluna.status)"
            >
              <template #item="{ element: c }">
                <div class="bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-lg p-3 shadow-sm">
                  <div class="flex items-start justify-between gap-1">
                    <p class="font-medium text-sm text-gray-900 dark:text-slate-100">{{ c.candidato.nome }}</p>
                    <ServicosCrudMenu
                      v-if="podeGerenciar"
                      :show-edit="false"
                      @delete="removerCandidatura(c)"
                    />
                  </div>
                  <p class="text-xs text-gray-500 dark:text-slate-400 mt-0.5">{{ c.candidato.telefone }}</p>
                  <p v-if="c.candidato.bairro" class="text-xs text-gray-400">{{ c.candidato.bairro }}</p>
                  <RastreabilidadeMeta
                    :rastreabilidade="c.rastreabilidade"
                    :alvo-auditoria="AUDITORIA_ALVO.candidatura(c.id)"
                    historico-titulo="Histórico da candidatura"
                    compact
                    class="mt-1"
                  />
                  <div
                    v-if="c.curriculo?.etiquetas?.length"
                    class="flex flex-wrap gap-1 mt-2"
                  >
                    <span
                      v-for="tag in c.curriculo.etiquetas"
                      :key="tag.id"
                      class="text-[10px] px-1.5 py-0.5 rounded-full"
                      :style="{ backgroundColor: tag.cor + '22', color: tag.cor }"
                    >
                      {{ tag.nome }}
                    </span>
                  </div>
                  <a
                    v-if="c.curriculo?.urlDownload"
                    :href="c.curriculo.urlDownload"
                    target="_blank"
                    rel="noopener"
                    class="inline-flex items-center gap-1 mt-2 text-xs text-indigo-600 dark:text-indigo-400 hover:underline"
                    @click.stop
                  >
                    <FileText class="w-3 h-3" />
                    Currículo
                    <ExternalLink class="w-3 h-3" />
                  </a>
                  <p v-else class="text-xs text-amber-600 dark:text-amber-400 mt-2">Sem currículo compatível</p>
                  <div v-if="podeGerenciar" class="mt-2 border-t border-gray-100 dark:border-slate-800 pt-2">
                    <template v-if="candidaturaEditandoObs === c.id">
                      <textarea v-model="obsRascunho" rows="2" class="input text-xs" placeholder="Observações" />
                      <div class="flex gap-1 mt-1">
                        <button type="button" class="text-xs text-primary-600" @click="salvarObservacoes(c)">Salvar</button>
                        <button type="button" class="text-xs text-gray-500" @click="candidaturaEditandoObs = null">Cancelar</button>
                      </div>
                    </template>
                    <button
                      v-else
                      type="button"
                      class="text-xs text-gray-500 hover:text-gray-800 dark:hover:text-slate-200"
                      @click="editarObservacoes(c)"
                    >
                      {{ c.observacoes ? 'Editar observações' : 'Adicionar observações' }}
                    </button>
                    <p v-if="candidaturaEditandoObs !== c.id && c.observacoes" class="text-xs text-gray-500 mt-1 line-clamp-2">
                      {{ c.observacoes }}
                    </p>
                  </div>
                </div>
              </template>
            </draggable>
          </div>
        </div>
        <p
          v-if="!podeGerenciar"
          class="text-sm text-gray-500 dark:text-slate-400 mt-4"
        >
          Seu perfil pode visualizar o pipeline, mas não mover candidatos entre etapas.
        </p>
      </div>
    </div>

    <NovaCandidaturaModal
      v-model="mostrarNovaCandidatura"
      :vaga-id="vagaSelecionadaId"
      :vaga-titulo="vagaSelecionada?.titulo"
      :vaga-tags-alvo="vagaSelecionada?.tagsAlvo ?? []"
      :candidatos-ja-na-vaga="idsCandidatosNaVaga"
      @success="aoVincularCandidato"
    />
  </div>
</template>
