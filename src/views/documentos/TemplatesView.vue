<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTemplatesStore } from '@/stores/templates'
import { useAuthStore } from '@/stores/auth'
import { useAlertDialog } from '@/composables/useAlertDialog'
import type { Template } from '@/stores/templates'
import type { TipoDocumento } from '@/types'
import RichTextEditor from '@/components/documentos/RichTextEditor.vue'
import { 
  FileText, 
  Plus,
  Search,
  Edit,
  Trash2,
  Eye,
  Filter,
  X,
  Save,
  Copy,
  ArrowLeft
} from 'lucide-vue-next'

const router = useRouter()
const templatesStore = useTemplatesStore()
const authStore = useAuthStore()
const { showSuccess, showError, showConfirm } = useAlertDialog()

const busca = ref('')
const filtroTipo = ref<TipoDocumento | 'todos'>('todos')
const templateSelecionado = ref<Template | null>(null)
const modoEdicao = ref<'criar' | 'editar' | 'visualizar' | null>(null)

// Form data
const form = ref({
  nome: '',
  tipo: 'generico' as TipoDocumento,
  descricao: '',
  conteudo: '',
  isDefault: false,
})

const tiposDocumento: Array<{ value: TipoDocumento; label: string }> = [
  { value: 'oficio', label: 'Ofício' },
  { value: 'memorando', label: 'Memorando' },
  { value: 'requerimento', label: 'Requerimento' },
  { value: 'projeto_lei', label: 'Projeto de Lei' },
  { value: 'ata', label: 'Ata' },
  { value: 'declaracao', label: 'Declaração' },
  { value: 'parecer', label: 'Parecer' },
  { value: 'relatorio', label: 'Relatório' },
  { value: 'mocao', label: 'Moção' },
  { value: 'indicacao', label: 'Indicação' },
  { value: 'generico', label: 'Genérico' },
]

onMounted(async () => {
  await templatesStore.fetchTemplates()
})

const templatesFiltrados = computed(() => {
  let templates = templatesStore.templates

  // Filtrar por busca
  if (busca.value.trim()) {
    const query = busca.value.toLowerCase()
    templates = templates.filter(t => 
      t.nome.toLowerCase().includes(query) ||
      (t.descricao && t.descricao.toLowerCase().includes(query))
    )
  }

  // Filtrar por tipo
  if (filtroTipo.value !== 'todos') {
    templates = templates.filter(t => t.tipo === filtroTipo.value)
  }

  return templates.sort((a, b) => {
    // Templates padrão primeiro
    if (a.isDefault && !b.isDefault) return -1
    if (!a.isDefault && b.isDefault) return 1
    return a.nome.localeCompare(b.nome)
  })
})

function getTipoLabel(tipo: TipoDocumento): string {
  return tiposDocumento.find(t => t.value === tipo)?.label || tipo
}

function podeCriarTemplate() {
  return authStore.hasPermission('criar_docs') || authStore.hasPermission('editar_docs')
}

function novoTemplate() {
  form.value = {
    nome: '',
    tipo: 'generico',
    descricao: '',
    conteudo: '<div style="font-family: Arial, sans-serif; line-height: 1.6;"><p>[CONTEÚDO]</p></div>',
    isDefault: false,
  }
  templateSelecionado.value = null
  modoEdicao.value = 'criar'
}

function editarTemplate(template: Template) {
  form.value = {
    nome: template.nome,
    tipo: template.tipo,
    descricao: template.descricao || '',
    conteudo: template.conteudo,
    isDefault: template.isDefault,
  }
  templateSelecionado.value = template
  modoEdicao.value = 'editar'
}

function visualizarTemplate(template: Template) {
  templateSelecionado.value = template
  modoEdicao.value = 'visualizar'
}

async function duplicarTemplate(template: Template) {
  const confirmed = await showConfirm(`Deseja criar uma cópia de "${template.nome}"?`)
  if (!confirmed) return

  try {
    await templatesStore.createTemplate({
      nome: `${template.nome} (Cópia)`,
      tipo: template.tipo,
      descricao: template.descricao,
      conteudo: template.conteudo,
      isDefault: false
    })
    showSuccess('Template duplicado com sucesso!')
  } catch (error) {
    showError('Erro ao duplicar template')
  }
}

async function salvarTemplate() {
  if (!form.value.nome.trim()) {
    showError('Por favor, preencha o nome do template')
    return
  }

  const conteudoTexto = form.value.conteudo.replace(/<[^>]+>/g, '').trim()
  if (!conteudoTexto) {
    showError('Por favor, preencha o conteúdo do template')
    return
  }

  try {
    if (modoEdicao.value === 'criar') {
      await templatesStore.createTemplate({
        nome: form.value.nome,
        tipo: form.value.tipo,
        descricao: form.value.descricao,
        conteudo: form.value.conteudo,
        isDefault: form.value.isDefault,
      })
      showSuccess('Template criado com sucesso!')
    } else if (modoEdicao.value === 'editar' && templateSelecionado.value) {
      await templatesStore.updateTemplate(templateSelecionado.value.id, {
        nome: form.value.nome,
        tipo: form.value.tipo,
        descricao: form.value.descricao,
        conteudo: form.value.conteudo,
        isDefault: form.value.isDefault,
      })
      showSuccess('Template atualizado com sucesso!')
    }
    fecharModal()
  } catch (error: any) {
    showError(error.message || 'Erro ao salvar template')
  }
}

async function excluirTemplate(template: Template) {
  const mensagem = template.isDefault
    ? `«${template.nome}» é o template padrão deste tipo. Só será excluído se existir outro template para substituí-lo. Continuar?`
    : `Tem certeza que deseja excluir o template "${template.nome}"?`

  const confirmed = await showConfirm(mensagem)
  if (!confirmed) return

  try {
    await templatesStore.deleteTemplate(template.id)
    showSuccess('Template excluído com sucesso!')
  } catch (error: any) {
    showError(error.message || 'Erro ao excluir template')
  }
}

function fecharModal() {
  modoEdicao.value = null
  templateSelecionado.value = null
  form.value = {
    nome: '',
    tipo: 'generico',
    descricao: '',
    conteudo: '',
    isDefault: false,
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Botão Voltar -->
    <button
      @click="router.push('/documentos')"
      class="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 transition-colors"
    >
      <ArrowLeft class="w-5 h-5" />
      Voltar para Documentos
    </button>

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-100">
          Gestão de Templates
        </h1>
        <p class="text-gray-600 dark:text-gray-400 mt-1">
          Crie e gerencie templates personalizados para seus documentos
        </p>
      </div>

      <button
        v-if="podeCriarTemplate()"
        @click="novoTemplate"
        class="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors"
      >
        <Plus class="w-5 h-5" />
        Novo Template
      </button>
    </div>

    <!-- Filtros -->
    <div class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
      <div class="flex items-center gap-4">
        <!-- Busca -->
        <div class="flex-1 relative">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            v-model="busca"
            type="text"
            placeholder="Buscar templates..."
            class="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400"
          />
        </div>

        <!-- Filtro de Tipo -->
        <div class="flex items-center gap-2">
          <Filter class="w-5 h-5 text-gray-400" />
          <select
            v-model="filtroTipo"
            class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400"
          >
            <option value="todos">Todos os Tipos</option>
            <option v-for="tipo in tiposDocumento" :key="tipo.value" :value="tipo.value">
              {{ tipo.label }}
            </option>
          </select>
        </div>

        <div class="text-sm text-gray-600 dark:text-gray-400">
          {{ templatesFiltrados.length }} template(s)
        </div>
      </div>
    </div>

    <!-- Lista de Templates -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="template in templatesFiltrados"
        :key="template.id"
        class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 hover:shadow-lg transition-shadow"
      >
        <!-- Header do Card -->
        <div class="flex items-start justify-between mb-3">
          <div class="flex-1 min-w-0">
            <h3 class="font-semibold text-gray-900 dark:text-gray-100 truncate">
              {{ template.nome }}
            </h3>
            <div class="flex items-center gap-2 mt-1">
              <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400">
                {{ getTipoLabel(template.tipo) }}
              </span>
              <span
                v-if="template.isDefault"
                class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400"
              >
                Padrão
              </span>
            </div>
          </div>

          <FileText class="w-10 h-10 text-gray-300 dark:text-gray-600 flex-shrink-0 ml-2" />
        </div>

        <!-- Descrição -->
        <p v-if="template.descricao" class="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
          {{ template.descricao }}
        </p>

        <!-- Metadata -->
        <div class="text-xs text-gray-500 dark:text-gray-500 mb-3">
          Criado em {{ new Date(template.createdAt).toLocaleDateString('pt-BR') }}
        </div>

        <!-- Ações -->
        <div class="flex items-center gap-2">
          <button
            @click="visualizarTemplate(template)"
            class="flex-1 flex items-center justify-center gap-1 px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded transition-colors"
          >
            <Eye class="w-4 h-4" />
            Ver
          </button>

          <button
            v-if="podeCriarTemplate()"
            @click="duplicarTemplate(template)"
            class="flex-1 flex items-center justify-center gap-1 px-3 py-1.5 text-sm bg-blue-100 hover:bg-blue-200 dark:bg-blue-900/30 dark:hover:bg-blue-900/50 text-blue-700 dark:text-blue-400 rounded transition-colors"
            title="Duplicar template"
          >
            <Copy class="w-4 h-4" />
            Duplicar
          </button>

          <button
            v-if="authStore.hasPermission('editar_docs')"
            @click="editarTemplate(template)"
            class="flex-1 flex items-center justify-center gap-1 px-3 py-1.5 text-sm bg-amber-100 hover:bg-amber-200 dark:bg-amber-900/30 dark:hover:bg-amber-900/50 text-amber-700 dark:text-amber-400 rounded transition-colors"
          >
            <Edit class="w-4 h-4" />
            Editar
          </button>

          <button
            v-if="authStore.hasPermission('excluir_docs')"
            @click="excluirTemplate(template)"
            class="p-1.5 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
            title="Excluir"
          >
            <Trash2 class="w-4 h-4" />
          </button>
        </div>
      </div>

      <!-- Estado Vazio -->
      <div v-if="templatesFiltrados.length === 0" class="col-span-full text-center py-12">
        <FileText class="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
        <p class="text-gray-500 dark:text-gray-400">
          {{ busca || filtroTipo !== 'todos' ? 'Nenhum template encontrado' : 'Nenhum template cadastrado' }}
        </p>
      </div>
    </div>

    <!-- Modal de Criar/Editar/Visualizar -->
    <Transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="modoEdicao"
        class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4 overflow-y-auto"
        @click.self="fecharModal"
      >
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-5xl w-full my-8">
          <!-- Header -->
          <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
              {{ modoEdicao === 'criar' ? 'Novo Template' : modoEdicao === 'editar' ? 'Editar Template' : 'Visualizar Template' }}
            </h3>
            <button
              @click="fecharModal"
              class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded transition-colors"
            >
              <X class="w-5 h-5" />
            </button>
          </div>

          <!-- Conteúdo -->
          <div class="p-6 space-y-4">
            <div v-if="modoEdicao !== 'visualizar'" class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <!-- Nome -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Nome do Template *
                </label>
                <input
                  v-model="form.nome"
                  type="text"
                  placeholder="Ex: Ofício Convite"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400"
                />
              </div>

              <!-- Tipo -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Tipo de Documento *
                </label>
                <select
                  v-model="form.tipo"
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400"
                >
                  <option v-for="tipo in tiposDocumento" :key="tipo.value" :value="tipo.value">
                    {{ tipo.label }}
                  </option>
                </select>
              </div>

              <!-- Padrão do tipo -->
              <div class="md:col-span-2">
                <label class="flex items-center gap-2 cursor-pointer">
                  <input
                    v-model="form.isDefault"
                    type="checkbox"
                    class="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span class="text-sm text-gray-700 dark:text-gray-300">
                    Definir como template padrão deste tipo de documento
                  </span>
                </label>
              </div>

              <!-- Descrição -->
              <div class="md:col-span-2">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Descrição
                </label>
                <textarea
                  v-model="form.descricao"
                  rows="2"
                  placeholder="Breve descrição do template..."
                  class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400 resize-none"
                />
              </div>

              <!-- Conteúdo -->
              <div class="md:col-span-2">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Conteúdo do template *
                </label>
                <RichTextEditor
                  :key="`${modoEdicao}-${templateSelecionado?.id ?? 'novo'}`"
                  v-model="form.conteudo"
                  min-height="320px"
                  placeholder="Redija o corpo do template como em um editor de texto..."
                />
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">
                  Use o botão <strong>{ }</strong> na barra de ferramentas para inserir variáveis como
                  <code class="text-primary-600 dark:text-primary-400">[ASSUNTO]</code> ou
                  <code class="text-primary-600 dark:text-primary-400">[DATA]</code>. O sistema salva o HTML
                  automaticamente para uso nos documentos.
                </p>
              </div>
            </div>

            <!-- Visualização -->
            <div v-else class="space-y-4">
              <div>
                <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Nome:</span>
                <p class="text-gray-900 dark:text-gray-100 mt-1">{{ templateSelecionado?.nome }}</p>
              </div>

              <div>
                <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Tipo:</span>
                <p class="text-gray-900 dark:text-gray-100 mt-1">{{ getTipoLabel(templateSelecionado?.tipo!) }}</p>
              </div>

              <div v-if="templateSelecionado?.descricao">
                <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Descrição:</span>
                <p class="text-gray-900 dark:text-gray-100 mt-1">{{ templateSelecionado.descricao }}</p>
              </div>

              <div>
                <span class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">Preview:</span>
                <div 
                  class="bg-white dark:bg-gray-50 p-8 rounded border border-gray-200 dark:border-gray-700 max-h-96 overflow-y-auto"
                  v-html="templateSelecionado?.conteudo"
                  style="color: #1f2937;"
                />
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="flex items-center justify-end gap-3 p-4 border-t border-gray-200 dark:border-gray-700">
            <button
              @click="fecharModal"
              class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
              {{ modoEdicao === 'visualizar' ? 'Fechar' : 'Cancelar' }}
            </button>
            <button
              v-if="modoEdicao !== 'visualizar'"
              @click="salvarTemplate"
              :disabled="templatesStore.loading"
              class="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
            >
              <Save class="w-4 h-4" />
              {{ modoEdicao === 'criar' ? 'Criar Template' : 'Salvar Alterações' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
