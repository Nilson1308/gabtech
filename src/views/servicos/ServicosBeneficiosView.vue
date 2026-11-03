<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useServicosStore } from '@/stores/servicos'
import { useAuthStore } from '@/stores/auth'
import { PERMS } from '@/constants/rbac'
import TagsAlvoSelect from '@/components/servicos/TagsAlvoSelect.vue'
import SugestoesMatchList from '@/components/servicos/SugestoesMatchList.vue'
import CidadaoBuscaSelect from '@/components/crm/CidadaoBuscaSelect.vue'
import Button from '@/components/common/Button.vue'
import ServicosCrudMenu from '@/components/servicos/ServicosCrudMenu.vue'
import RastreabilidadeMeta from '@/components/common/RastreabilidadeMeta.vue'
import { AUDITORIA_ALVO } from '@/services/auditoria'
import { useAlertDialog } from '@/composables/useAlertDialog'
import type { EntregaBeneficio, ItemBeneficio, SugestaoMatchmaking } from '@/types'
import { CalendarDays, Gift, History } from 'lucide-vue-next'
import { RouterLink } from 'vue-router'

const servicosStore = useServicosStore()
const authStore = useAuthStore()
const podeGerenciar = authStore.hasPermission(PERMS.servicosAssistencia)
const { showConfirm, showError } = useAlertDialog()

const mostrarForm = ref(false)
const itemEmEdicaoId = ref<string | null>(null)
const nome = ref('')
const descricao = ref('')
const exigeLaudo = ref(false)
const tagsAlvoIds = ref<string[]>([])
const formItemErro = ref('')
const entregaEmEdicaoId = ref<string | null>(null)
const entregaEditData = ref('')
const entregaEditQtd = ref(1)
const itemSelecionadoId = ref<string | null>(null)
const sugestoes = ref<SugestaoMatchmaking[]>([])
const carregandoSugestoes = ref(false)
const cidadaoEntregaId = ref<string | null>(null)
const dataEntrega = ref(new Date().toISOString().slice(0, 10))
const feedback = ref('')
const erro = ref('')
const processandoId = ref<string | null>(null)

const idsComEntregaNoItem = computed(() => {
  if (!itemSelecionadoId.value) return []
  return servicosStore.entregasBeneficio
    .filter(e => e.itemId === itemSelecionadoId.value)
    .map(e => e.cidadaoId)
})

const entregasDoItem = computed(() => {
  if (!itemSelecionadoId.value) return []
  return [...servicosStore.entregasBeneficio]
    .filter(e => e.itemId === itemSelecionadoId.value)
    .sort((a, b) => b.dataEntrega.localeCompare(a.dataEntrega) || b.createdAt.localeCompare(a.createdAt))
})

const itemSelecionado = computed(() =>
  servicosStore.itensBeneficio.find(i => i.id === itemSelecionadoId.value) ?? null,
)

function contagemEntregasItem(itemId: string) {
  return servicosStore.entregasBeneficio.filter(e => e.itemId === itemId).length
}

function formatarDataEntrega(iso: string) {
  if (!iso) return '—'
  const [y, m, d] = iso.split('-')
  if (!y || !m || !d) return iso
  return `${d}/${m}/${y}`
}

onMounted(() => servicosStore.carregarAssistenciaSocial())

function limparFormItem() {
  itemEmEdicaoId.value = null
  nome.value = ''
  descricao.value = ''
  exigeLaudo.value = false
  tagsAlvoIds.value = []
  formItemErro.value = ''
}

function abrirNovoItem() {
  limparFormItem()
  mostrarForm.value = true
}

function abrirEditarItem(item: ItemBeneficio) {
  itemEmEdicaoId.value = item.id
  nome.value = item.nome
  descricao.value = item.descricao
  exigeLaudo.value = item.exigeLaudo
  tagsAlvoIds.value = [...item.tagsAlvoIds]
  mostrarForm.value = true
  formItemErro.value = ''
}

async function salvarItem() {
  formItemErro.value = ''
  if (!nome.value.trim()) {
    formItemErro.value = 'Informe o nome do benefício.'
    return
  }
  if (itemEmEdicaoId.value) {
    const { erro } = await servicosStore.updateItemBeneficio(itemEmEdicaoId.value, {
      nome: nome.value.trim(),
      descricao: descricao.value.trim(),
      exigeLaudo: exigeLaudo.value,
      tagsAlvoIds: [...tagsAlvoIds.value],
    })
    if (erro) formItemErro.value = erro
    else {
      mostrarForm.value = false
      limparFormItem()
      if (itemSelecionadoId.value) await carregarSugestoes(itemSelecionadoId.value)
    }
    return
  }
  const created = await servicosStore.createItemBeneficio({
    nome: nome.value.trim(),
    descricao: descricao.value.trim(),
    exigeLaudo: exigeLaudo.value,
    tagsAlvoIds: [...tagsAlvoIds.value],
  })
  if (created) {
    mostrarForm.value = false
    limparFormItem()
  } else formItemErro.value = 'Não foi possível criar o item.'
}

async function excluirItem(item: ItemBeneficio) {
  const ok = await showConfirm(`Excluir «${item.nome}»?`, 'Excluir item')
  if (!ok) return
  const { ok: done, erro } = await servicosStore.deleteItemBeneficio(item.id)
  if (!done) await showError(erro ?? 'Erro ao excluir.')
  else if (itemSelecionadoId.value === item.id) itemSelecionadoId.value = null
}

function iniciarEditarEntrega(e: EntregaBeneficio) {
  entregaEmEdicaoId.value = e.id
  entregaEditData.value = e.dataEntrega
  entregaEditQtd.value = e.quantidade
}

async function salvarEntregaEditada() {
  if (!entregaEmEdicaoId.value) return
  const { erro } = await servicosStore.updateEntregaBeneficio(entregaEmEdicaoId.value, {
    dataEntrega: entregaEditData.value,
    quantidade: entregaEditQtd.value,
  })
  if (erro) await showError(erro)
  else entregaEmEdicaoId.value = null
}

async function excluirEntrega(e: EntregaBeneficio) {
  const ok = await showConfirm(
    `Remover o registro de entrega para ${e.cidadaoNome ?? 'cidadão'}?`,
    'Excluir entrega',
  )
  if (!ok) return
  const { ok: done, erro } = await servicosStore.deleteEntregaBeneficio(e.id)
  if (!done) await showError(erro ?? 'Erro ao excluir.')
  else if (itemSelecionadoId.value) {
    sugestoes.value = await servicosStore.fetchSugerirPublicoBeneficio(itemSelecionadoId.value, 25)
  }
}

async function carregarSugestoes(itemId: string) {
  itemSelecionadoId.value = itemId
  feedback.value = ''
  erro.value = ''
  carregandoSugestoes.value = true
  try {
    sugestoes.value = await servicosStore.fetchSugerirPublicoBeneficio(itemId, 25)
    await servicosStore.fetchEntregasBeneficio()
  } finally {
    carregandoSugestoes.value = false
  }
}

async function registrarEntregaCidadao(cidadaoId: string) {
  if (!itemSelecionadoId.value || !podeGerenciar) return
  erro.value = ''
  feedback.value = ''
  processandoId.value = cidadaoId
  const { erro: err } = await servicosStore.createEntregaBeneficio({
    cidadaoId,
    itemId: itemSelecionadoId.value,
    dataEntrega: dataEntrega.value,
  })
  processandoId.value = null
  if (err) {
    erro.value = err
    return
  }
  feedback.value = 'Entrega registrada com sucesso.'
  cidadaoEntregaId.value = null
  await servicosStore.fetchEntregasBeneficio()
  sugestoes.value = await servicosStore.fetchSugerirPublicoBeneficio(itemSelecionadoId.value, 25)
}

function acaoSugestao(s: SugestaoMatchmaking) {
  registrarEntregaCidadao(s.cidadao.id)
}

async function registrarEntregaManual() {
  if (!cidadaoEntregaId.value) {
    erro.value = 'Selecione um cidadão na busca.'
    return
  }
  await registrarEntregaCidadao(cidadaoEntregaId.value)
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between gap-4">
      <p class="text-sm text-gray-600 dark:text-slate-400">
        Itens, entregas e sugestão de público por tags de segmentação.
      </p>
      <Button v-if="podeGerenciar" variant="primary" @click="abrirNovoItem">
        Novo item
      </Button>
    </div>

    <div v-if="mostrarForm && podeGerenciar" class="card space-y-3">
      <h4 class="text-sm font-semibold">{{ itemEmEdicaoId ? 'Editar item' : 'Novo item' }}</h4>
      <input v-model="nome" class="input" placeholder="Nome do benefício" />
      <textarea v-model="descricao" class="input" rows="2" placeholder="Descrição" />
      <label class="flex items-center gap-2 text-sm">
        <input v-model="exigeLaudo" type="checkbox" />
        Exige laudo médico no CRM
      </label>
      <TagsAlvoSelect v-model="tagsAlvoIds" variant="segmentacao" />
      <div class="flex gap-2">
        <Button variant="secondary" @click="salvarItem">Salvar</Button>
        <Button variant="ghost" @click="mostrarForm = false; limparFormItem()">Cancelar</Button>
      </div>
      <p v-if="formItemErro" class="text-sm text-red-600">{{ formItemErro }}</p>
    </div>

    <div class="grid lg:grid-cols-2 gap-6">
      <div class="card space-y-2">
        <h3 class="font-semibold flex items-center gap-2">
          <Gift class="w-4 h-4 text-emerald-600" />
          Itens
        </h3>
        <div
          v-for="item in servicosStore.itensBeneficio"
          :key="item.id"
          class="w-full flex gap-2 p-3 rounded-lg border transition-colors hover:border-emerald-400"
          :class="itemSelecionadoId === item.id ? 'border-emerald-500 bg-emerald-50/50 dark:bg-emerald-950/20' : ''"
        >
          <button type="button" class="flex-1 min-w-0 text-left" @click="carregarSugestoes(item.id)">
          <div class="flex items-start justify-between gap-2">
            <p class="font-medium text-sm">{{ item.nome }}</p>
            <span
              v-if="contagemEntregasItem(item.id) > 0"
              class="text-[10px] font-medium px-1.5 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-900/40 text-emerald-800 dark:text-emerald-300 shrink-0"
            >
              {{ contagemEntregasItem(item.id) }} entrega{{ contagemEntregasItem(item.id) === 1 ? '' : 's' }}
            </span>
          </div>
          <div class="flex flex-wrap gap-1 mt-1">
            <span
              v-for="tag in item.tagsAlvo"
              :key="tag.id"
              class="text-[10px] px-1.5 py-0.5 rounded-full"
              :style="{ backgroundColor: tag.cor + '22', color: tag.cor }"
            >
              {{ tag.nome }}
            </span>
          </div>
          <RastreabilidadeMeta
            :rastreabilidade="item.rastreabilidade"
            :alvo-auditoria="AUDITORIA_ALVO.itemBeneficio(item.id)"
            historico-titulo="Histórico do item"
            compact
            class="mt-1"
          />
          </button>
          <ServicosCrudMenu
            v-if="podeGerenciar"
            @edit="abrirEditarItem(item)"
            @delete="excluirItem(item)"
          />
        </div>
      </div>

      <div class="space-y-4">
        <SugestoesMatchList
          :sugestoes="sugestoes"
          :ids-ja-vinculados="idsComEntregaNoItem"
          :carregando="carregandoSugestoes"
          acao-label="Registrar entrega"
          :processando-id="processandoId"
          vazio="Selecione um item à esquerda para ver o público sugerido."
          @acao="acaoSugestao"
        />

        <div
          v-if="podeGerenciar && itemSelecionadoId"
          class="card space-y-3 border-dashed"
        >
          <h4 class="text-sm font-semibold text-gray-900 dark:text-slate-100">
            Outro cidadão
          </h4>
          <p class="text-xs text-gray-500 dark:text-slate-400">
            Busque na base do CRM — não é necessário informar ID.
          </p>
          <CidadaoBuscaSelect v-model="cidadaoEntregaId" label="Cidadão" />
          <label class="block">
            <span class="label text-xs">Data da entrega</span>
            <input v-model="dataEntrega" type="date" class="input mt-1" />
          </label>
          <Button variant="secondary" tamanho="sm" :disabled="!!processandoId" @click="registrarEntregaManual">
            Registrar entrega
          </Button>
          <p v-if="feedback" class="text-sm text-emerald-700 dark:text-emerald-400">{{ feedback }}</p>
          <p v-if="erro" class="text-sm text-red-600 dark:text-red-400">{{ erro }}</p>
        </div>

        <div v-if="itemSelecionadoId" class="card">
          <h4 class="text-sm font-semibold flex items-center gap-2 mb-3">
            <History class="w-4 h-4 text-emerald-600" />
            Entregas registradas
            <span v-if="itemSelecionado" class="font-normal text-gray-500 dark:text-slate-400 truncate">
              — {{ itemSelecionado.nome }}
            </span>
          </h4>

          <ul v-if="entregasDoItem.length" class="divide-y divide-gray-100 dark:divide-slate-800">
            <li
              v-for="entrega in entregasDoItem"
              :key="entrega.id"
              class="py-3 first:pt-0 last:pb-0 flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2"
            >
              <div class="min-w-0 flex-1">
                <RouterLink
                  :to="{ name: 'CRMPerfil', params: { id: entrega.cidadaoId } }"
                  class="text-sm font-medium text-primary-700 dark:text-primary-400 hover:underline truncate block"
                >
                  {{ entrega.cidadaoNome ?? 'Cidadão' }}
                </RouterLink>
                <template v-if="entregaEmEdicaoId === entrega.id && podeGerenciar">
                  <div class="mt-2 flex flex-wrap gap-2 items-end">
                    <label class="text-xs">
                      Data
                      <input v-model="entregaEditData" type="date" class="input mt-0.5 text-sm" />
                    </label>
                    <label class="text-xs">
                      Qtd.
                      <input v-model.number="entregaEditQtd" type="number" min="1" class="input mt-0.5 w-20 text-sm" />
                    </label>
                    <button type="button" class="text-xs text-primary-600" @click="salvarEntregaEditada">Salvar</button>
                    <button type="button" class="text-xs text-gray-500" @click="entregaEmEdicaoId = null">Cancelar</button>
                  </div>
                </template>
                <p v-else class="text-xs text-gray-500 dark:text-slate-400 flex items-center gap-1.5 mt-0.5">
                  <CalendarDays class="w-3.5 h-3.5 shrink-0" />
                  Entregue em {{ formatarDataEntrega(entrega.dataEntrega) }}
                  <span v-if="entrega.quantidade > 1"> · qtd. {{ entrega.quantidade }}</span>
                </p>
                <RastreabilidadeMeta
                  :rastreabilidade="entrega.rastreabilidade"
                  :alvo-auditoria="AUDITORIA_ALVO.entregaBeneficio(entrega.id)"
                  historico-titulo="Histórico da entrega"
                  compact
                  class="mt-0.5"
                />
              </div>
              <ServicosCrudMenu
                v-if="podeGerenciar"
                @edit="iniciarEditarEntrega(entrega)"
                @delete="excluirEntrega(entrega)"
              />
            </li>
          </ul>
          <p v-else class="text-sm text-gray-500 dark:text-slate-400">
            Nenhuma entrega registrada para este item ainda.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
