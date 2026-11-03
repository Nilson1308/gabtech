<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useServicosStore } from '@/stores/servicos'
import { useAuthStore } from '@/stores/auth'
import { PERMS } from '@/constants/rbac'
import TagsAlvoSelect from '@/components/servicos/TagsAlvoSelect.vue'
import SugestoesMatchList from '@/components/servicos/SugestoesMatchList.vue'
import CidadaoBuscaSelect from '@/components/crm/CidadaoBuscaSelect.vue'
import ServicosCrudMenu from '@/components/servicos/ServicosCrudMenu.vue'
import RastreabilidadeMeta from '@/components/common/RastreabilidadeMeta.vue'
import { AUDITORIA_ALVO } from '@/services/auditoria'
import Button from '@/components/common/Button.vue'
import { useAlertDialog } from '@/composables/useAlertDialog'
import type { InscricaoCurso, SugestaoMatchmaking, TurmaCurso } from '@/types'
import { GraduationCap } from 'lucide-vue-next'
import { RouterLink } from 'vue-router'

const servicosStore = useServicosStore()
const authStore = useAuthStore()
const podeGerenciar = authStore.hasPermission(PERMS.servicosCursos)
const { showConfirm, showError } = useAlertDialog()

const STATUS_TURMA = [
  { value: 'aberta' as const, label: 'Aberta' },
  { value: 'em_andamento' as const, label: 'Em andamento' },
  { value: 'encerrada' as const, label: 'Encerrada' },
]

const STATUS_INSCRICAO = [
  { value: 'inscrito' as const, label: 'Inscrito' },
  { value: 'lista_espera' as const, label: 'Lista de espera' },
  { value: 'cancelado' as const, label: 'Cancelado' },
]

const mostrarForm = ref(false)
const turmaEmEdicaoId = ref<string | null>(null)
const nomeCurso = ref('')
const vagasTotais = ref(20)
const statusTurma = ref<TurmaCurso['status']>('aberta')
const tagsAlvoIds = ref<string[]>([])
const formTurmaErro = ref('')
const turmaSelecionadaId = ref<string | null>(null)
const sugestoes = ref<SugestaoMatchmaking[]>([])
const carregandoSugestoes = ref(false)
const cidadaoInscricaoId = ref<string | null>(null)
const feedback = ref('')
const erro = ref('')
const processandoId = ref<string | null>(null)

const turmaSelecionada = computed(() =>
  servicosStore.turmas.find(t => t.id === turmaSelecionadaId.value) ?? null,
)

const idsInscritosNaTurma = computed(() => {
  if (!turmaSelecionadaId.value) return []
  return servicosStore.inscricoes
    .filter(i => i.turmaId === turmaSelecionadaId.value && i.status !== 'cancelado')
    .map(i => i.cidadaoId)
})

const inscricoesDaTurma = computed(() => {
  if (!turmaSelecionadaId.value) return []
  return servicosStore.inscricoes.filter(x => x.turmaId === turmaSelecionadaId.value)
})

onMounted(() => servicosStore.carregarCursos())

function limparFormTurma() {
  turmaEmEdicaoId.value = null
  nomeCurso.value = ''
  vagasTotais.value = 20
  statusTurma.value = 'aberta'
  tagsAlvoIds.value = []
  formTurmaErro.value = ''
}

function abrirNovaTurma() {
  limparFormTurma()
  mostrarForm.value = true
}

function abrirEditarTurma(t: TurmaCurso) {
  turmaEmEdicaoId.value = t.id
  nomeCurso.value = t.nomeCurso
  vagasTotais.value = t.vagasTotais
  statusTurma.value = t.status
  tagsAlvoIds.value = [...t.tagsAlvoIds]
  mostrarForm.value = true
}

async function salvarTurma() {
  formTurmaErro.value = ''
  if (!nomeCurso.value.trim()) {
    formTurmaErro.value = 'Informe o nome do curso.'
    return
  }
  if (turmaEmEdicaoId.value) {
    const { erro: err } = await servicosStore.updateTurma(turmaEmEdicaoId.value, {
      nomeCurso: nomeCurso.value.trim(),
      vagasTotais: vagasTotais.value,
      status: statusTurma.value,
      tagsAlvoIds: [...tagsAlvoIds.value],
    })
    if (err) formTurmaErro.value = err
    else {
      mostrarForm.value = false
      limparFormTurma()
      if (turmaSelecionadaId.value) await carregarSugestoes(turmaSelecionadaId.value)
    }
    return
  }
  const t = await servicosStore.createTurma({
    nomeCurso: nomeCurso.value.trim(),
    vagasTotais: vagasTotais.value,
    tagsAlvoIds: [...tagsAlvoIds.value],
  })
  if (t) {
    turmaSelecionadaId.value = t.id
    mostrarForm.value = false
    limparFormTurma()
    await servicosStore.fetchInscricoes(t.id)
  } else formTurmaErro.value = 'Não foi possível criar a turma.'
}

async function excluirTurma(t: TurmaCurso) {
  const ok = await showConfirm(
    `Excluir a turma «${t.nomeCurso}»? Todas as inscrições serão removidas.`,
    'Excluir turma',
  )
  if (!ok) return
  const { ok: done, erro: err } = await servicosStore.deleteTurma(t.id)
  if (!done) await showError(err ?? 'Erro ao excluir.')
  else if (turmaSelecionadaId.value === t.id) turmaSelecionadaId.value = null
}

async function carregarSugestoes(turmaId: string) {
  turmaSelecionadaId.value = turmaId
  feedback.value = ''
  erro.value = ''
  carregandoSugestoes.value = true
  try {
    sugestoes.value = await servicosStore.fetchSugerirPublicoTurma(turmaId, 25)
    await servicosStore.fetchInscricoes(turmaId)
  } finally {
    carregandoSugestoes.value = false
  }
}

async function inscreverCidadao(cidadaoId: string) {
  if (!turmaSelecionadaId.value || !podeGerenciar) return
  erro.value = ''
  feedback.value = ''
  processandoId.value = cidadaoId
  const { inscricao, erro: err } = await servicosStore.createInscricaoCurso({
    turmaId: turmaSelecionadaId.value,
    cidadaoId,
  })
  processandoId.value = null
  if (err) {
    erro.value = err
    return
  }
  if (inscricao) {
    feedback.value =
      inscricao.status === 'lista_espera'
        ? 'Cidadão incluído na lista de espera (turma cheia).'
        : 'Inscrição confirmada.'
    cidadaoInscricaoId.value = null
    await servicosStore.fetchInscricoes(turmaSelecionadaId.value)
    sugestoes.value = await servicosStore.fetchSugerirPublicoTurma(turmaSelecionadaId.value, 25)
  }
}

function acaoSugestao(s: SugestaoMatchmaking) {
  inscreverCidadao(s.cidadao.id)
}

async function inscreverManual() {
  if (!cidadaoInscricaoId.value) {
    erro.value = 'Selecione um cidadão na busca.'
    return
  }
  await inscreverCidadao(cidadaoInscricaoId.value)
}

async function alterarStatusInscricao(i: InscricaoCurso, status: InscricaoCurso['status']) {
  const { erro: err } = await servicosStore.updateInscricaoCurso(i.id, { status })
  if (err) await showError(err)
  else if (turmaSelecionadaId.value) {
    await servicosStore.fetchInscricoes(turmaSelecionadaId.value)
    sugestoes.value = await servicosStore.fetchSugerirPublicoTurma(turmaSelecionadaId.value, 25)
  }
}

async function removerInscricao(i: InscricaoCurso) {
  const ok = await showConfirm(
    `Remover inscrição de ${i.cidadaoNome ?? 'cidadão'}?`,
    'Excluir inscrição',
  )
  if (!ok) return
  const { ok: done, erro: err } = await servicosStore.deleteInscricaoCurso(i.id)
  if (!done) await showError(err ?? 'Erro ao excluir.')
  else if (turmaSelecionadaId.value) {
    sugestoes.value = await servicosStore.fetchSugerirPublicoTurma(turmaSelecionadaId.value, 25)
  }
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between gap-4">
      <p class="text-sm text-gray-600 dark:text-slate-400">
        Turmas, inscrições e lista de espera automática.
      </p>
      <Button v-if="podeGerenciar" variant="primary" @click="abrirNovaTurma">
        Nova turma
      </Button>
    </div>

    <div v-if="mostrarForm && podeGerenciar" class="card space-y-3 max-w-xl">
      <h4 class="text-sm font-semibold">{{ turmaEmEdicaoId ? 'Editar turma' : 'Nova turma' }}</h4>
      <input v-model="nomeCurso" class="input" placeholder="Nome do curso" />
      <input v-model.number="vagasTotais" type="number" min="1" class="input" placeholder="Vagas totais" />
      <select v-model="statusTurma" class="input">
        <option v-for="s in STATUS_TURMA" :key="s.value" :value="s.value">{{ s.label }}</option>
      </select>
      <TagsAlvoSelect v-model="tagsAlvoIds" />
      <div class="flex gap-2">
        <Button variant="secondary" @click="salvarTurma">Salvar</Button>
        <Button variant="ghost" @click="mostrarForm = false; limparFormTurma()">Cancelar</Button>
      </div>
      <p v-if="formTurmaErro" class="text-sm text-red-600">{{ formTurmaErro }}</p>
    </div>

    <div class="grid lg:grid-cols-2 gap-6">
      <div class="card space-y-2">
        <h3 class="font-semibold flex items-center gap-2">
          <GraduationCap class="w-4 h-4 text-violet-600" />
          Turmas
        </h3>
        <div
          v-for="t in servicosStore.turmas"
          :key="t.id"
          class="w-full flex gap-2 p-3 rounded-lg border transition-colors"
          :class="turmaSelecionadaId === t.id ? 'border-violet-500 bg-violet-50/50 dark:bg-violet-950/20' : ''"
        >
          <button type="button" class="flex-1 min-w-0 text-left" @click="carregarSugestoes(t.id)">
            <p class="font-medium text-sm">{{ t.nomeCurso }}</p>
            <p class="text-xs text-gray-500">
              {{ t.vagasOcupadas }} / {{ t.vagasTotais }} vagas ·
              {{ STATUS_TURMA.find(s => s.value === t.status)?.label ?? t.status }}
            </p>
            <div class="flex flex-wrap gap-1 mt-1">
              <span
                v-for="tag in t.tagsAlvo"
                :key="tag.id"
                class="text-[10px] px-1.5 py-0.5 rounded-full"
                :style="{ backgroundColor: tag.cor + '22', color: tag.cor }"
              >
                {{ tag.nome }}
              </span>
            </div>
            <RastreabilidadeMeta
              :rastreabilidade="t.rastreabilidade"
              :alvo-auditoria="AUDITORIA_ALVO.turmaCurso(t.id)"
              historico-titulo="Histórico da turma"
              compact
              class="mt-1"
            />
          </button>
          <ServicosCrudMenu
            v-if="podeGerenciar"
            @edit="abrirEditarTurma(t)"
            @delete="excluirTurma(t)"
          />
        </div>
      </div>

      <div class="space-y-4">
        <SugestoesMatchList
          :sugestoes="sugestoes"
          :ids-ja-vinculados="idsInscritosNaTurma"
          :carregando="carregandoSugestoes"
          acao-label="Inscrever na turma"
          :processando-id="processandoId"
          vazio="Selecione uma turma à esquerda para ver sugestões."
          @acao="acaoSugestao"
        />

        <div v-if="turmaSelecionada && podeGerenciar" class="card space-y-3 border-dashed">
          <h4 class="text-sm font-semibold">Outro cidadão</h4>
          <p class="text-xs text-gray-500 dark:text-slate-400">
            Busque por nome, CPF ou telefone no CRM.
          </p>
          <CidadaoBuscaSelect v-model="cidadaoInscricaoId" label="Cidadão" />
          <Button variant="secondary" tamanho="sm" :disabled="!!processandoId" @click="inscreverManual">
            Inscrever
          </Button>
          <p v-if="feedback" class="text-sm text-emerald-700 dark:text-emerald-400">{{ feedback }}</p>
          <p v-if="erro" class="text-sm text-red-600 dark:text-red-400">{{ erro }}</p>
        </div>

        <div v-if="turmaSelecionadaId" class="card">
          <h4 class="text-sm font-semibold mb-2">Inscrições</h4>
          <ul v-if="inscricoesDaTurma.length" class="text-sm space-y-3">
            <li
              v-for="i in inscricoesDaTurma"
              :key="i.id"
              class="flex flex-col sm:flex-row sm:items-center gap-2 py-2 border-b border-gray-100 dark:border-slate-800 last:border-0"
            >
              <RouterLink
                :to="{ name: 'CRMPerfil', params: { id: i.cidadaoId } }"
                class="font-medium text-primary-700 dark:text-primary-400 hover:underline flex-1 min-w-0 truncate"
              >
                {{ i.cidadaoNome ?? 'Cidadão' }}
              </RouterLink>
              <select
                v-if="podeGerenciar"
                :value="i.status"
                class="input text-xs py-1 max-w-[10rem]"
                @change="alterarStatusInscricao(i, ($event.target as HTMLSelectElement).value as InscricaoCurso['status'])"
              >
                <option v-for="s in STATUS_INSCRICAO" :key="s.value" :value="s.value">
                  {{ s.label }}
                </option>
              </select>
              <span v-else class="text-xs text-gray-500 capitalize">{{ i.status.replace('_', ' ') }}</span>
              <RastreabilidadeMeta
                :rastreabilidade="i.rastreabilidade"
                :alvo-auditoria="AUDITORIA_ALVO.inscricaoCurso(i.id)"
                historico-titulo="Histórico da inscrição"
                compact
                class="sm:max-w-[14rem]"
              />
              <ServicosCrudMenu
                v-if="podeGerenciar"
                :show-edit="false"
                @delete="removerInscricao(i)"
              />
            </li>
          </ul>
          <p v-else class="text-sm text-gray-500">Nenhuma inscrição ainda.</p>
        </div>
      </div>
    </div>
  </div>
</template>
