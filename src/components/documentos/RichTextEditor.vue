<script setup lang="ts">
import { ref, watch, onMounted, nextTick } from 'vue'
import {
  Bold,
  Italic,
  Underline,
  Strikethrough,
  AlignLeft,
  AlignCenter,
  AlignRight,
  AlignJustify,
  List,
  ListOrdered,
  Link2,
  Minus,
  Undo,
  Redo,
  Braces,
} from 'lucide-vue-next'

const props = withDefaults(
  defineProps<{
    modelValue: string
    disabled?: boolean
    minHeight?: string
    placeholder?: string
  }>(),
  {
    disabled: false,
    minHeight: '280px',
    placeholder: 'Digite o conteúdo...',
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const editorRef = ref<HTMLDivElement | null>(null)
const tamanhoFonte = ref('3')
const corTexto = ref('#1f2937')
const sincronizando = ref(false)

function emitConteudo() {
  if (!editorRef.value || props.disabled) return
  emit('update:modelValue', editorRef.value.innerHTML)
}

function aplicarHtmlExterno(html: string) {
  if (!editorRef.value) return
  sincronizando.value = true
  editorRef.value.innerHTML = html || ''
  sincronizando.value = false
}

watch(
  () => props.modelValue,
  novo => {
    if (sincronizando.value || !editorRef.value) return
    if (editorRef.value.innerHTML !== novo) {
      aplicarHtmlExterno(novo)
    }
  },
)

onMounted(async () => {
  await nextTick()
  aplicarHtmlExterno(props.modelValue)
})

function execCommand(command: string, value?: string) {
  if (props.disabled) return
  editorRef.value?.focus()
  document.execCommand(command, false, value)
  emitConteudo()
}

function inserirLink() {
  if (props.disabled) return
  const url = prompt('Digite a URL:')
  if (url) execCommand('createLink', url)
}

function inserirLinha() {
  execCommand('insertHorizontalRule')
}

function inserirVariavel() {
  if (props.disabled) return
  const nome = prompt('Nome da variável (será inserida como [NOME]):')
  if (!nome?.trim()) return
  const token = `[${nome.trim().toUpperCase()}]`
  editorRef.value?.focus()
  document.execCommand('insertText', false, token)
  emitConteudo()
}

function onInput() {
  emitConteudo()
}

function onPaste(event: ClipboardEvent) {
  event.preventDefault()
  const text = event.clipboardData?.getData('text/plain') ?? ''
  document.execCommand('insertText', false, text)
  emitConteudo()
}
</script>

<template>
  <div
    class="rounded-lg border border-gray-300 dark:border-gray-600 overflow-hidden bg-white dark:bg-gray-800"
    :class="{ 'opacity-60 pointer-events-none': disabled }"
  >
    <div
      class="flex items-center gap-1 p-2 flex-wrap border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900"
    >
      <select
        v-model="tamanhoFonte"
        class="px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm"
        title="Tamanho da fonte"
        @change="execCommand('fontSize', tamanhoFonte)"
      >
        <option value="1">8pt</option>
        <option value="2">10pt</option>
        <option value="3">12pt</option>
        <option value="4">14pt</option>
        <option value="5">18pt</option>
        <option value="6">24pt</option>
        <option value="7">36pt</option>
      </select>

      <div class="w-px h-6 bg-gray-300 dark:bg-gray-600 mx-1" />

      <button
        type="button"
        class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors text-gray-700 dark:text-gray-300"
        title="Negrito"
        @click="execCommand('bold')"
      >
        <Bold class="w-4 h-4" />
      </button>
      <button
        type="button"
        class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors text-gray-700 dark:text-gray-300"
        title="Itálico"
        @click="execCommand('italic')"
      >
        <Italic class="w-4 h-4" />
      </button>
      <button
        type="button"
        class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors text-gray-700 dark:text-gray-300"
        title="Sublinhado"
        @click="execCommand('underline')"
      >
        <Underline class="w-4 h-4" />
      </button>
      <button
        type="button"
        class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors text-gray-700 dark:text-gray-300"
        title="Tachado"
        @click="execCommand('strikeThrough')"
      >
        <Strikethrough class="w-4 h-4" />
      </button>

      <div class="w-px h-6 bg-gray-300 dark:bg-gray-600 mx-1" />

      <input
        v-model="corTexto"
        type="color"
        class="w-8 h-8 rounded cursor-pointer border border-gray-300 dark:border-gray-600"
        title="Cor do texto"
        @change="execCommand('foreColor', corTexto)"
      />

      <div class="w-px h-6 bg-gray-300 dark:bg-gray-600 mx-1" />

      <button
        type="button"
        class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors text-gray-700 dark:text-gray-300"
        title="Esquerda"
        @click="execCommand('justifyLeft')"
      >
        <AlignLeft class="w-4 h-4" />
      </button>
      <button
        type="button"
        class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors text-gray-700 dark:text-gray-300"
        title="Centro"
        @click="execCommand('justifyCenter')"
      >
        <AlignCenter class="w-4 h-4" />
      </button>
      <button
        type="button"
        class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors text-gray-700 dark:text-gray-300"
        title="Direita"
        @click="execCommand('justifyRight')"
      >
        <AlignRight class="w-4 h-4" />
      </button>
      <button
        type="button"
        class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors text-gray-700 dark:text-gray-300"
        title="Justificar"
        @click="execCommand('justifyFull')"
      >
        <AlignJustify class="w-4 h-4" />
      </button>

      <div class="w-px h-6 bg-gray-300 dark:bg-gray-600 mx-1" />

      <button
        type="button"
        class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors text-gray-700 dark:text-gray-300"
        title="Lista"
        @click="execCommand('insertUnorderedList')"
      >
        <List class="w-4 h-4" />
      </button>
      <button
        type="button"
        class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors text-gray-700 dark:text-gray-300"
        title="Lista numerada"
        @click="execCommand('insertOrderedList')"
      >
        <ListOrdered class="w-4 h-4" />
      </button>

      <div class="w-px h-6 bg-gray-300 dark:bg-gray-600 mx-1" />

      <button
        type="button"
        class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors text-gray-700 dark:text-gray-300"
        title="Link"
        @click="inserirLink"
      >
        <Link2 class="w-4 h-4" />
      </button>
      <button
        type="button"
        class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors text-gray-700 dark:text-gray-300"
        title="Linha horizontal"
        @click="inserirLinha"
      >
        <Minus class="w-4 h-4" />
      </button>
      <button
        type="button"
        class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors text-gray-700 dark:text-gray-300"
        title="Inserir variável"
        @click="inserirVariavel"
      >
        <Braces class="w-4 h-4" />
      </button>

      <div class="w-px h-6 bg-gray-300 dark:bg-gray-600 mx-1" />

      <button
        type="button"
        class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors text-gray-700 dark:text-gray-300"
        title="Desfazer"
        @click="execCommand('undo')"
      >
        <Undo class="w-4 h-4" />
      </button>
      <button
        type="button"
        class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors text-gray-700 dark:text-gray-300"
        title="Refazer"
        @click="execCommand('redo')"
      >
        <Redo class="w-4 h-4" />
      </button>
    </div>

    <div
      ref="editorRef"
      contenteditable="true"
      class="documento-rich-editor px-4 py-3 text-gray-900 dark:text-gray-100 outline-none overflow-y-auto prose prose-sm max-w-none dark:prose-invert"
      :style="{ minHeight }"
      :data-placeholder="placeholder"
      @input="onInput"
      @blur="emitConteudo"
      @paste="onPaste"
    />
  </div>
</template>

<style scoped>
.documento-rich-editor:empty::before {
  content: attr(data-placeholder);
  color: #9ca3af;
  pointer-events: none;
}

:global(.dark) .documento-rich-editor:empty::before {
  color: #6b7280;
}

.documento-rich-editor :deep(p) {
  margin-bottom: 0.75rem;
}

.documento-rich-editor :deep(ul),
.documento-rich-editor :deep(ol) {
  margin-left: 1.25rem;
  margin-bottom: 0.75rem;
}
</style>
