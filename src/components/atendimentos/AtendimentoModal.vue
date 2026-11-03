<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useAtendimentosStore } from '@/stores/atendimentos'
import { useCrmStore } from '@/stores/crm'
import { useAuthStore } from '@/stores/auth'
import { PERMS } from '@/constants/rbac'
import type { Atendimento, Tag } from '@/types'
import Modal from '@/components/common/Modal.vue'
import Button from '@/components/common/Button.vue'
import TagAtendimentoCreatorInline from '@/components/atendimentos/TagAtendimentoCreatorInline.vue'
import CidadaoModal from '@/components/crm/CidadaoModal.vue'
import { Search, Upload, X, FileText, Image as ImageIcon, UserPlus } from 'lucide-vue-next'

interface Props {
  modelValue: boolean
  /** Quando informado, o modal edita o protocolo (somente válido com status aberto). */
  atendimento?: Atendimento | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: [atendimento?: Atendimento]
}>()

const isEdicao = computed(() => Boolean(props.atendimento?.id))
const tituloModal = computed(() => (isEdicao.value ? 'Editar Atendimento' : 'Novo Atendimento'))

const atendimentosStore = useAtendimentosStore()
const crmStore = useCrmStore()
const authStore = useAuthStore()

// Form data
const form = ref({
  cidadaoId: '',
  perfil_ativo_id: '',
  macrotemasId: '',
  assunto: '',
  descricao: '',
  responsavelId: '',
  prioridade: 'media' as 'baixa' | 'media' | 'alta' | 'urgente',
  tags: [] as Tag[],
  anexos: [] as File[]
})

const buscaCidadao = ref('')
const loading = ref(false)
const erro = ref<string | null>(null)
const isDragging = ref(false)
const mostrarCidadaoModal = ref(false)
const cidadaoEditando = ref<any>(null)

// Seleção de perfil para cidadão com múltiplos perfis
const mostrarSeletorPerfil = ref(false)
const cidadaoParaSelecionarPerfil = ref<string>('')
const perfilSelecionado = ref<string>('')

// Cidadãos filtrados para busca
const cidadaosFiltrados = computed(() => {
  if (!buscaCidadao.value) return crmStore.cidadaos.slice(0, 10)
  
  const query = buscaCidadao.value.toLowerCase()
  return crmStore.cidadaos
    .filter(c => 
      c.nome.toLowerCase().includes(query) ||
      c.telefone.includes(query) ||
      c.cpf?.includes(query)
    )
    .slice(0, 10)
})

// Cidadão selecionado
const cidadaoSelecionado = computed(() => {
  return crmStore.cidadaos.find(c => c.id === form.value.cidadaoId)
})

const podeEscolherResponsavel = computed(() => authStore.hasPermission(PERMS.atendReassign))

const responsaveisDisponiveis = computed(() => {
  if (podeEscolherResponsavel.value) {
    return atendimentosStore.responsaveisElegiveis
  }
  return authStore.usuario ? [authStore.usuario] : []
})

// Resetar formulário
const resetForm = () => {
  form.value = {
    cidadaoId: '',
    perfil_ativo_id: '',
    macrotemasId: '',
    assunto: '',
    descricao: '',
    responsavelId: authStore.usuario?.id || '',
    prioridade: 'media',
    tags: [],
    anexos: []
  }
  buscaCidadao.value = ''
  erro.value = null
}

// Selecionar cidadão
const selecionarCidadao = (id: string) => {
  const cidadao = crmStore.cidadaos.find(c => c.id === id)
  if (!cidadao) return
  
  // Verificar se tem múltiplos perfis
  if (cidadao.perfis_profissionais && cidadao.perfis_profissionais.length > 1) {
    // Mostrar seletor de perfil
    cidadaoParaSelecionarPerfil.value = id
    perfilSelecionado.value = ''
    mostrarSeletorPerfil.value = true
  } else {
    // Selecionar diretamente
    form.value.cidadaoId = id
    form.value.perfil_ativo_id = cidadao.perfis_profissionais && cidadao.perfis_profissionais.length > 0
      ? cidadao.perfis_profissionais[0].id
      : ''
    buscaCidadao.value = ''
  }
}

// Confirmar seleção de perfil
const confirmarSelecaoPerfil = () => {
  if (!cidadaoParaSelecionarPerfil.value || !perfilSelecionado.value) {
    erro.value = 'Selecione um perfil para continuar'
    return
  }
  
  form.value.cidadaoId = cidadaoParaSelecionarPerfil.value
  form.value.perfil_ativo_id = perfilSelecionado.value
  
  // Reset
  mostrarSeletorPerfil.value = false
  cidadaoParaSelecionarPerfil.value = ''
  perfilSelecionado.value = ''
  buscaCidadao.value = ''
}

// Cancelar seleção de perfil
const cancelarSelecaoPerfil = () => {
  mostrarSeletorPerfil.value = false
  cidadaoParaSelecionarPerfil.value = ''
  perfilSelecionado.value = ''
}

// Remover cidadão
const removerCidadao = () => {
  form.value.cidadaoId = ''
  form.value.perfil_ativo_id = ''
}

// Abrir modal para criar novo cidadão
const abrirModalNovoCidadao = () => {
  cidadaoEditando.value = null
  mostrarCidadaoModal.value = true
}

// Abrir modal para editar cidadão existente
const editarCidadao = () => {
  cidadaoEditando.value = cidadaoSelecionado.value
  mostrarCidadaoModal.value = true
}

// Callback após criar/editar cidadão
const handleCidadaoCriado = () => {
  if (!cidadaoEditando.value) {
    // Criação: seleciona o último cidadão (recém-criado) verificando perfis
    const ultimoCidadao = crmStore.cidadaos[0] // Novo cidadão está no início (unshift)
    if (ultimoCidadao) {
      selecionarCidadao(ultimoCidadao.id)
    }
  }
  // Se for edição, mantém o cidadão já selecionado
  cidadaoEditando.value = null
  mostrarCidadaoModal.value = false
}

// Gerenciar Tags
const toggleTag = (tag: Tag) => {
  const index = form.value.tags.findIndex(t => t.id === tag.id)
  if (index > -1) {
    form.value.tags.splice(index, 1)
  } else {
    form.value.tags.push(tag)
  }
}

const isTagSelected = (tag: Tag) => {
  return form.value.tags.some(t => t.id === tag.id)
}

const handleTagCriada = (tagId: string) => {
  const tag = atendimentosStore.tagsAtendimentoDisponiveis.find(t => t.id === tagId)
  if (tag && !form.value.tags.some(t => t.id === tagId)) {
    form.value.tags.push(tag)
  }
}

// Gerenciar Anexos
const handleDragEnter = (e: DragEvent) => {
  e.preventDefault()
  isDragging.value = true
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
  const files = Array.from(e.dataTransfer?.files || [])
  files.forEach(file => adicionarAnexo(file))
}

const handleFileInput = (e: Event) => {
  const target = e.target as HTMLInputElement
  const files = Array.from(target.files || [])
  files.forEach(file => adicionarAnexo(file))
  target.value = ''
}

const adicionarAnexo = (file: File) => {
  if (file.size > 10 * 1024 * 1024) {
    erro.value = 'Arquivo muito grande. Máximo 10MB'
    return
  }
  
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    erro.value = 'Tipo de arquivo não permitido. Use imagens ou PDFs'
    return
  }
  
  form.value.anexos.push(file)
}

const removerAnexo = (index: number) => {
  form.value.anexos.splice(index, 1)
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

// Validação
const validar = (): boolean => {
  if (!form.value.cidadaoId) {
    erro.value = 'Selecione um cidadão'
    return false
  }
  if (!form.value.macrotemasId) {
    erro.value = 'Selecione um macrotema'
    return false
  }
  if (!form.value.assunto.trim()) {
    erro.value = 'Informe o assunto'
    return false
  }
  if (!form.value.descricao.trim()) {
    erro.value = 'Informe a descrição'
    return false
  }
  erro.value = null
  return true
}

const preencherFormularioEdicao = (a: Atendimento) => {
  form.value = {
    cidadaoId: a.cidadaoId,
    perfil_ativo_id: a.perfil_ativo_id || '',
    macrotemasId: a.macrotema.id,
    assunto: a.assunto,
    descricao: a.descricao,
    responsavelId: a.responsavelId,
    prioridade: a.prioridade,
    tags: a.tags ?? [],
    anexos: [],
  }
  if (!crmStore.cidadaos.some(c => c.id === a.cidadaoId)) {
    crmStore.cidadaos.push({
      ...a.cidadao,
      createdAt: a.cidadao.createdAt || a.createdAt,
      updatedAt: a.cidadao.updatedAt || a.updatedAt,
    })
  }
}

const salvar = async () => {
  if (!validar()) return

  loading.value = true
  erro.value = null

  try {
    const macrotema = atendimentosStore.macrotemasDisponiveis.find(m => m.id === form.value.macrotemasId)!
    const dados = {
      cidadaoId: form.value.cidadaoId,
      perfil_ativo_id: form.value.perfil_ativo_id || undefined,
      assunto: form.value.assunto,
      descricao: form.value.descricao,
      macrotema,
      tags: form.value.tags,
      responsavelId:
        form.value.responsavelId
        || (isEdicao.value ? props.atendimento!.responsavelId : authStore.usuario!.id),
      prioridade: form.value.prioridade,
    }

    if (isEdicao.value && props.atendimento) {
      const atualizado = await atendimentosStore.updateAtendimento(
        props.atendimento.id,
        dados,
        form.value.anexos,
      )
      if (!atualizado) {
        erro.value = 'Erro ao salvar alterações. Verifique se o status ainda é Aberto.'
        return
      }
      emit('success', atualizado)
    } else {
      await atendimentosStore.createAtendimento(dados, form.value.anexos)
      emit('success')
    }

    fechar()
  } catch {
    erro.value = isEdicao.value
      ? 'Erro ao salvar alterações. Tente novamente.'
      : 'Erro ao criar atendimento. Tente novamente.'
  } finally {
    loading.value = false
  }
}

const fechar = () => {
  emit('update:modelValue', false)
  resetForm()
}

watch(
  () => props.modelValue,
  async (aberto) => {
    if (!aberto) return
    await Promise.all([
      atendimentosStore.fetchMacrotemas(),
      atendimentosStore.fetchTagsAtendimento(),
      atendimentosStore.fetchResponsaveisElegiveis().catch(() => []),
    ])
    if (crmStore.cidadaos.length === 0) {
      await crmStore.fetchCidadaos(1, 50)
    }
    if (props.atendimento) {
      preencherFormularioEdicao(props.atendimento)
    } else {
      resetForm()
    }
  },
)
</script>

<template>
  <Modal
    :model-value="modelValue"
    @update:model-value="fechar"
    :titulo="tituloModal"
    largura="2xl"
  >
    <!-- Alerta de Erro -->
    <div
      v-if="erro"
      class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-800"
    >
      {{ erro }}
    </div>

    <!-- Formulário -->
    <form @submit.prevent="salvar" class="space-y-6">
      <!-- Busca de Cidadão -->
      <div>
        <label class="label">Cidadão *</label>
        
        <!-- Cidadão Selecionado -->
        <div v-if="cidadaoSelecionado" class="mb-2">
          <div class="flex items-center justify-between p-3 bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800 rounded-lg">
            <div>
              <p class="font-medium text-gray-900 dark:text-gray-100">{{ cidadaoSelecionado.nome }}</p>
              <p class="text-sm text-gray-600 dark:text-gray-400">{{ cidadaoSelecionado.telefone }}</p>
            </div>
            <div class="flex items-center gap-2">
              <button
                @click="editarCidadao"
                type="button"
                class="text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium"
              >
                Editar
              </button>
              <button
                @click="removerCidadao"
                type="button"
                class="text-sm text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300"
              >
                Remover
              </button>
            </div>
          </div>
        </div>

        <!-- Campo de Busca -->
        <div v-else>
          <div class="flex gap-2 mb-2">
            <div class="relative flex-1">
              <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
              <input
                v-model="buscaCidadao"
                type="text"
                class="input pl-10"
                placeholder="Buscar por nome, telefone ou CPF..."
              />
            </div>
            <button
              @click="abrirModalNovoCidadao"
              type="button"
              class="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors whitespace-nowrap"
            >
              <UserPlus class="w-5 h-5" />
              Novo Cidadão
            </button>
          </div>

          <!-- Lista de Resultados -->
          <div v-if="buscaCidadao && cidadaosFiltrados.length > 0" class="mt-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg divide-y divide-gray-200 dark:divide-gray-700 max-h-48 overflow-y-auto">
            <button
              v-for="cidadao in cidadaosFiltrados"
              :key="cidadao.id"
              @click="selecionarCidadao(cidadao.id)"
              type="button"
              class="w-full text-left p-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              <p class="font-medium text-gray-900 dark:text-gray-100">{{ cidadao.nome }}</p>
              <p class="text-sm text-gray-600 dark:text-gray-400">{{ cidadao.telefone }}</p>
            </button>
          </div>

          <!-- Sem Resultados -->
          <div v-else-if="buscaCidadao" class="mt-2 p-3 text-sm text-gray-500 dark:text-gray-400 text-center bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg">
            Nenhum cidadão encontrado
          </div>
        </div>
      </div>

      <!-- Macrotema -->
      <div>
        <label class="label">Macrotema *</label>
        <select v-model="form.macrotemasId" class="input" required>
          <option value="">Selecione um macrotema</option>
          <option
            v-for="macrotema in atendimentosStore.macrotemasDisponiveis"
            :key="macrotema.id"
            :value="macrotema.id"
          >
            {{ macrotema.nome }}
          </option>
        </select>
      </div>

      <!-- Assunto -->
      <div>
        <label class="label">Assunto *</label>
        <input
          v-model="form.assunto"
          type="text"
          class="input"
          placeholder="Ex: Solicitação de consulta médica"
          required
        />
      </div>

      <!-- Descrição -->
      <div>
        <label class="label">Descrição *</label>
        <textarea
          v-model="form.descricao"
          rows="4"
          class="input"
          placeholder="Descreva detalhadamente o atendimento solicitado..."
          required
        ></textarea>
      </div>

      <!-- Grid: Responsável + Prioridade -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Responsável -->
        <div v-if="podeEscolherResponsavel">
          <label class="label">Responsável</label>
          <select v-model="form.responsavelId" class="input" required>
            <option
              v-for="responsavel in responsaveisDisponiveis"
              :key="responsavel.id"
              :value="responsavel.id"
            >
              {{ responsavel.nome }} — {{ responsavel.cargo }}
            </option>
          </select>
        </div>
        <div v-else class="text-sm text-gray-600 dark:text-slate-400">
          <span class="label block mb-1">Responsável</span>
          {{ authStore.usuario?.nome }} (você)
        </div>

        <!-- Prioridade -->
        <div>
          <label class="label">Prioridade</label>
          <select v-model="form.prioridade" class="input">
            <option value="baixa">Baixa</option>
            <option value="media">Média</option>
            <option value="alta">Alta</option>
            <option value="urgente">Urgente</option>
          </select>
        </div>
      </div>

      <!-- Tags de Serviço/Assunto -->
      <div>
        <label class="label">Tags de Serviço (opcional)</label>
        <p class="text-xs text-gray-500 dark:text-gray-400 mb-3">
          Especifique o tipo de serviço ou assunto do atendimento
        </p>
        <div class="space-y-3">
          <!-- Tags Existentes -->
          <div class="flex flex-wrap gap-2">
            <button
              v-for="tag in atendimentosStore.tagsAtendimentoDisponiveis"
              :key="tag.id"
              @click.prevent="toggleTag(tag)"
              type="button"
              :style="{ 
                backgroundColor: isTagSelected(tag) ? tag.cor : tag.cor + '20',
                color: isTagSelected(tag) ? '#fff' : tag.cor,
                borderColor: tag.cor
              }"
              class="px-3 py-1.5 rounded-full text-sm font-medium border-2 transition-colors hover:opacity-80"
            >
              {{ tag.nome }}
            </button>
          </div>

          <!-- Criador Inline -->
          <TagAtendimentoCreatorInline @created="handleTagCriada" />
        </div>
      </div>

      <!-- Anexos -->
      <div>
        <label class="label">Anexos (opcional)</label>
        <p class="text-xs text-gray-500 dark:text-gray-400 mb-3">
          Adicione fotos ou documentos relacionados (ex: foto do buraco na rua)
        </p>
        
        <!-- Área de Drop -->
        <div
          @dragenter="handleDragEnter"
          @dragleave="handleDragLeave"
          @dragover="handleDragOver"
          @drop="handleDrop"
          :class="[
            isDragging
              ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
              : 'border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800',
            'relative border-2 border-dashed rounded-lg p-6 transition-colors'
          ]"
        >
          <div class="text-center">
            <Upload 
              :class="[
                isDragging ? 'text-primary-600 dark:text-primary-400' : 'text-gray-400',
                'mx-auto w-10 h-10 mb-3'
              ]"
            />
            <p class="text-sm font-medium text-gray-900 dark:text-gray-100 mb-1">
              {{ isDragging ? 'Solte os arquivos aqui' : 'Arraste arquivos ou clique para selecionar' }}
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400 mb-3">
              Imagens (JPG, PNG) ou PDF até 10MB
            </p>
            <label class="btn btn-secondary cursor-pointer inline-flex items-center gap-2">
              <Upload class="w-4 h-4" />
              Selecionar Arquivos
              <input
                type="file"
                multiple
                accept="image/*,.pdf"
                @change="handleFileInput"
                class="hidden"
              />
            </label>
          </div>
        </div>

        <!-- Lista de Anexos -->
        <div v-if="form.anexos.length > 0" class="mt-3 space-y-2">
          <div
            v-for="(anexo, index) in form.anexos"
            :key="index"
            class="flex items-center gap-3 p-2 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded"
          >
            <component :is="getIconeAnexo(anexo)" class="w-5 h-5 text-gray-600 dark:text-gray-400 flex-shrink-0" />
            <span class="text-sm text-gray-700 dark:text-gray-300 flex-1 truncate">{{ anexo.name }}</span>
            <span class="text-xs text-gray-500 dark:text-gray-400 flex-shrink-0">{{ formatarTamanho(anexo.size) }}</span>
            <button
              @click="removerAnexo(index)"
              type="button"
              class="text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 flex-shrink-0"
            >
              <X class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </form>

    <!-- Footer -->
    <template #footer>
      <Button
        variant="secondary"
        @click="fechar"
        :disabled="loading"
      >
        Cancelar
      </Button>
      <Button
        variant="primary"
        @click="salvar"
        :loading="loading"
      >
        {{
          loading
            ? (isEdicao ? 'Salvando...' : 'Criando...')
            : (isEdicao ? 'Salvar alterações' : 'Criar Ticket')
        }}
      </Button>
    </template>
  </Modal>

  <!-- Modal de Seleção de Perfil -->
  <Transition
    enter-active-class="transition-opacity duration-200"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition-opacity duration-200"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div v-if="mostrarSeletorPerfil" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[100] p-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
          Selecione o Perfil Atuante
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
          {{ cidadaoParaSelecionarPerfil ? crmStore.cidadaos.find(c => c.id === cidadaoParaSelecionarPerfil)?.nome : '' }} possui múltiplos perfis. Selecione qual perfil está sendo usado neste atendimento:
        </p>

        <div class="space-y-2 mb-6">
          <label
            v-for="perfil in cidadaoParaSelecionarPerfil ? crmStore.cidadaos.find(c => c.id === cidadaoParaSelecionarPerfil)?.perfis_profissionais : []"
            :key="perfil.id"
            class="flex items-start gap-3 p-3 border-2 rounded-lg cursor-pointer transition-colors"
            :class="[
              perfilSelecionado === perfil.id
                ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
            ]"
          >
            <input
              type="radio"
              :value="perfil.id"
              v-model="perfilSelecionado"
              class="mt-1"
            />
            <div class="flex-1">
              <p class="font-medium text-gray-900 dark:text-gray-100">
                {{ perfil.cargo }}
              </p>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                em {{ perfil.instituicao }}
              </p>
              <span
                v-if="perfil.tag_id"
                :style="{
                  backgroundColor: crmStore.tagsDisponiveis.find(t => t.id === perfil.tag_id)?.cor + '20' || '#e5e7eb',
                  color: crmStore.tagsDisponiveis.find(t => t.id === perfil.tag_id)?.cor || '#6b7280'
                }"
                class="inline-block mt-1 px-2 py-0.5 rounded text-xs font-medium"
              >
                {{ crmStore.tagsDisponiveis.find(t => t.id === perfil.tag_id)?.nome || 'Sem Tag' }}
              </span>
            </div>
          </label>
        </div>

        <div class="flex justify-end gap-3">
          <button
            @click="cancelarSelecaoPerfil"
            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            Cancelar
          </button>
          <button
            @click="confirmarSelecaoPerfil"
            :disabled="!perfilSelecionado"
            class="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:bg-gray-300 dark:disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg transition-colors"
          >
            Confirmar
          </button>
        </div>
      </div>
    </div>
  </Transition>

  <!-- Modal de Criação/Edição de Cidadão (Cross-Module) -->
  <CidadaoModal
    v-model="mostrarCidadaoModal"
    :cidadao="cidadaoEditando"
    @success="handleCidadaoCriado"
  />
</template>
