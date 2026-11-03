<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useServicosStore } from '@/stores/servicos'
import { ApiError } from '@/services/api'
import type { SugestaoMatchmaking, TagResumo } from '@/types'
import Modal from '@/components/common/Modal.vue'
import Button from '@/components/common/Button.vue'
import SugestoesMatchList from '@/components/servicos/SugestoesMatchList.vue'
import CidadaoBuscaSelect from '@/components/crm/CidadaoBuscaSelect.vue'
import { FileText, UserPlus } from 'lucide-vue-next'

interface Props {
  modelValue: boolean
  vagaId: string | null
  vagaTitulo?: string
  vagaTagsAlvo?: TagResumo[]
  /** @deprecated use vagaTagsAlvo */
  vagaEtiquetas?: TagResumo[]
  candidatosJaNaVaga: string[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

const servicosStore = useServicosStore()

const tagsVaga = computed(() => props.vagaTagsAlvo ?? props.vagaEtiquetas ?? [])

const sugestoesInteligentes = ref<SugestaoMatchmaking[]>([])
const carregandoMatch = ref(false)
const erroBusca = ref('')
const candidatoManualId = ref<string | null>(null)
const observacoes = ref('')
const salvando = ref(false)
const erroSalvar = ref('')
const processandoId = ref<string | null>(null)

const searchOptions = computed(() => {
  const tagIds = tagsVaga.value.map(t => t.id)
  return {
    anexoCategoria: 'curriculo' as const,
    curriculoTagIds: tagIds.length > 0 ? tagIds : undefined,
  }
})

function fechar() {
  emit('update:modelValue', false)
}

function resetar() {
  sugestoesInteligentes.value = []
  candidatoManualId.value = null
  observacoes.value = ''
  erroBusca.value = ''
  erroSalvar.value = ''
  processandoId.value = null
}

watch(
  () => props.modelValue,
  aberto => {
    if (aberto) {
      resetar()
      carregarMatchmaking()
    }
  },
)

async function carregarMatchmaking() {
  if (!props.vagaId) return
  carregandoMatch.value = true
  erroBusca.value = ''
  try {
    sugestoesInteligentes.value = await servicosStore.fetchSugerirCandidatos(props.vagaId, 30)
  } catch (e) {
    sugestoesInteligentes.value = []
    erroBusca.value = mensagemErroBusca(e)
  } finally {
    carregandoMatch.value = false
  }
}

function mensagemErroBusca(e: unknown): string {
  if (e instanceof ApiError) {
    if (e.status === 403) return 'Sem permissão para consultar cidadãos.'
    if (e.status === 401) return 'Sessão expirada. Faça login novamente.'
  }
  return 'Não foi possível carregar sugestões.'
}

async function vincularCandidato(candidatoId: string) {
  if (!props.vagaId) return
  salvando.value = true
  processandoId.value = candidatoId
  erroSalvar.value = ''
  try {
    const { candidatura, erro } = await servicosStore.createCandidatura({
      vagaId: props.vagaId,
      candidatoId,
      observacoes: observacoes.value.trim(),
    })
    if (!candidatura) {
      erroSalvar.value = erro ?? 'Não foi possível criar a candidatura.'
      return
    }
    emit('success')
    fechar()
  } finally {
    salvando.value = false
    processandoId.value = null
  }
}

function acaoSugestao(s: SugestaoMatchmaking) {
  vincularCandidato(s.cidadao.id)
}

async function vincularManual() {
  if (!candidatoManualId.value) {
    erroSalvar.value = 'Selecione um cidadão na busca.'
    return
  }
  await vincularCandidato(candidatoManualId.value)
}
</script>

<template>
  <Modal
    :model-value="modelValue"
    titulo="Vincular candidato à vaga"
    largura="md"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <div class="space-y-5">
      <p v-if="vagaTitulo" class="text-sm text-gray-600 dark:text-slate-400">
        Vaga:
        <span class="font-medium text-gray-900 dark:text-slate-100">{{ vagaTitulo }}</span>
      </p>

      <div v-if="tagsVaga.length" class="flex flex-wrap gap-1.5">
        <span
          v-for="tag in tagsVaga"
          :key="tag.id"
          class="text-xs px-2 py-0.5 rounded-full font-medium"
          :style="{ backgroundColor: tag.cor + '22', color: tag.cor }"
        >
          {{ tag.nome }}
        </span>
      </div>

      <p v-if="erroBusca" class="text-sm text-red-600 dark:text-red-400">{{ erroBusca }}</p>

      <SugestoesMatchList
        :sugestoes="sugestoesInteligentes"
        :ids-ja-vinculados="candidatosJaNaVaga"
        :carregando="carregandoMatch"
        acao-label="Vincular à vaga"
        :processando-id="processandoId"
        vazio="Nenhuma sugestão automática. Ajuste tags da vaga ou currículos no CRM, ou busque abaixo."
        @acao="acaoSugestao"
      />

      <div class="border-t border-gray-200 dark:border-slate-700 pt-4 space-y-3">
        <h4 class="text-sm font-semibold text-gray-900 dark:text-slate-100">Buscar outro cidadão</h4>
        <CidadaoBuscaSelect
          v-model="candidatoManualId"
          label="Cidadão"
          placeholder="Nome, CPF ou telefone (mín. 2 caracteres)"
          :search-options="searchOptions"
        />
        <p class="text-xs text-gray-500 dark:text-slate-400 flex items-start gap-2">
          <FileText class="w-4 h-4 shrink-0 mt-0.5" />
          Prioriza quem tem currículo no CRM; com tags na vaga, a busca favorece perfis compatíveis.
        </p>
        <div v-if="candidatoManualId">
          <label class="label">Observações (opcional)</label>
          <textarea
            v-model="observacoes"
            rows="2"
            class="input"
            placeholder="Triagem inicial, indicação, etc."
          />
        </div>
      </div>

      <p v-if="erroSalvar" class="text-sm text-red-600 dark:text-red-400">{{ erroSalvar }}</p>
    </div>

    <template #footer>
      <Button variant="secondary" :disabled="salvando" @click="fechar">Cancelar</Button>
      <Button
        variant="primary"
        :loading="salvando && !processandoId"
        :disabled="!candidatoManualId || !vagaId || !!processandoId"
        @click="vincularManual"
      >
        <UserPlus class="w-4 h-4" />
        Vincular selecionado
      </Button>
    </template>
  </Modal>
</template>
