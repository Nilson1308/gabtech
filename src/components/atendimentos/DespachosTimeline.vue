<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useAtendimentosStore } from '@/stores/atendimentos'
import type { Despacho } from '@/types'
import { useFormatters } from '@/composables/useFormatters'
import Avatar from '@/components/common/Avatar.vue'
import Button from '@/components/common/Button.vue'
import { 
  MessageCircle, 
  MessageSquare, 
  RefreshCw, 
  UserCheck,
  Send,
  Paperclip,
  X,
  FileText,
  Image as ImageIcon
} from 'lucide-vue-next'

interface Props {
  atendimentoId: string
  despachos: Despacho[]
  /** Ex.: perfil Recepção (sem editar_atend) — só leitura da timeline */
  podeRegistrarDespacho?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  podeRegistrarDespacho: true,
})

const emit = defineEmits<{
  updated: [atendimento: import('@/types').Atendimento]
}>()

const authStore = useAuthStore()
const atendimentosStore = useAtendimentosStore()
const { formatRelativeTime } = useFormatters()

// Novo despacho
const novoDespacho = ref('')
const isInterno = ref(false)
const enviando = ref(false)
const anexos = ref<File[]>([])
const inputAnexo = ref<HTMLInputElement | null>(null)

// Ícone por tipo
const iconeMap = {
  nota_interna: MessageCircle,
  nota_publica: MessageSquare,
  mudanca_status: RefreshCw,
  reatribuicao: UserCheck
}

const getIcone = (tipo: string) => {
  return iconeMap[tipo as keyof typeof iconeMap] || MessageCircle
}

// Handlers de anexos
const handleAnexarClick = () => {
  inputAnexo.value?.click()
}

const handleAnexoInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = Array.from(target.files || [])
  
  files.forEach(file => {
    if (file.size > 10 * 1024 * 1024) {
      alert('Arquivo muito grande. Máximo 10MB.')
      return
    }
    anexos.value.push(file)
  })
  
  // Limpar input
  target.value = ''
}

const removerAnexo = (index: number) => {
  anexos.value.splice(index, 1)
}

const getIconeAnexo = (file: File) => {
  if (file.type.startsWith('image/')) return ImageIcon
  return FileText
}

const formatarTamanho = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

// Enviar despacho
const enviar = async () => {
  if (!novoDespacho.value.trim() && anexos.value.length === 0) return

  enviando.value = true

  try {
    const texto = novoDespacho.value.trim()
    const conteudo = texto || (anexos.value.length > 0 ? 'Arquivo(s) anexado(s).' : '')
    const arquivos = [...anexos.value]

    const atualizado = await atendimentosStore.addDespacho(
      props.atendimentoId,
      conteudo,
      isInterno.value ? 'nota_interna' : 'nota_publica',
      arquivos,
    )

    if (atualizado) {
      emit('updated', atualizado)
    }

    novoDespacho.value = ''
    isInterno.value = false
    anexos.value = []
  } finally {
    enviando.value = false
  }
}
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Timeline -->
    <div class="flex-1 space-y-4 overflow-y-auto pr-2 mb-6">
      <div
        v-for="despacho in despachos"
        :key="despacho.id"
        class="flex gap-3"
      >
        <!-- Avatar -->
        <div class="flex-shrink-0">
          <Avatar :nome="despacho.autor.nome" tamanho="md" />
        </div>

        <!-- Conteúdo -->
        <div class="flex-1 min-w-0">
          <div class="bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-lg p-4">
            <!-- Header -->
            <div class="flex items-start justify-between gap-2 mb-2">
              <div class="flex items-center gap-2">
                <component :is="getIcone(despacho.tipo)" class="w-4 h-4 text-gray-400 dark:text-slate-500" />
                <span class="font-medium text-gray-900 dark:text-slate-100">{{ despacho.autor.nome }}</span>
                
                <!-- Badge Interno -->
                <span
                  v-if="despacho.tipo === 'nota_interna'"
                  class="px-2 py-0.5 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 text-xs font-medium rounded"
                >
                  Interno
                </span>
              </div>
              
              <span class="text-xs text-gray-500 dark:text-slate-400 whitespace-nowrap">
                {{ formatRelativeTime(despacho.createdAt) }}
              </span>
            </div>

            <!-- Conteúdo do Despacho -->
            <p class="text-gray-700 dark:text-slate-300 whitespace-pre-line">{{ despacho.conteudo }}</p>

            <ul
              v-if="despacho.anexos?.length"
              class="mt-3 space-y-1 border-t border-gray-100 dark:border-slate-700 pt-2"
            >
              <li
                v-for="anexo in despacho.anexos"
                :key="anexo.id"
                class="flex items-center gap-2 text-sm"
              >
                <Paperclip class="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
                <button
                  type="button"
                  class="text-primary-600 dark:text-primary-400 hover:underline truncate text-left"
                  @click="atendimentosStore.downloadAnexoAtendimento(anexo)"
                >
                  {{ anexo.nome }}
                </button>
                <span class="text-xs text-gray-500 flex-shrink-0">{{ formatarTamanho(anexo.tamanho) }}</span>
              </li>
            </ul>

            <!-- Informações de Mudança de Status/Reatribuição -->
            <div v-if="despacho.statusAnterior && despacho.statusNovo" class="mt-2 pt-2 border-t border-gray-200 dark:border-slate-700">
              <p class="text-xs text-gray-600 dark:text-slate-400">
                Status alterado: 
                <span class="font-medium">{{ despacho.statusAnterior }}</span> 
                → 
                <span class="font-medium">{{ despacho.statusNovo }}</span>
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Estado Vazio -->
      <div v-if="despachos.length === 0" class="text-center py-12">
        <MessageCircle class="w-12 h-12 text-gray-300 dark:text-slate-600 mx-auto mb-3" />
        <p class="text-gray-500 dark:text-slate-400">Nenhum despacho ainda</p>
      </div>
    </div>

    <div
      v-if="!podeRegistrarDespacho"
      class="border-t border-gray-200 dark:border-slate-700 pt-4 flex-shrink-0"
    >
      <p class="text-sm text-gray-500 dark:text-slate-400 text-center py-3">
        Seu perfil pode acompanhar a timeline, mas não registrar novos despachos.
      </p>
    </div>

    <!-- Novo Despacho -->
    <div v-else class="border-t border-gray-200 dark:border-slate-700 pt-4 flex-shrink-0">
      <div class="flex gap-3 w-full">
        <!-- Avatar do Usuário -->
        <div class="flex-shrink-0">
          <Avatar :nome="authStore.usuario!.nome" tamanho="md" />
        </div>

        <!-- Form -->
        <div class="flex-1 min-w-0">
          <textarea
            v-model="novoDespacho"
            rows="3"
            class="w-full resize-y p-3 border border-gray-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:outline-none bg-white dark:bg-slate-700 text-gray-900 dark:text-slate-100 mb-2 box-border"
            placeholder="Escreva um despacho..."
            :disabled="enviando"
          ></textarea>

          <!-- Lista de Anexos -->
          <div v-if="anexos.length > 0" class="mb-2 space-y-1">
            <div
              v-for="(anexo, index) in anexos"
              :key="index"
              class="flex items-center gap-2 p-2 bg-gray-50 dark:bg-slate-800 rounded border border-gray-200 dark:border-slate-600"
            >
              <component :is="getIconeAnexo(anexo)" class="w-4 h-4 text-gray-600 dark:text-slate-400 flex-shrink-0" />
              <span class="text-sm text-gray-700 dark:text-slate-300 flex-1 truncate">{{ anexo.name }}</span>
              <span class="text-xs text-gray-500 dark:text-slate-400 flex-shrink-0">{{ formatarTamanho(anexo.size) }}</span>
              <button
                @click="removerAnexo(index)"
                type="button"
                class="text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 flex-shrink-0"
                :disabled="enviando"
              >
                <X class="w-4 h-4" />
              </button>
            </div>
          </div>

          <div class="flex items-center justify-between">
            <!-- Esquerda: Checkbox + Anexar -->
            <div class="flex items-center gap-4">
              <!-- Checkbox Interno -->
              <label class="flex items-center gap-2 text-sm text-gray-700 dark:text-slate-300 cursor-pointer">
                <input
                  v-model="isInterno"
                  type="checkbox"
                  class="rounded border-gray-300 dark:border-slate-600 text-primary-600 focus:ring-primary-500"
                  :disabled="enviando"
                />
                Interno
              </label>

              <!-- Botão Anexar -->
              <button
                @click="handleAnexarClick"
                type="button"
                class="flex items-center gap-1 text-sm text-gray-600 dark:text-slate-400 hover:text-gray-900 dark:hover:text-slate-200"
                :disabled="enviando"
                title="Anexar arquivo"
              >
                <Paperclip class="w-4 h-4" />
                Anexar
              </button>
              <input
                ref="inputAnexo"
                type="file"
                multiple
                accept="image/*,.pdf,.doc,.docx"
                @change="handleAnexoInput"
                class="hidden"
              />
            </div>

            <!-- Botão Enviar -->
            <Button
              variant="primary"
              @click="enviar"
              :loading="enviando"
              :disabled="!novoDespacho.trim() && anexos.length === 0"
            >
              <Send class="w-4 h-4" />
              {{ enviando ? 'Enviando...' : 'Enviar' }}
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
