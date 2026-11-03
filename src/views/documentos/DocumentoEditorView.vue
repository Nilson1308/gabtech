<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useDocumentosStore } from '@/stores/documentos'
import { useTemplatesStore } from '@/stores/templates'
import { useAuthStore } from '@/stores/auth'
import { useAlertDialog } from '@/composables/useAlertDialog'
import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'
import { 
  Save,
  Send,
  CheckCircle2,
  ArrowLeft,
  Tag,
  History,
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
  Undo,
  Redo,
  Type,
  Link2,
  Image as ImageIcon,
  Minus,
  Quote,
  Table as TableIcon,
  FileDown,
  FileText,
  Clock
} from 'lucide-vue-next'
import type { Documento, TipoDocumento } from '@/types'
import RastreabilidadeMeta from '@/components/common/RastreabilidadeMeta.vue'
import { AUDITORIA_ALVO } from '@/services/auditoria'
import AssinaturaCropper from '@/components/documentos/AssinaturaCropper.vue'
import TemplateSelector from '@/components/documentos/TemplateSelector.vue'
import TabelaInserter from '@/components/documentos/TabelaInserter.vue'
import HistoricoVersoes from '@/components/documentos/HistoricoVersoes.vue'

const router = useRouter()
const route = useRoute()
const documentosStore = useDocumentosStore()
const templatesStore = useTemplatesStore()
const authStore = useAuthStore()
const { showSuccess, showError, showWarning, showConfirm } = useAlertDialog()

// State
const documento = ref<Documento | null>(null)
const titulo = ref('')
const pastaId = ref<string | undefined>(undefined)
const conteudo = ref('')
const etiquetasSelecionadas = ref<string[]>([])
const salvando = ref(false)
const editorRef = ref<HTMLDivElement | null>(null)
const tamanhFonte = ref('3')
const corTexto = ref('#1f2937')
const assinaturaUrl = ref<string | null>(null)
const uploadingAssinatura = ref(false)
const assinaturaTempUrl = ref<string | null>(null)

// Modals
const mostrarCropper = ref(false)
const mostrarTemplateSelector = ref(false)
const mostrarTabelaInserter = ref(false)
const mostrarHistorico = ref(false)

const isNovoDocumento = computed(() => route.params.id === 'novo')
const tipoDocumento = computed(() => {
  if (documento.value) {
    return documento.value.tipo
  }
  return (route.query.tipo as TipoDocumento) || 'oficio'
})

const podeAssinar = computed(() => authStore.hasPermission('sign_docs'))
const podeEditar = computed(() => authStore.hasPermission('editar_docs'))
const podeSalvar = computed(() => authStore.hasPermission('criar_docs') || authStore.hasPermission('editar_docs'))

onMounted(async () => {
  await Promise.all([
    documentosStore.initialize(),
    templatesStore.initialize(),
    documentosStore.fetchMinhaAssinaturaVisual().then(url => {
      if (url) assinaturaUrl.value = url
    }),
  ])
  
  if (!isNovoDocumento.value) {
    const docId = route.params.id as string
    const doc = await documentosStore.fetchDocumentoById(docId)

    if (doc) {
      documento.value = doc
      titulo.value = doc.titulo
      pastaId.value = doc.pastaId
      conteudo.value = doc.conteudo
      etiquetasSelecionadas.value = doc.etiquetas.map(e => e.id)
      if (editorRef.value) {
        editorRef.value.innerHTML = doc.conteudo
      }
    } else {
      router.push('/documentos')
    }
  } else {
    // Novo documento - carregar template padrão
    const template = templatesStore.getDefaultTemplate(tipoDocumento.value)
    titulo.value = getTituloTemplate(tipoDocumento.value)
    conteudo.value = template?.conteudo || getConteudoTemplate(tipoDocumento.value)
  }
})

watch(conteudo, (novoConteudo) => {
  if (editorRef.value && editorRef.value.innerHTML !== novoConteudo) {
    editorRef.value.innerHTML = novoConteudo
  }
})

// Métodos de Edição
function execCommand(command: string, value: string | undefined = undefined) {
  document.execCommand(command, false, value)
  atualizarConteudo()
}

function atualizarConteudo() {
  if (editorRef.value) {
    conteudo.value = editorRef.value.innerHTML
  }
}

function inserirLink() {
  const url = prompt('Digite a URL:')
  if (url) {
    execCommand('createLink', url)
  }
}

function inserirLinha() {
  execCommand('insertHorizontalRule')
}

function inserirAssinatura() {
  if (!assinaturaUrl.value) {
    showWarning('Por favor, faça upload de uma assinatura primeiro.')
    return
  }
  
  const img = `<img src="${assinaturaUrl.value}" alt="Assinatura" style="max-width: 200px; height: auto; display: block; margin: 1rem 0;" />`
  document.execCommand('insertHTML', false, img)
  atualizarConteudo()
}

function abrirTabelaInserter() {
  mostrarTabelaInserter.value = true
}

function inserirTabela(config: { rows: number; cols: number }) {
  let tableHtml = '<table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%; margin: 1rem 0;">'
  
  for (let i = 0; i < config.rows; i++) {
    tableHtml += '<tr>'
    for (let j = 0; j < config.cols; j++) {
      if (i === 0) {
        tableHtml += '<th style="border: 1px solid #ccc; padding: 8px; background-color: #f3f4f6;">&nbsp;</th>'
      } else {
        tableHtml += '<td style="border: 1px solid #ccc; padding: 8px;">&nbsp;</td>'
      }
    }
    tableHtml += '</tr>'
  }
  
  tableHtml += '</table><p>&nbsp;</p>'
  
  document.execCommand('insertHTML', false, tableHtml)
  atualizarConteudo()
  mostrarTabelaInserter.value = false
}

async function handleAssinaturaUpload(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  
  if (!file) return
  
  if (!file.type.startsWith('image/')) {
    showError('Por favor, selecione uma imagem.')
    return
  }
  
  if (file.size > 2 * 1024 * 1024) {
    showError('A imagem deve ter no máximo 2MB.')
    return
  }
  
  uploadingAssinatura.value = true
  
  try {
    const reader = new FileReader()
    reader.onload = (e) => {
      assinaturaTempUrl.value = e.target?.result as string
      mostrarCropper.value = true
      uploadingAssinatura.value = false
    }
    reader.readAsDataURL(file)
  } catch (error) {
    uploadingAssinatura.value = false
    showError('Erro ao processar imagem')
  }
}

async function confirmarAssinaturaCrop(croppedImage: string) {
  mostrarCropper.value = false
  assinaturaTempUrl.value = null
  uploadingAssinatura.value = true
  try {
    const url = await documentosStore.uploadMinhaAssinaturaVisual(croppedImage)
    assinaturaUrl.value = url
    showSuccess('Assinatura visual salva no seu usuário.')
  } catch {
    showError('Não foi possível salvar a assinatura. Tente novamente.')
  } finally {
    uploadingAssinatura.value = false
  }
}

function cancelarCrop() {
  mostrarCropper.value = false
  assinaturaTempUrl.value = null
}

// Exportar PDF
async function exportarPDF() {
  if (!editorRef.value) return
  
  salvando.value = true
  
  try {
    const canvas = await html2canvas(editorRef.value, {
      scale: 2,
      useCORS: true,
      logging: false,
      backgroundColor: '#ffffff'
    })
    
    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF('p', 'mm', 'a4')
    
    const imgWidth = 210 // A4 width in mm
    const imgHeight = (canvas.height * imgWidth) / canvas.width
    let heightLeft = imgHeight
    let position = 0
    
    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
    heightLeft -= 297 // A4 height in mm
    
    while (heightLeft >= 0) {
      position = heightLeft - imgHeight
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
      heightLeft -= 297
    }
    
    const fileName = `${titulo.value || 'documento'}.pdf`
    pdf.save(fileName)
    
    showSuccess('PDF exportado com sucesso!')
  } catch (error) {
    console.error('Erro ao exportar PDF:', error)
    showError('Erro ao exportar PDF. Tente novamente.')
  } finally {
    salvando.value = false
  }
}

// Salvar
async function salvarRascunho() {
  if (!podeSalvar.value) return
  
  salvando.value = true
  
  try {
    if (isNovoDocumento.value) {
      const novoDoc = await documentosStore.createDocumento({
        titulo: titulo.value || 'Documento sem título',
        tipo: tipoDocumento.value,
        pastaId: pastaId.value,
        conteudo: conteudo.value,
        etiquetaIds: etiquetasSelecionadas.value,
      })
      
      router.replace(`/documentos/editor/${novoDoc.id}`)
    } else {
      const atualizado = await documentosStore.updateDocumento(documento.value!.id, {
        titulo: titulo.value,
        pastaId: pastaId.value,
        conteudo: conteudo.value,
        etiquetaIds: etiquetasSelecionadas.value,
      })
      documento.value = atualizado
    }
    
    showSuccess('Documento salvo com sucesso!')
  } catch (error) {
    showError('Erro ao salvar documento')
  } finally {
    salvando.value = false
  }
}

async function enviarParaAssinatura() {
  if (!documento.value) return
  
  salvando.value = true
  
  try {
    await documentosStore.changeStatus(documento.value.id, 'aguardando_assinatura')
    showSuccess('Documento enviado para assinatura!')
    voltar()
  } catch (error) {
    showError('Erro ao enviar documento')
  } finally {
    salvando.value = false
  }
}

async function assinarFinalizar() {
  if (!documento.value || !podeAssinar.value) return
  
  const confirmed = await showConfirm('Ao assinar, o documento será finalizado e não poderá mais ser editado. Confirma?')
  if (!confirmed) return
  
  salvando.value = true
  
  try {
    await documentosStore.changeStatus(documento.value.id, 'finalizado')
    showSuccess('Documento assinado e finalizado com sucesso!')
    voltar()
  } catch (error) {
    showError('Erro ao finalizar documento')
  } finally {
    salvando.value = false
  }
}

function voltar() {
  router.push('/documentos')
}

function selecionarTemplate(template: any) {
  conteudo.value = template.conteudo
  if (editorRef.value) {
    editorRef.value.innerHTML = template.conteudo
  }
  mostrarTemplateSelector.value = false
}

function abrirHistorico() {
  if (documento.value) {
    mostrarHistorico.value = true
  }
}

async function restaurarVersao(versaoNumero: number) {
  if (!documento.value) return

  const confirmed = await showConfirm(
    `Restaurar a versão ${versaoNumero}? O conteúdo atual será preservado no histórico.`,
  )
  if (!confirmed) return

  try {
    const atualizado = await documentosStore.restaurarVersao(documento.value.id, versaoNumero)
    documento.value = atualizado
    titulo.value = atualizado.titulo
    conteudo.value = atualizado.conteudo
    if (editorRef.value) {
      editorRef.value.innerHTML = atualizado.conteudo
    }
    showSuccess(`Versão ${versaoNumero} restaurada com sucesso.`)
  } catch {
    showError('Não foi possível restaurar a versão.')
  } finally {
    mostrarHistorico.value = false
  }
}

// Templates
function getTituloTemplate(tipo: TipoDocumento): string {
  const templates: Record<TipoDocumento, string> = {
    oficio: 'Ofício nº ___/2026',
    memorando: 'Memorando Interno nº ___/2026',
    requerimento: 'Requerimento de Informações',
    projeto_lei: 'Projeto de Lei nº ___/2026',
    ata: 'Ata de Reunião nº ___/2026',
    declaracao: 'Declaração',
    parecer: 'Parecer Técnico nº ___/2026',
    relatorio: 'Relatório - [Título]',
    mocao: 'Moção nº ___/2026',
    indicacao: 'Indicação nº ___/2026',
    generico: 'Novo Documento'
  }
  return templates[tipo] || 'Novo Documento'
}

function getConteudoTemplate(_tipo: TipoDocumento): string {
  return '<p>Conteúdo do documento...</p>'
}

function getTipoLabel(tipo: TipoDocumento): string {
  const labels: Record<TipoDocumento, string> = {
    oficio: 'Ofício',
    memorando: 'Memorando',
    requerimento: 'Requerimento',
    projeto_lei: 'Projeto de Lei',
    ata: 'Ata',
    declaracao: 'Declaração',
    parecer: 'Parecer',
    relatorio: 'Relatório',
    mocao: 'Moção',
    indicacao: 'Indicação',
    generico: 'Genérico'
  }
  return labels[tipo] || tipo
}
</script>

<template>
  <div class="flex flex-col h-[calc(100vh-8rem)]">
    <!-- Header do Editor -->
    <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 mb-4 flex-shrink-0">
      <div class="flex items-start justify-between gap-4">
        <div class="flex-1 min-w-0">
          <!-- Botão Voltar -->
          <button
            @click="voltar"
            class="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 mb-3"
          >
            <ArrowLeft class="w-4 h-4" />
            Voltar para Documentos
          </button>

          <!-- Título do Documento -->
          <input
            v-model="titulo"
            type="text"
            placeholder="Título do documento"
            :disabled="documento?.status === 'finalizado'"
            class="w-full text-2xl font-bold text-gray-900 dark:text-gray-100 bg-transparent border-0 border-b-2 border-transparent focus:border-primary-500 dark:focus:border-primary-400 focus:outline-none px-0 py-1 placeholder-gray-400 dark:placeholder-gray-500 disabled:opacity-60"
          />

          <!-- Metadados -->
          <div class="flex items-center gap-4 mt-3 text-sm">
            <span class="inline-flex items-center gap-1 text-gray-600 dark:text-gray-400">
              <Type class="w-4 h-4" />
              {{ getTipoLabel(documento?.tipo || tipoDocumento) }}
            </span>

            <span v-if="documento?.autor" class="inline-flex items-center gap-2 text-gray-600 dark:text-gray-400">
              <img
                :src="documento.autor.avatar"
                :alt="documento.autor.nome"
                class="w-5 h-5 rounded-full"
              />
              {{ documento.autor.nome }}
            </span>

            <RastreabilidadeMeta
              v-if="documento"
              :rastreabilidade="documento.rastreabilidade"
              :alvo-auditoria="AUDITORIA_ALVO.documento(documento.id)"
              historico-titulo="Histórico do documento"
            />
            <span
              v-if="documento && !documento.rastreabilidade?.ultimaAcaoEm && documento.updatedAt"
              class="text-gray-500 dark:text-gray-500"
            >
              Atualizado em {{ new Date(documento.updatedAt).toLocaleString('pt-BR') }}
            </span>
          </div>
        </div>

        <!-- Botões de Ação -->
        <div class="flex items-center gap-2 flex-shrink-0 flex-wrap">
          <!-- Templates -->
          <button
            v-if="podeEditar && (!documento || documento.status !== 'finalizado')"
            @click="mostrarTemplateSelector = true"
            class="flex items-center gap-2 px-3 py-2 bg-purple-100 hover:bg-purple-200 dark:bg-purple-900/30 dark:hover:bg-purple-900/50 text-purple-700 dark:text-purple-400 rounded-lg font-medium transition-colors text-sm"
            title="Selecionar template"
          >
            <FileText class="w-4 h-4" />
            Template
          </button>

          <!-- Histórico -->
          <button
            v-if="documento"
            @click="abrirHistorico"
            class="flex items-center gap-2 px-3 py-2 bg-blue-100 hover:bg-blue-200 dark:bg-blue-900/30 dark:hover:bg-blue-900/50 text-blue-700 dark:text-blue-400 rounded-lg font-medium transition-colors text-sm"
            title="Ver histórico"
          >
            <Clock class="w-4 h-4" />
            Histórico
          </button>

          <!-- Exportar PDF -->
          <button
            @click="exportarPDF"
            :disabled="salvando"
            class="flex items-center gap-2 px-3 py-2 bg-green-100 hover:bg-green-200 dark:bg-green-900/30 dark:hover:bg-green-900/50 text-green-700 dark:text-green-400 rounded-lg font-medium transition-colors disabled:opacity-50 text-sm"
          >
            <FileDown class="w-4 h-4" />
            Exportar PDF
          </button>

          <!-- Pasta -->
          <select
            v-model="pastaId"
            :disabled="documento?.status === 'finalizado'"
            class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400 disabled:opacity-60 text-sm"
          >
            <option :value="undefined">Sem pasta</option>
            <option
              v-for="pasta in documentosStore.pastas"
              :key="pasta.id"
              :value="pasta.id"
            >
              {{ pasta.nome }}
            </option>
          </select>

          <!-- Salvar Rascunho -->
          <button
            v-if="podeSalvar && documento?.status !== 'finalizado'"
            @click="salvarRascunho"
            :disabled="salvando"
            class="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 dark:text-gray-100 rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            <Save class="w-4 h-4" />
            Salvar
          </button>

          <!-- Enviar para Assinatura -->
          <button
            v-if="documento && documento.status === 'rascunho' && podeEditar"
            @click="enviarParaAssinatura"
            :disabled="salvando"
            class="flex items-center gap-2 px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            <Send class="w-4 h-4" />
            Enviar para Assinatura
          </button>

          <!-- Assinar e Finalizar -->
          <button
            v-if="documento && documento.status === 'aguardando_assinatura' && podeAssinar"
            @click="assinarFinalizar"
            :disabled="salvando"
            class="flex items-center gap-2 px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            <CheckCircle2 class="w-4 h-4" />
            Assinar e Finalizar
          </button>
        </div>
      </div>
    </div>

    <!-- Corpo Principal -->
    <div class="flex-1 flex gap-4 min-h-0">
      <!-- Editor -->
      <div class="flex-1 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden flex flex-col">
        <!-- Barra de Ferramentas -->
        <div
          v-if="documento?.status !== 'finalizado'"
          class="flex items-center gap-1 p-2 border-b border-gray-200 dark:border-gray-700 flex-wrap bg-gray-50 dark:bg-gray-900"
        >
          <!-- Tamanho da Fonte -->
          <select
            v-model="tamanhFonte"
            @change="execCommand('fontSize', tamanhFonte)"
            class="px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm focus:outline-none focus:ring-1 focus:ring-primary-500"
            title="Tamanho da fonte"
          >
            <option value="1">8pt</option>
            <option value="2">10pt</option>
            <option value="3">12pt</option>
            <option value="4">14pt</option>
            <option value="5">18pt</option>
            <option value="6">24pt</option>
            <option value="7">36pt</option>
          </select>

          <div class="w-px h-6 bg-gray-300 dark:bg-gray-600 mx-1"></div>

          <!-- Formatação de Texto -->
          <button
            @click="execCommand('bold')"
            class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
            title="Negrito (Ctrl+B)"
          >
            <Bold class="w-4 h-4 text-gray-700 dark:text-gray-300" />
          </button>

          <button
            @click="execCommand('italic')"
            class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
            title="Itálico (Ctrl+I)"
          >
            <Italic class="w-4 h-4 text-gray-700 dark:text-gray-300" />
          </button>

          <button
            @click="execCommand('underline')"
            class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
            title="Sublinhado (Ctrl+U)"
          >
            <Underline class="w-4 h-4 text-gray-700 dark:text-gray-300" />
          </button>

          <button
            @click="execCommand('strikeThrough')"
            class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
            title="Tachado"
          >
            <Strikethrough class="w-4 h-4 text-gray-700 dark:text-gray-300" />
          </button>

          <div class="w-px h-6 bg-gray-300 dark:bg-gray-600 mx-1"></div>

          <!-- Cor do Texto -->
          <div class="relative">
            <input
              v-model="corTexto"
              type="color"
              @change="execCommand('foreColor', corTexto)"
              class="w-8 h-8 rounded cursor-pointer border border-gray-300 dark:border-gray-600"
              title="Cor do texto"
            />
          </div>

          <div class="w-px h-6 bg-gray-300 dark:bg-gray-600 mx-1"></div>

          <!-- Alinhamento -->
          <button
            @click="execCommand('justifyLeft')"
            class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
            title="Alinhar à esquerda"
          >
            <AlignLeft class="w-4 h-4 text-gray-700 dark:text-gray-300" />
          </button>

          <button
            @click="execCommand('justifyCenter')"
            class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
            title="Centralizar"
          >
            <AlignCenter class="w-4 h-4 text-gray-700 dark:text-gray-300" />
          </button>

          <button
            @click="execCommand('justifyRight')"
            class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
            title="Alinhar à direita"
          >
            <AlignRight class="w-4 h-4 text-gray-700 dark:text-gray-300" />
          </button>

          <button
            @click="execCommand('justifyFull')"
            class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
            title="Justificar"
          >
            <AlignJustify class="w-4 h-4 text-gray-700 dark:text-gray-300" />
          </button>

          <div class="w-px h-6 bg-gray-300 dark:bg-gray-600 mx-1"></div>

          <!-- Listas -->
          <button
            @click="execCommand('insertUnorderedList')"
            class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
            title="Lista não ordenada"
          >
            <List class="w-4 h-4 text-gray-700 dark:text-gray-300" />
          </button>

          <button
            @click="execCommand('insertOrderedList')"
            class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
            title="Lista ordenada"
          >
            <ListOrdered class="w-4 h-4 text-gray-700 dark:text-gray-300" />
          </button>

          <div class="w-px h-6 bg-gray-300 dark:bg-gray-600 mx-1"></div>

          <!-- Inserir -->
          <button
            @click="inserirLink"
            class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
            title="Inserir link"
          >
            <Link2 class="w-4 h-4 text-gray-700 dark:text-gray-300" />
          </button>

          <button
            @click="abrirTabelaInserter"
            class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
            title="Inserir tabela"
          >
            <TableIcon class="w-4 h-4 text-gray-700 dark:text-gray-300" />
          </button>

          <button
            @click="inserirLinha"
            class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
            title="Inserir linha horizontal"
          >
            <Minus class="w-4 h-4 text-gray-700 dark:text-gray-300" />
          </button>

          <button
            @click="execCommand('formatBlock', 'blockquote')"
            class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
            title="Citação"
          >
            <Quote class="w-4 h-4 text-gray-700 dark:text-gray-300" />
          </button>

          <div class="w-px h-6 bg-gray-300 dark:bg-gray-600 mx-1"></div>

          <!-- Desfazer/Refazer -->
          <button
            @click="execCommand('undo')"
            class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
            title="Desfazer (Ctrl+Z)"
          >
            <Undo class="w-4 h-4 text-gray-700 dark:text-gray-300" />
          </button>

          <button
            @click="execCommand('redo')"
            class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
            title="Refazer (Ctrl+Y)"
          >
            <Redo class="w-4 h-4 text-gray-700 dark:text-gray-300" />
          </button>

          <div class="w-px h-6 bg-gray-300 dark:bg-gray-600 mx-1"></div>

          <!-- Inserir Assinatura -->
          <button
            @click="inserirAssinatura"
            :disabled="!assinaturaUrl"
            class="flex items-center gap-1 px-3 py-1.5 bg-primary-50 hover:bg-primary-100 dark:bg-primary-900/30 dark:hover:bg-primary-900/50 text-primary-700 dark:text-primary-400 rounded transition-colors text-sm font-medium disabled:opacity-40 disabled:cursor-not-allowed"
            title="Inserir assinatura visual"
          >
            <ImageIcon class="w-4 h-4" />
            Inserir Assinatura
          </button>
        </div>

        <!-- Área de Edição (Folha A4) -->
        <div class="flex-1 overflow-y-auto p-8 bg-gray-100 dark:bg-slate-900">
          <div
            ref="editorRef"
            contenteditable="true"
            @input="atualizarConteudo"
            :class="[
              documento?.status === 'finalizado' && 'pointer-events-none',
              'bg-white dark:bg-gray-50 shadow-lg mx-auto p-16 min-h-[29.7cm] w-[21cm] focus:outline-none focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400 rounded'
            ]"
            style="font-family: Arial, sans-serif; color: #1f2937; line-height: 1.6;"
          >
            <!-- Conteúdo será inserido via innerHTML -->
          </div>
        </div>
      </div>

      <!-- Painel Lateral Direito - Metadados -->
      <aside class="w-64 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 overflow-y-auto flex-shrink-0">
        <!-- Status -->
        <div class="mb-6">
          <h3 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
            Status
          </h3>
          <span
            v-if="documento"
            :class="[
              documento.status === 'rascunho' && 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
              documento.status === 'aguardando_assinatura' && 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
              documento.status === 'finalizado' && 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400',
              'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium'
            ]"
          >
            {{ documento.status === 'rascunho' ? 'Rascunho' : documento.status === 'aguardando_assinatura' ? 'Aguardando Assinatura' : 'Finalizado' }}
          </span>
          <span v-else class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300">
            Novo Documento
          </span>
        </div>

        <!-- Upload de Assinatura Visual -->
        <div class="mb-6 pb-6 border-b border-gray-200 dark:border-gray-700">
          <h3 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-1">
            <ImageIcon class="w-3 h-3" />
            Assinatura Visual
          </h3>
          
          <!-- Preview da Assinatura -->
          <div v-if="assinaturaUrl" class="mb-3 p-3 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
            <img 
              :src="assinaturaUrl" 
              alt="Assinatura" 
              class="w-full h-auto max-h-24 object-contain"
            />
          </div>

          <!-- Botão de Upload -->
          <label 
            class="flex items-center justify-center gap-2 px-3 py-2 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg cursor-pointer transition-colors text-sm font-medium"
          >
            <ImageIcon class="w-4 h-4" />
            {{ assinaturaUrl ? 'Alterar' : 'Fazer Upload' }}
            <input
              type="file"
              accept="image/*"
              @change="handleAssinaturaUpload"
              class="hidden"
            />
          </label>
          
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">
            PNG/JPG/WebP até 2MB. Após recortar, a imagem fica salva no seu usuário e pode ser
            reinserida em outros documentos.
          </p>
        </div>

        <!-- Etiquetas -->
        <div class="mb-6">
          <h3 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-1">
            <Tag class="w-3 h-3" />
            Etiquetas
          </h3>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="etiqueta in documentosStore.etiquetas"
              :key="etiqueta.id"
              @click="() => {
                const index = etiquetasSelecionadas.indexOf(etiqueta.id)
                if (index > -1) {
                  etiquetasSelecionadas.splice(index, 1)
                } else {
                  etiquetasSelecionadas.push(etiqueta.id)
                }
              }"
              :disabled="documento?.status === 'finalizado'"
              :class="[
                etiquetasSelecionadas.includes(etiqueta.id) ? 'ring-2 ring-offset-1 ring-offset-white dark:ring-offset-gray-800' : 'opacity-50',
                'px-2 py-1 rounded text-xs font-medium text-white transition-all disabled:opacity-30'
              ]"
              :style="{ 
                backgroundColor: etiqueta.cor,
                ...(etiquetasSelecionadas.includes(etiqueta.id) ? { '--tw-ring-color': etiqueta.cor } : {})
              }"
            >
              {{ etiqueta.nome }}
            </button>
          </div>
        </div>

        <!-- Histórico de Versões -->
        <div v-if="documento">
          <h3 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2 flex items-center gap-1">
            <History class="w-3 h-3" />
            Histórico
          </h3>
          <div class="space-y-2">
            <div class="text-sm text-gray-600 dark:text-gray-400 border-l-2 border-primary-500 dark:border-primary-400 pl-3">
              <p class="font-medium text-gray-900 dark:text-gray-100">Versão {{ documento.versaoAtual }}</p>
              <p class="text-xs">Editado por {{ documento.autor.nome }}</p>
              <p class="text-xs">{{ new Date(documento.updatedAt).toLocaleString('pt-BR') }}</p>
            </div>
            
            <div v-if="documento.createdAt !== documento.updatedAt" class="text-sm text-gray-600 dark:text-gray-400 border-l-2 border-gray-300 dark:border-gray-600 pl-3">
              <p class="font-medium text-gray-900 dark:text-gray-100">Versão 1 (Criação)</p>
              <p class="text-xs">{{ documento.autor.nome }}</p>
              <p class="text-xs">{{ new Date(documento.createdAt).toLocaleString('pt-BR') }}</p>
            </div>
          </div>
        </div>
      </aside>
    </div>

    <!-- Modals -->
    <AssinaturaCropper
      v-if="mostrarCropper && assinaturaTempUrl"
      :image-url="assinaturaTempUrl"
      @confirm="confirmarAssinaturaCrop"
      @cancel="cancelarCrop"
    />

    <TemplateSelector
      v-if="mostrarTemplateSelector"
      :templates="templatesStore.templates"
      :tipo="tipoDocumento"
      @select="selecionarTemplate"
      @close="mostrarTemplateSelector = false"
    />

    <TabelaInserter
      v-if="mostrarTabelaInserter"
      @insert="inserirTabela"
      @close="mostrarTabelaInserter = false"
    />

    <HistoricoVersoes
      v-if="mostrarHistorico && documento"
      :documento="documento"
      @restore="restaurarVersao"
      @close="mostrarHistorico = false"
    />
  </div>
</template>

<style scoped>
[contenteditable] {
  caret-color: #3b82f6;
}

[contenteditable]:focus {
  outline: none;
}
</style>
