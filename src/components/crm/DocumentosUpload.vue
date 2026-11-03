<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useCrmStore } from '@/stores/crm'
import { useAlertDialog } from '@/composables/useAlertDialog'
import type { CidadaoDocumento } from '@/types'
import {
  CATEGORIAS_DOCUMENTO_CIDADAO,
  labelCategoriaDocumento,
  type CategoriaDocumentoCidadao,
} from '@/constants/crmDocumentos'
import {
  HINT_CURRICULO_TAGS,
  LABEL_TAGS_CONTEXTO_PROFISSIONAL,
} from '@/constants/servicosTags'
import { Upload, File, X, FileText, Image as ImageIcon, Loader2 } from 'lucide-vue-next'

interface Props {
  cidadaoId: string
  /** Permite upload e exclusão (ex.: permissão editar_crm) */
  podeEditar?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  podeEditar: true,
})

const crmStore = useCrmStore()
const { tagsContextoProfissional } = storeToRefs(crmStore)
const { showConfirm, showError } = useAlertDialog()

const isDragging = ref(false)
const isUploading = ref(false)
const erro = ref<string | null>(null)
const documentosLocal = ref<CidadaoDocumento[]>([])
const categoriaUpload = ref<CategoriaDocumentoCidadao>('outros')
const etiquetasUpload = ref<string[]>([])

function toggleEtiquetaUpload(tagId: string) {
  const i = etiquetasUpload.value.indexOf(tagId)
  if (i >= 0) etiquetasUpload.value.splice(i, 1)
  else etiquetasUpload.value.push(tagId)
}

function toggleEtiquetaDocumento(doc: CidadaoDocumento, tagId: string) {
  const atuais = doc.etiquetas.map(e => e.id)
  const i = atuais.indexOf(tagId)
  if (i >= 0) atuais.splice(i, 1)
  else atuais.push(tagId)
  return atuais
}

const EXTENSOES = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
const MIME_PERMITIDOS = [
  'application/pdf',
  'image/jpeg',
  'image/jpg',
  'image/png',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
]

async function carregarDocumentos() {
  if (!props.cidadaoId) {
    documentosLocal.value = []
    return
  }
  try {
    documentosLocal.value = await crmStore.fetchDocumentosCidadao(props.cidadaoId)
  } catch {
    erro.value = 'Não foi possível carregar os documentos.'
  }
}

onMounted(async () => {
  await crmStore.fetchTags()
  await carregarDocumentos()
})
watch(() => props.cidadaoId, carregarDocumentos)

watch(categoriaUpload, cat => {
  if (cat !== 'curriculo') etiquetasUpload.value = []
})

const handleDragEnter = (e: DragEvent) => {
  e.preventDefault()
  if (props.podeEditar) {
    isDragging.value = true
  }
}

const handleDragLeave = (e: DragEvent) => {
  e.preventDefault()
  if (e.target === e.currentTarget) {
    isDragging.value = false
  }
}

const handleDragOver = (e: DragEvent) => {
  e.preventDefault()
}

const handleDrop = (e: DragEvent) => {
  e.preventDefault()
  isDragging.value = false
  if (!props.podeEditar) {
    return
  }
  const files = Array.from(e.dataTransfer?.files || [])
  files.forEach(file => processarArquivo(file))
}

const handleFileInput = (e: Event) => {
  const target = e.target as HTMLInputElement
  const files = Array.from(target.files || [])
  files.forEach(file => processarArquivo(file))
  target.value = ''
}

function arquivoPermitido(file: File): boolean {
  const maxSize = 10 * 1024 * 1024
  if (file.size > maxSize) {
    erro.value = 'Arquivo muito grande. Máximo 10MB.'
    return false
  }

  const nome = file.name.toLowerCase()
  const extOk = EXTENSOES.some(ext => nome.endsWith(ext))
  const mimeOk = !file.type || MIME_PERMITIDOS.includes(file.type)

  if (!extOk || !mimeOk) {
    erro.value = 'Tipo de arquivo não permitido. Use PDF, DOC, DOCX, JPG ou PNG.'
    return false
  }

  erro.value = null
  return true
}

const processarArquivo = async (file: File) => {
  if (!props.podeEditar || !props.cidadaoId) {
    return
  }
  if (!arquivoPermitido(file)) {
    return
  }

  isUploading.value = true
  try {
    const tagIds =
      categoriaUpload.value === 'curriculo' ? [...etiquetasUpload.value] : []
    const doc = await crmStore.uploadDocumentoCidadao(
      props.cidadaoId,
      file,
      categoriaUpload.value,
      tagIds,
    )
    documentosLocal.value.unshift(doc)
  } catch (e) {
    erro.value = e instanceof Error ? e.message : 'Falha no upload.'
  } finally {
    isUploading.value = false
  }
}

const atualizandoCategoriaId = ref<string | null>(null)

async function alterarEtiquetasDocumento(doc: CidadaoDocumento, tagId: string) {
  if (!props.podeEditar || doc.categoria !== 'curriculo') return
  const novas = toggleEtiquetaDocumento(doc, tagId)
  atualizandoCategoriaId.value = doc.id
  try {
    const atualizado = await crmStore.updateDocumentoEtiquetas(doc.id, novas)
    const idx = documentosLocal.value.findIndex(d => d.id === doc.id)
    if (idx >= 0) documentosLocal.value[idx] = atualizado
  } catch {
    erro.value = 'Não foi possível atualizar as áreas do currículo.'
  } finally {
    atualizandoCategoriaId.value = null
  }
}

async function alterarCategoria(doc: CidadaoDocumento, categoria: CategoriaDocumentoCidadao) {
  if (!props.podeEditar || doc.categoria === categoria) return
  atualizandoCategoriaId.value = doc.id
  try {
    const atualizado = await crmStore.updateDocumentoCategoria(doc.id, categoria)
    const idx = documentosLocal.value.findIndex(d => d.id === doc.id)
    if (idx >= 0) documentosLocal.value[idx] = atualizado
  } catch {
    erro.value = 'Não foi possível alterar a categoria do documento.'
  } finally {
    atualizandoCategoriaId.value = null
  }
}

const removerDocumento = async (id: string) => {
  if (!props.podeEditar) {
    return
  }
  const confirmado = await showConfirm(
    'Remover este documento?',
    'Remover anexo',
  )
  if (!confirmado) {
    return
  }
  try {
    await crmStore.deleteDocumentoCidadao(id)
    documentosLocal.value = documentosLocal.value.filter(d => d.id !== id)
  } catch {
    await showError('Não foi possível remover o documento.')
  }
}

const baixarDocumento = async (doc: CidadaoDocumento) => {
  try {
    await crmStore.downloadDocumentoCidadao(doc)
  } catch {
    erro.value = 'Não foi possível baixar o arquivo.'
  }
}

const getIcone = (tipo: string) => {
  if (tipo.startsWith('image/')) {
    return ImageIcon
  }
  if (tipo.includes('pdf')) {
    return FileText
  }
  return File
}

const formatarTamanho = (bytes: number) => {
  if (bytes < 1024) {
    return `${bytes} B`
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

const formatarData = (data: string) => {
  return new Date(data).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

<template>
  <div class="space-y-4">
    <p v-if="erro" class="text-sm text-red-600 dark:text-red-400">{{ erro }}</p>

    <div v-if="podeEditar" class="space-y-2">
      <label class="block">
        <span class="label">Tipo de documento <span class="text-red-500">*</span></span>
        <select v-model="categoriaUpload" class="input mt-1">
          <option
            v-for="opt in CATEGORIAS_DOCUMENTO_CIDADAO"
            :key="opt.value"
            :value="opt.value"
          >
            {{ opt.label }}
          </option>
        </select>
      </label>
      <div v-if="categoriaUpload === 'curriculo'" class="mt-2">
        <span class="label text-xs">{{ LABEL_TAGS_CONTEXTO_PROFISSIONAL }}</span>
        <p class="text-xs text-gray-500 dark:text-slate-400 mb-2">
          {{ HINT_CURRICULO_TAGS }}
        </p>
        <p
          v-if="tagsContextoProfissional.length === 0"
          class="text-xs text-amber-700 dark:text-amber-400/90"
        >
          Nenhuma tag de contexto profissional no CRM. Cadastre em Configurações → Classificações
          (tipo «Contexto profissional», módulo CRM).
        </p>
        <div v-else class="flex flex-wrap gap-2">
          <button
            v-for="tag in tagsContextoProfissional"
            :key="tag.id"
            type="button"
            class="text-xs px-2.5 py-1 rounded-full border transition-colors"
            :style="
              etiquetasUpload.includes(tag.id)
                ? { backgroundColor: tag.cor, borderColor: tag.cor, color: '#fff' }
                : { borderColor: tag.cor + '66', color: tag.cor }
            "
            @click="toggleEtiquetaUpload(tag.id)"
          >
            {{ tag.nome }}
          </button>
        </div>
      </div>
    </div>

    <div
      v-if="podeEditar"
      @dragenter="handleDragEnter"
      @dragleave="handleDragLeave"
      @dragover="handleDragOver"
      @drop="handleDrop"
      :class="[
        isDragging
          ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
          : 'border-gray-300 dark:border-slate-600 bg-gray-50 dark:bg-slate-800',
        'relative border-2 border-dashed rounded-lg p-8 transition-colors',
      ]"
    >
      <div class="text-center">
        <Upload
          :class="[
            isDragging ? 'text-primary-600 dark:text-primary-400' : 'text-gray-400 dark:text-slate-500',
            'mx-auto w-12 h-12 mb-4',
          ]"
        />

        <p class="text-sm font-medium text-gray-900 dark:text-slate-100 mb-1">
          {{ isDragging ? 'Solte os arquivos aqui' : 'Arraste arquivos ou clique para selecionar' }}
        </p>

        <p class="text-xs text-gray-500 dark:text-slate-400 mb-4">
          PDF, DOC, DOCX, JPG, PNG até 10MB
        </p>

        <label class="btn btn-secondary cursor-pointer inline-flex items-center gap-2">
          <Upload class="w-4 h-4" />
          Selecionar Arquivos
          <input
            type="file"
            multiple
            accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
            :disabled="isUploading"
            @change="handleFileInput"
            class="hidden"
          />
        </label>
      </div>

      <div v-if="isUploading" class="mt-4 flex items-center justify-center gap-2 text-sm text-gray-600 dark:text-slate-400">
        <Loader2 class="w-4 h-4 animate-spin" />
        <span>Enviando...</span>
      </div>
    </div>

    <div v-else class="text-xs text-gray-500 dark:text-slate-400">
      Você não tem permissão para enviar ou excluir anexos.
    </div>

    <div v-if="documentosLocal.length > 0" class="space-y-2">
      <h5 class="text-sm font-semibold text-gray-900 dark:text-slate-100">
        Documentos ({{ documentosLocal.length }})
      </h5>

      <div class="space-y-2">
        <div
          v-for="doc in documentosLocal"
          :key="doc.id"
          class="flex items-center gap-3 p-3 bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-lg hover:border-primary-300 dark:hover:border-primary-600 transition-colors group"
        >
          <div class="flex-shrink-0 w-10 h-10 bg-gray-100 dark:bg-slate-700 rounded-lg flex items-center justify-center">
            <component :is="getIcone(doc.tipo)" class="w-5 h-5 text-gray-600 dark:text-slate-400" />
          </div>

          <div class="flex-1 min-w-0">
            <p class="font-medium text-gray-900 dark:text-slate-100 truncate">{{ doc.nome }}</p>
            <div v-if="podeEditar" class="mt-1 flex items-center gap-2">
              <label class="text-xs text-gray-500 dark:text-slate-400 shrink-0">Tipo</label>
              <select
                class="input input-sm py-0.5 text-xs max-w-[11rem]"
                :value="doc.categoria"
                :disabled="atualizandoCategoriaId === doc.id"
                @change="alterarCategoria(doc, ($event.target as HTMLSelectElement).value as CategoriaDocumentoCidadao)"
              >
                <option
                  v-for="opt in CATEGORIAS_DOCUMENTO_CIDADAO"
                  :key="opt.value"
                  :value="opt.value"
                >
                  {{ opt.label }}
                </option>
              </select>
            </div>
            <p class="text-xs text-gray-500 dark:text-slate-400 mt-0.5">
              <template v-if="!podeEditar">{{ labelCategoriaDocumento(doc.categoria) }} • </template>
              {{ formatarTamanho(doc.tamanho) }} • {{ formatarData(doc.dataUpload) }}
            </p>
            <div
              v-if="doc.categoria === 'curriculo' && tagsContextoProfissional.length > 0 && podeEditar"
              class="mt-2 flex flex-wrap gap-1.5"
            >
              <button
                v-for="tag in tagsContextoProfissional"
                :key="`${doc.id}-${tag.id}`"
                type="button"
                class="text-[10px] px-2 py-0.5 rounded-full border"
                :disabled="atualizandoCategoriaId === doc.id"
                :style="
                  doc.etiquetas.some(e => e.id === tag.id)
                    ? { backgroundColor: tag.cor, borderColor: tag.cor, color: '#fff' }
                    : { borderColor: tag.cor + '55', color: tag.cor }
                "
                @click="alterarEtiquetasDocumento(doc, tag.id)"
              >
                {{ tag.nome }}
              </button>
            </div>
            <p
              v-else-if="doc.categoria === 'curriculo' && doc.etiquetas.length > 0"
              class="mt-1 flex flex-wrap gap-1"
            >
              <span
                v-for="tag in doc.etiquetas"
                :key="tag.id"
                class="text-[10px] px-2 py-0.5 rounded-full"
                :style="{ backgroundColor: tag.cor + '22', color: tag.cor }"
              >
                {{ tag.nome }}
              </span>
            </p>
          </div>

          <div class="flex items-center gap-2">
            <button
              type="button"
              @click="baixarDocumento(doc)"
              class="text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium opacity-0 group-hover:opacity-100 transition-opacity"
            >
              Baixar
            </button>
            <button
              v-if="podeEditar"
              type="button"
              @click="removerDocumento(doc.id)"
              class="p-1 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 rounded opacity-0 group-hover:opacity-100 transition-opacity"
              title="Remover"
            >
              <X class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-else-if="!isUploading" class="text-center py-8 text-gray-500 dark:text-slate-400 text-sm">
      Nenhum documento anexado ainda
    </div>
  </div>
</template>
