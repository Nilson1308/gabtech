<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useCerimonialStore } from '@/stores/cerimonial'
import type { ItemChecklist } from '@/stores/cerimonial'
import { Check, ClipboardList, Loader2, Send, Trash2 } from 'lucide-vue-next'
import PublicBrandHeader from '@/components/public/PublicBrandHeader.vue'

const route = useRoute()
const cerimonialStore = useCerimonialStore()

const token = computed(() => route.params.token as string)
const loading = ref(true)
const enviando = ref(false)
const erro = ref('')
const sucesso = ref(false)
const titulo = ref('')
const dataEvento = ref('')
const local = ref('')
const itens = ref<ItemChecklist[]>([])
const itensDescartados = ref<ItemChecklist[]>([])
const observacaoEnvio = ref('')

const categoriasNomes: Record<string, string> = {
  infraestrutura: 'Infraestrutura',
  buffet: 'Buffet',
  cerimonial: 'Cerimonial',
  comunicacao: 'Comunicação',
  seguranca: 'Segurança',
  tecnologia: 'Tecnologia',
}

const itensPorCategoria = computed(() => {
  const map: Record<string, ItemChecklist[]> = {}
  for (const item of itens.value) {
    if (!map[item.categoria]) map[item.categoria] = []
    map[item.categoria].push(item)
  }
  return map
})

onMounted(async () => {
  try {
    const data = await cerimonialStore.fetchLogisticaPublica(token.value)
    titulo.value = data.titulo
    dataEvento.value = data.data
    local.value = data.local
    itens.value = data.checklist.map(row => ({
      id: String(row.id),
      categoria: row.categoria as ItemChecklist['categoria'],
      descricao: row.descricao,
      status: row.status as ItemChecklist['status'],
      responsavel: row.responsavel || '',
      prazo: row.prazo || '',
      observacoes: row.observacoes || '',
      createdAt: row.created_at,
      updatedAt: row.updated_at,
    }))
  } catch {
    erro.value = 'Link inválido, expirado ou desativado.'
  } finally {
    loading.value = false
  }
})

function toggleItemLocal(item: ItemChecklist) {
  item.status = item.status === 'providenciado' ? 'pendente' : 'providenciado'
}

function descartarItem(item: ItemChecklist) {
  itensDescartados.value.push({ ...item })
  itens.value = itens.value.filter(i => i.id !== item.id)
}

function restaurarDescartado(item: ItemChecklist) {
  itens.value.push({ ...item })
  itensDescartados.value = itensDescartados.value.filter(i => i.id !== item.id)
}

async function enviarAtualizacoes() {
  if (itens.value.length === 0 && itensDescartados.value.length === 0) {
    erro.value = 'Não há itens para enviar.'
    return
  }

  enviando.value = true
  erro.value = ''

  try {
    const payloadItens = [
      ...itens.value.map(item => ({
        id: Number(item.id),
        responsavel: item.responsavel || '',
        prazo: item.prazo || null,
        observacoes: item.observacoes || '',
        status: item.status,
        descartar: false,
      })),
      ...itensDescartados.value.map(item => ({
        id: Number(item.id),
        descartar: true,
      })),
    ]

    await cerimonialStore.enviarLogisticaPublica(token.value, {
      itens: payloadItens,
      observacao_envio: observacaoEnvio.value.trim(),
    })

    sucesso.value = true
    itensDescartados.value = []
  } catch (e) {
    erro.value = e instanceof Error ? e.message : 'Falha ao enviar. Tente novamente.'
  } finally {
    enviando.value = false
  }
}

function formatarData(data: string) {
  if (!data) return ''
  return new Date(data + 'T12:00:00').toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  })
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 pb-24">
    <header class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-10">
      <div class="max-w-3xl mx-auto px-4 py-4 flex flex-col items-center gap-3 sm:flex-row sm:justify-between">
        <PublicBrandHeader subtitle="Checklist logístico — colaborador externo" />
        <div class="flex items-center gap-2 text-primary-600 dark:text-primary-400 text-sm">
          <ClipboardList class="w-5 h-5 flex-shrink-0" />
          <span>Acesso temporário</span>
        </div>
      </div>
    </header>

    <main class="max-w-3xl mx-auto px-4 py-8 space-y-6">
      <div v-if="loading" class="flex justify-center py-16">
        <Loader2 class="w-8 h-8 animate-spin text-primary-600" />
      </div>

      <div v-else-if="sucesso" class="text-center py-16 space-y-4">
        <div class="w-16 h-16 mx-auto bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center">
          <Check class="w-8 h-8 text-green-600 dark:text-green-400" />
        </div>
        <h2 class="text-xl font-bold text-gray-900 dark:text-gray-100">Enviado com sucesso!</h2>
        <p class="text-gray-600 dark:text-gray-400">
          O gestor do evento recebeu suas atualizações na checklist.
        </p>
        <p class="text-sm text-amber-700 dark:text-amber-400 max-w-md mx-auto">
          Este link foi encerrado. Para novas alterações, solicite um novo link ao organizador do evento.
        </p>
      </div>

      <div v-else-if="erro && !itens.length && !titulo" class="text-center py-16 text-red-600 dark:text-red-400">
        {{ erro }}
      </div>

      <template v-else-if="!sucesso">
        <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6">
          <h1 class="text-xl font-bold text-gray-900 dark:text-gray-100">{{ titulo }}</h1>
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-2">
            {{ formatarData(dataEvento) }}
            <span v-if="local"> · {{ local }}</span>
          </p>
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-4">
            Revise os itens abaixo: atualize responsável e prazo, marque como providenciado ou
            <strong>descarte</strong> o que não se aplicar. Ao terminar, use o botão
            <strong>Enviar atualizações</strong> no final da página — nada é salvo antes disso.
          </p>
        </div>

        <div
          v-for="(lista, categoria) in itensPorCategoria"
          :key="categoria"
          class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden"
        >
          <div class="px-4 py-3 bg-gray-100 dark:bg-gray-700/50 font-semibold text-gray-900 dark:text-gray-100">
            {{ categoriasNomes[categoria] || categoria }}
          </div>
          <div class="divide-y divide-gray-200 dark:divide-gray-700">
            <div v-for="item in lista" :key="item.id" class="p-4 space-y-3">
              <div class="flex items-start gap-3">
                <button
                  type="button"
                  @click="toggleItemLocal(item)"
                  :class="[
                    item.status === 'providenciado'
                      ? 'bg-green-500 border-green-500'
                      : 'border-gray-300 dark:border-gray-600',
                    'w-5 h-5 rounded border-2 flex items-center justify-center flex-shrink-0 mt-1',
                  ]"
                >
                  <Check v-if="item.status === 'providenciado'" class="w-3 h-3 text-white" />
                </button>
                <p
                  :class="[
                    item.status === 'providenciado' ? 'line-through text-gray-500' : 'text-gray-900 dark:text-gray-100',
                    'font-medium flex-1',
                  ]"
                >
                  {{ item.descricao }}
                </p>
                <button
                  type="button"
                  @click="descartarItem(item)"
                  class="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg"
                  title="Descartar item"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pl-8">
                <input
                  v-model="item.responsavel"
                  type="text"
                  placeholder="Responsável"
                  class="input text-sm"
                />
                <input v-model="item.prazo" type="date" class="input text-sm" />
              </div>
              <textarea
                v-model="item.observacoes"
                rows="2"
                placeholder="Observações sobre este item"
                class="input text-sm ml-8 w-[calc(100%-2rem)]"
              />
            </div>
          </div>
        </div>

        <div
          v-if="itensDescartados.length"
          class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl p-4 space-y-2"
        >
          <p class="text-sm font-medium text-amber-900 dark:text-amber-200">Itens marcados para descarte (enviados ao confirmar):</p>
          <div
            v-for="item in itensDescartados"
            :key="'d-' + item.id"
            class="flex items-center justify-between text-sm text-amber-800 dark:text-amber-300"
          >
            <span>{{ item.descricao }}</span>
            <button type="button" class="underline" @click="restaurarDescartado(item)">Restaurar</button>
          </div>
        </div>

        <p v-if="itens.length === 0 && !itensDescartados.length" class="text-center text-gray-500 py-8">
          Nenhum item na checklist. Aguarde o gestor adicionar itens ao evento.
        </p>

        <div
          v-if="itens.length || itensDescartados.length"
          class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-6 space-y-4 sticky bottom-4 shadow-lg"
        >
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Observações gerais (opcional)
          </label>
          <textarea
            v-model="observacaoEnvio"
            rows="3"
            placeholder="Ex.: Itens de buffet confirmados com fornecedor X..."
            class="input w-full"
          />
          <p v-if="erro" class="text-sm text-red-600 dark:text-red-400">{{ erro }}</p>
          <button
            type="button"
            :disabled="enviando"
            @click="enviarAtualizacoes"
            class="w-full flex items-center justify-center gap-2 px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-semibold disabled:opacity-50"
          >
            <Loader2 v-if="enviando" class="w-5 h-5 animate-spin" />
            <Send v-else class="w-5 h-5" />
            {{ enviando ? 'Enviando...' : 'Enviar atualizações ao gabinete' }}
          </button>
        </div>
      </template>
    </main>
  </div>
</template>
