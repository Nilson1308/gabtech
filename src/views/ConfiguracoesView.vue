<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { PERMS } from '@/constants/rbac'
import { useCrmStore } from '@/stores/crm'
import { useAtendimentosStore } from '@/stores/atendimentos'
import type { Tag, ModuloTag, TipoTag } from '@/types'
import Button from '@/components/common/Button.vue'
import Modal from '@/components/common/Modal.vue'
import GovernancaView from './configuracoes/GovernancaView.vue'
import ConfiguracoesDocumentosView from './documentos/ConfiguracoesDocumentosView.vue'
import EspacosView from './agenda/EspacosView.vue'
import TiposEventoView from './agenda/TiposEventoView.vue'
import IntegracoesView from './agenda/IntegracoesView.vue'
import ComunicacaoView from './configuracoes/ComunicacaoView.vue'
import MacrotemasView from './configuracoes/MacrotemasView.vue'
import SlaAtendimentosView from './configuracoes/SlaAtendimentosView.vue'
import UsuariosView from './configuracoes/UsuariosView.vue'
import { 
  Tags as TagsIcon, 
  Shield, 
  FileText, 
  Calendar, 
  Plug, 
  Plus, 
  Edit, 
  Trash2, 
  AlertCircle, 
  Users, 
  Inbox,
  FolderTree,
  MessageSquare,
  UserCog,
  Clock,
} from 'lucide-vue-next'

const authStore = useAuthStore()
const crmStore = useCrmStore()
const atendimentosStore = useAtendimentosStore()

// Seções disponíveis
type SecaoConfig = 'classificacoes' | 'macrotemas' | 'sla-atendimentos' | 'documentos' | 'agenda-cerimonial' | 'integracoes' | 'comunicacao' | 'usuarios' | 'governanca'

const secaoAtiva = ref<SecaoConfig>('classificacoes')

// Sub-aba de Agenda & Cerimonial
const abaAgenda = ref<'espacos' | 'tipos'>('espacos')

// Seções do menu
const secoes = computed(() => [
  {
    id: 'classificacoes' as SecaoConfig,
    nome: 'Classificações',
    descricao: 'Tags & Etiquetas',
    icone: TagsIcon,
    cor: '#10b981',
    disponivel: authStore.hasPermission(PERMS.manageTags),
  },
  {
    id: 'macrotemas' as SecaoConfig,
    nome: 'Macrotemas',
    descricao: 'Categorias de Atendimento',
    icone: FolderTree,
    cor: '#06b6d4',
    disponivel: authStore.hasPermission(PERMS.manageMacrotemas),
  },
  {
    id: 'sla-atendimentos' as SecaoConfig,
    nome: 'SLA de Atendimentos',
    descricao: 'Prazos por prioridade',
    icone: Clock,
    cor: '#0ea5e9',
    disponivel: authStore.hasPermission(PERMS.manageSlaAtend),
  },
  {
    id: 'documentos' as SecaoConfig,
    nome: 'Documentos',
    descricao: 'Pastas & Tipos',
    icone: FileText,
    cor: '#f97316',
    disponivel: authStore.hasPermission(PERMS.manageDocsConfig),
  },
  {
    id: 'agenda-cerimonial' as SecaoConfig,
    nome: 'Agenda & Cerimonial',
    descricao: 'Espaços & Tipos de Evento',
    icone: Calendar,
    cor: '#8b5cf6',
    disponivel: authStore.hasPermission(PERMS.manageAgendaCerimonial),
  },
  {
    id: 'integracoes' as SecaoConfig,
    nome: 'Integrações',
    descricao: 'Calendário (Google/Outlook)',
    icone: Plug,
    cor: '#3b82f6',
    disponivel: authStore.hasPermission(PERMS.manageIntegrations),
  },
  {
    id: 'comunicacao' as SecaoConfig,
    nome: 'Comunicação',
    descricao: 'Email, WhatsApp & SMS',
    icone: MessageSquare,
    cor: '#10b981',
    disponivel: authStore.hasPermission(PERMS.manageComunicacao),
  },
  {
    id: 'usuarios' as SecaoConfig,
    nome: 'Usuários e Equipe',
    descricao: 'Gestão de Acessos',
    icone: UserCog,
    cor: '#f59e0b',
    disponivel: authStore.hasPermission(PERMS.manageUsers),
  },
  {
    id: 'governanca' as SecaoConfig,
    nome: 'Governança e Perfis',
    descricao: 'Matriz RBAC',
    icone: Shield,
    cor: '#dc2626',
    disponivel: authStore.hasPermission(PERMS.manageProfiles),
  },
])

const secoesVisiveis = computed(() => secoes.value.filter(s => s.disponivel))

watch(
  secoesVisiveis,
  (lista) => {
    if (lista.length === 0) return
    if (!lista.some(s => s.id === secaoAtiva.value)) {
      secaoAtiva.value = lista[0].id
    }
  },
  { immediate: true },
)

watch(
  secaoAtiva,
  secao => {
    if (secao === 'classificacoes') {
      void crmStore.fetchTags()
    }
  },
  { immediate: true },
)

// ============= GESTÃO DE TAGS (Classificações) =============
const mostrarModal = ref(false)
const tagEditando = ref<Tag | null>(null)
const confirmandoExclusao = ref<string | null>(null)
const mostrarAvisoUso = ref(false)
const quantidadeUso = ref(0)

const tiposTag: { value: TipoTag; label: string; descricao: string }[] = [
  {
    value: 'segmentacao',
    label: 'Segmentação',
    descricao: 'Marcadores do cidadão (Idoso, PCD, liderança…)',
  },
  {
    value: 'contexto',
    label: 'Contexto institucional',
    descricao: 'Classificação de perfis (órgão + cargo)',
  },
  {
    value: 'contexto_profissional',
    label: 'Contexto profissional',
    descricao: 'Currículos, vagas (Talentos) e turmas de capacitação',
  },
  {
    value: 'ambos',
    label: 'Ambos (segmentação + contexto institucional)',
    descricao: 'Marcadores do cidadão e perfis profissionais no CRM',
  },
]

const labelTipoTag = (tipo: TipoTag) =>
  tiposTag.find(t => t.value === tipo)?.label ?? tipo

const form = ref({
  nome: '',
  cor: '#3b82f6',
  modulos: ['crm'] as ModuloTag[],
  tipo: 'segmentacao' as TipoTag,
})

const cores = [
  { nome: 'Azul', valor: '#3b82f6' },
  { nome: 'Verde', valor: '#10b981' },
  { nome: 'Amarelo', valor: '#f59e0b' },
  { nome: 'Vermelho', valor: '#ef4444' },
  { nome: 'Roxo', valor: '#8b5cf6' },
  { nome: 'Rosa', valor: '#ec4899' },
  { nome: 'Cinza', valor: '#6b7280' },
  { nome: 'Indigo', valor: '#6366f1' },
]

const abrirNova = () => {
  tagEditando.value = null
  form.value = {
    nome: '',
    cor: '#3b82f6',
    modulos: ['crm'],
    tipo: 'segmentacao',
  }
  mostrarModal.value = true
}

const abrirEdicao = (tag: Tag) => {
  tagEditando.value = tag
  form.value = {
    nome: tag.nome,
    cor: tag.cor,
    modulos: tag.modulos || ['crm'],
    tipo: tag.tipo ?? 'ambos',
  }
  mostrarModal.value = true
}

const toggleModulo = (modulo: ModuloTag) => {
  const index = form.value.modulos.indexOf(modulo)
  if (index > -1) {
    if (form.value.modulos.length > 1) {
      form.value.modulos.splice(index, 1)
    }
  } else {
    form.value.modulos.push(modulo)
  }
}

const salvar = () => {
  if (!form.value.nome.trim()) {
    return
  }

  if (tagEditando.value) {
    crmStore.updateTag(tagEditando.value.id, form.value)
  } else {
    crmStore.createTag(form.value)
  }

  fecharModal()
}

const fecharModal = () => {
  mostrarModal.value = false
  tagEditando.value = null
  form.value = {
    nome: '',
    cor: '#3b82f6',
    modulos: ['crm'],
    tipo: 'segmentacao',
  }
}

const handleExcluir = (tag: Tag) => {
  const emMarcadores = crmStore.cidadaos.filter(c => c.tag_ids?.includes(tag.id)).length
  const emPerfis = crmStore.cidadaos.filter(c =>
    c.perfis_profissionais?.some(p => p.tag_id === tag.id),
  ).length
  const emUsoCRM = emMarcadores + emPerfis
  
  // Verificar tags em atendimentos
  const emUsoAtendimentos = atendimentosStore.atendimentos.filter(a => 
    a.tags.some((t: any) => t.id === tag.id)
  ).length
  
  const totalEmUso = emUsoCRM + emUsoAtendimentos
  
  if (totalEmUso > 0) {
    quantidadeUso.value = totalEmUso
    mostrarAvisoUso.value = true
    return
  }

  if (confirmandoExclusao.value !== tag.id) {
    confirmandoExclusao.value = tag.id
    setTimeout(() => {
      confirmandoExclusao.value = null
    }, 3000)
    return
  }

  crmStore.deleteTag(tag.id)
  confirmandoExclusao.value = null
}
</script>

<template>
  <div class="flex flex-col lg:flex-row min-h-[calc(100vh-120px)] lg:h-[calc(100vh-120px)] gap-4 lg:gap-6">
    <!-- Mobile: seletor de seção -->
    <div class="lg:hidden card p-3">
      <label class="text-xs font-semibold text-gray-500 dark:text-slate-400 uppercase">Seção</label>
      <select
        v-model="secaoAtiva"
        class="mt-1 w-full input text-sm"
      >
        <option v-for="secao in secoesVisiveis" :key="secao.id" :value="secao.id">
          {{ secao.nome }}
        </option>
      </select>
    </div>

    <!-- Sidebar Vertical de Navegação -->
    <aside class="hidden lg:block w-72 flex-shrink-0">
      <div class="card p-4 sticky top-6 space-y-2">
        <div class="mb-4 pb-4 border-b border-gray-200 dark:border-slate-700">
          <h2 class="text-xl font-bold text-gray-900 dark:text-slate-100">Configurações</h2>
          <p class="text-sm text-gray-600 dark:text-slate-400 mt-1">
            Hub de Configurações do Sistema
          </p>
        </div>

        <nav class="space-y-1">
          <button
            v-for="secao in secoesVisiveis"
            :key="secao.id"
            @click="secaoAtiva = secao.id"
            :class="[
              secaoAtiva === secao.id
                ? 'bg-primary-50 dark:bg-primary-900/30 border-primary-500 dark:border-primary-600 text-primary-700 dark:text-primary-300'
                : 'bg-white dark:bg-slate-800 border-gray-200 dark:border-slate-700 text-gray-700 dark:text-slate-300 hover:bg-gray-50 dark:hover:bg-slate-700/50',
              'w-full flex items-start gap-3 p-3 rounded-lg border-2 transition-all text-left group'
            ]"
          >
            <div
              class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 transition-all"
              :style="{ 
                backgroundColor: secaoAtiva === secao.id ? secao.cor + '20' : 'transparent',
                color: secaoAtiva === secao.id ? secao.cor : 'currentColor'
              }"
            >
              <component :is="secao.icone" class="w-5 h-5" />
            </div>
            <div class="flex-1 min-w-0">
              <div class="font-medium">{{ secao.nome }}</div>
              <div class="text-xs opacity-75 mt-0.5">{{ secao.descricao }}</div>
            </div>
          </button>
        </nav>
      </div>
    </aside>

    <!-- Área de Conteúdo Principal -->
    <main class="flex-1 overflow-y-auto min-w-0 pb-8">
      <div
        v-if="secoesVisiveis.length === 0"
        class="card text-center py-16 text-gray-600 dark:text-slate-400"
      >
        <p class="font-medium text-gray-900 dark:text-slate-100">Nenhuma seção de configuração disponível</p>
        <p class="text-sm mt-2">Seu perfil não possui permissões em Sistema &amp; Configurações.</p>
      </div>

      <!-- Seção: Classificações (Tags) -->
      <div v-if="secaoAtiva === 'classificacoes'" class="space-y-6">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-2xl font-bold text-gray-900 dark:text-slate-100 flex items-center gap-2">
              <TagsIcon class="w-6 h-6 text-green-600 dark:text-green-400" />
              Classificações (Tags & Etiquetas)
            </h3>
            <p class="text-sm text-gray-600 dark:text-slate-400 mt-1">
              {{ crmStore.tagsDisponiveis.length }} {{ crmStore.tagsDisponiveis.length === 1 ? 'tag cadastrada' : 'tags cadastradas' }}
            </p>
          </div>

          <Button variant="primary" @click="abrirNova">
            <Plus class="w-4 h-4" />
            Nova Tag
          </Button>
        </div>

        <!-- Lista de Tags -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            v-for="tag in crmStore.tagsDisponiveis"
            :key="tag.id"
            class="card group hover:shadow-lg transition-all"
          >
            <div class="flex items-center gap-3 mb-3">
              <div
                class="flex-shrink-0 px-3 py-1.5 rounded-full text-sm font-medium"
                :style="{
                  backgroundColor: tag.cor + '20',
                  color: tag.cor,
                  borderColor: tag.cor + '40'
                }"
              >
                {{ tag.nome }}
              </div>

              <div class="flex-1"></div>
              
              <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  @click="abrirEdicao(tag)"
                  class="p-1.5 hover:bg-gray-100 dark:hover:bg-slate-700 rounded text-gray-600 dark:text-slate-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
                  title="Editar"
                >
                  <Edit class="w-4 h-4" />
                </button>
                <button
                  @click="handleExcluir(tag)"
                  :class="[
                    confirmandoExclusao === tag.id
                      ? 'bg-red-500 text-white'
                      : 'hover:bg-red-50 dark:hover:bg-red-900/30 text-red-600 dark:text-red-400',
                    'p-1.5 rounded transition-colors'
                  ]"
                  :title="confirmandoExclusao === tag.id ? 'Confirmar exclusão' : 'Excluir'"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </div>

            <div class="flex items-center gap-2 flex-wrap">
              <span
                class="inline-flex items-center px-2 py-0.5 bg-gray-100 dark:bg-slate-700 text-gray-700 dark:text-slate-300 text-xs font-medium rounded"
              >
                {{ labelTipoTag(tag.tipo ?? 'ambos') }}
              </span>
              <span
                v-if="tag.modulos?.includes('crm')"
                class="inline-flex items-center gap-1 px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs font-medium rounded"
              >
                <Users class="w-3 h-3" />
                CRM
              </span>
              <span
                v-if="tag.modulos?.includes('atendimentos')"
                class="inline-flex items-center gap-1 px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 text-xs font-medium rounded"
              >
                <Inbox class="w-3 h-3" />
                Atendimentos
              </span>
            </div>
          </div>
        </div>

        <div v-if="crmStore.tagsDisponiveis.length === 0" class="card text-center py-12">
          <TagsIcon class="w-16 h-16 text-gray-300 dark:text-slate-600 mx-auto mb-4" />
          <p class="text-gray-500 dark:text-slate-400">Nenhuma tag cadastrada</p>
        </div>
      </div>

      <!-- Seção: Macrotemas -->
      <div v-else-if="secaoAtiva === 'macrotemas'" class="space-y-6">
        <div class="mb-6">
          <h3 class="text-2xl font-bold text-gray-900 dark:text-slate-100 flex items-center gap-2">
            <FolderTree class="w-6 h-6 text-cyan-600 dark:text-cyan-400" />
            Macrotemas
          </h3>
          <p class="text-sm text-gray-600 dark:text-slate-400 mt-1">
            Categorias principais para classificação de atendimentos
          </p>
        </div>
        <MacrotemasView />
      </div>

      <div v-else-if="secaoAtiva === 'sla-atendimentos'" class="space-y-6">
        <div class="mb-6">
          <h3 class="text-2xl font-bold text-gray-900 dark:text-slate-100 flex items-center gap-2">
            <Clock class="w-6 h-6 text-sky-600 dark:text-sky-400" />
            SLA de Atendimentos
          </h3>
          <p class="text-sm text-gray-600 dark:text-slate-400 mt-1">
            Prazos de resposta por nível de prioridade
          </p>
        </div>
        <SlaAtendimentosView />
      </div>

      <!-- Seção: Documentos -->
      <div v-else-if="secaoAtiva === 'documentos'" class="space-y-6">
        <div class="mb-6">
          <h3 class="text-2xl font-bold text-gray-900 dark:text-slate-100 flex items-center gap-2">
            <FileText class="w-6 h-6 text-orange-600 dark:text-orange-400" />
            Documentos (Pastas & Tipos)
          </h3>
          <p class="text-sm text-gray-600 dark:text-slate-400 mt-1">
            Configure pastas e tipos de documentos do sistema
          </p>
        </div>
        <ConfiguracoesDocumentosView />
      </div>

      <!-- Seção: Agenda & Cerimonial -->
      <div v-else-if="secaoAtiva === 'agenda-cerimonial'" class="space-y-6">
        <div class="mb-6">
          <h3 class="text-2xl font-bold text-gray-900 dark:text-slate-100 flex items-center gap-2">
            <Calendar class="w-6 h-6 text-purple-600 dark:text-purple-400" />
            Agenda & Cerimonial
          </h3>
          <p class="text-sm text-gray-600 dark:text-slate-400 mt-1">
            Gerencie espaços físicos e tipos de eventos
          </p>
        </div>

        <!-- Tabs Espaços / Tipos -->
        <div class="border-b border-gray-200 dark:border-slate-700">
          <nav class="flex gap-4">
            <button
              @click="abaAgenda = 'espacos'"
              :class="[
                abaAgenda === 'espacos'
                  ? 'border-primary-600 text-primary-600 dark:border-primary-400 dark:text-primary-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600',
                'px-4 py-3 border-b-2 font-medium transition-colors'
              ]"
            >
              Espaços Físicos
            </button>

            <button
              @click="abaAgenda = 'tipos'"
              :class="[
                abaAgenda === 'tipos'
                  ? 'border-primary-600 text-primary-600 dark:border-primary-400 dark:text-primary-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600',
                'px-4 py-3 border-b-2 font-medium transition-colors'
              ]"
            >
              Tipos de Evento
            </button>
          </nav>
        </div>

        <EspacosView v-if="abaAgenda === 'espacos'" />
        <TiposEventoView v-else />
      </div>

      <!-- Seção: Integrações (Calendário) -->
      <div v-else-if="secaoAtiva === 'integracoes'" class="space-y-6">
        <div class="mb-6">
          <h3 class="text-2xl font-bold text-gray-900 dark:text-slate-100 flex items-center gap-2">
            <Plug class="w-6 h-6 text-blue-600 dark:text-blue-400" />
            Integrações de Calendário
          </h3>
          <p class="text-sm text-gray-600 dark:text-slate-400 mt-1">
            Sincronize eventos com Google Calendar e Outlook
          </p>
        </div>
        <IntegracoesView />
      </div>

      <!-- Seção: Comunicação -->
      <div v-else-if="secaoAtiva === 'comunicacao'" class="space-y-6">
        <div class="mb-6">
          <h3 class="text-2xl font-bold text-gray-900 dark:text-slate-100 flex items-center gap-2">
            <Plug class="w-6 h-6 text-green-600 dark:text-green-400" />
            Canais de Comunicação
          </h3>
          <p class="text-sm text-gray-600 dark:text-slate-400 mt-1">
            Configure Email, WhatsApp e SMS para notificações
          </p>
        </div>
        <ComunicacaoView />
      </div>

      <!-- Seção: Usuários e Equipe -->
      <div v-else-if="secaoAtiva === 'usuarios'" class="space-y-6">
        <div class="mb-6">
          <h3 class="text-2xl font-bold text-gray-900 dark:text-slate-100 flex items-center gap-2">
            <UserCog class="w-6 h-6 text-amber-600 dark:text-amber-400" />
            Usuários e Equipe
          </h3>
          <p class="text-sm text-gray-600 dark:text-slate-400 mt-1">
            Gerencie quem tem acesso ao sistema e seus perfis RBAC
          </p>
        </div>
        <UsuariosView />
      </div>

      <!-- Seção: Governança e Perfis (Largura Total) -->
      <div v-else-if="secaoAtiva === 'governanca'">
        <!-- Overlay com largura total -->
        <div
          class="fixed inset-0 bg-black/50 z-40"
          @click.self="secaoAtiva = 'classificacoes'"
        ></div>
        
        <div
          class="fixed inset-6 bg-white dark:bg-slate-900 rounded-lg shadow-2xl z-50 flex flex-col overflow-hidden"
          @click.stop
        >
          <!-- Header -->
          <div class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-slate-700 flex-shrink-0">
            <div>
              <h3 class="text-2xl font-bold text-gray-900 dark:text-slate-100 flex items-center gap-2">
                <Shield class="w-6 h-6 text-red-600 dark:text-red-400" />
                Governança e Perfis (RBAC)
              </h3>
              <p class="text-sm text-gray-600 dark:text-slate-400 mt-1">
                Matriz completa de permissões por perfil de usuário
              </p>
            </div>
            
            <button
              @click="secaoAtiva = 'classificacoes'"
              class="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg transition-colors"
              title="Fechar"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Conteúdo com scroll único -->
          <div class="flex-1 overflow-y-auto p-6">
            <GovernancaView />
          </div>
        </div>
      </div>
    </main>

    <!-- Modal de Tag -->
    <Modal
      :model-value="mostrarModal"
      @update:model-value="fecharModal"
      :titulo="tagEditando ? 'Editar Tag' : 'Nova Tag'"
      largura="md"
    >
      <form @submit.prevent="salvar" class="space-y-4">
        <div>
          <label class="label">Nome da Tag *</label>
          <input
            v-model="form.nome"
            type="text"
            class="input"
            placeholder="Ex: Urgente, VIP, Cadastro Incompleto"
            required
          />
        </div>

        <div>
          <label class="label">Tipo de uso no CRM *</label>
          <div class="space-y-2">
            <label
              v-for="opcao in tiposTag"
              :key="opcao.value"
              class="flex items-start gap-3 p-3 border rounded-lg cursor-pointer transition-colors"
              :class="
                form.tipo === opcao.value
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                  : 'border-gray-200 dark:border-slate-700'
              "
            >
              <input
                v-model="form.tipo"
                type="radio"
                :value="opcao.value"
                class="mt-1"
              />
              <span>
                <span class="block text-sm font-medium text-gray-900 dark:text-slate-100">{{ opcao.label }}</span>
                <span class="block text-xs text-gray-500 dark:text-slate-400">{{ opcao.descricao }}</span>
              </span>
            </label>
          </div>
        </div>

        <div>
          <label class="label">Disponível nos Módulos *</label>
          <p class="text-xs text-gray-500 dark:text-slate-400 mb-3">
            Selecione em quais módulos esta tag estará disponível (mínimo 1)
          </p>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <button
              type="button"
              @click="toggleModulo('crm')"
              :class="[
                form.modulos.includes('crm')
                  ? 'bg-green-50 dark:bg-green-900/30 border-green-500 dark:border-green-600 text-green-700 dark:text-green-400'
                  : 'bg-white dark:bg-slate-800 border-gray-300 dark:border-slate-600 text-gray-700 dark:text-slate-300',
                'flex items-center justify-center gap-2 px-4 py-3 border-2 rounded-lg font-medium transition-colors hover:border-green-400 dark:hover:border-green-600'
              ]"
            >
              <Users class="w-5 h-5" />
              CRM
            </button>

            <button
              type="button"
              @click="toggleModulo('atendimentos')"
              :class="[
                form.modulos.includes('atendimentos')
                  ? 'bg-blue-50 dark:bg-blue-900/30 border-blue-500 dark:border-blue-600 text-blue-700 dark:text-blue-400'
                  : 'bg-white dark:bg-slate-800 border-gray-300 dark:border-slate-600 text-gray-700 dark:text-slate-300',
                'flex items-center justify-center gap-2 px-4 py-3 border-2 rounded-lg font-medium transition-colors hover:border-blue-400 dark:hover:border-blue-600'
              ]"
            >
              <Inbox class="w-5 h-5" />
              Atendimentos
            </button>

          </div>
        </div>

        <div>
          <label class="label">Cor</label>
          <div class="grid grid-cols-4 gap-2">
            <button
              v-for="cor in cores"
              :key="cor.valor"
              @click="form.cor = cor.valor"
              type="button"
              :class="[
                form.cor === cor.valor
                  ? 'ring-2 ring-offset-2 ring-primary-600 dark:ring-offset-slate-800'
                  : '',
                'w-full h-12 rounded-lg transition-all hover:scale-105'
              ]"
              :style="{ backgroundColor: cor.valor }"
              :title="cor.nome"
            ></button>
          </div>

          <div class="mt-4 p-3 bg-gray-50 dark:bg-slate-900 rounded-lg">
            <p class="text-xs text-gray-600 dark:text-slate-400 mb-2">Preview:</p>
            <span
              class="inline-flex px-3 py-1.5 rounded-full text-sm font-medium"
              :style="{
                backgroundColor: form.cor + '20',
                color: form.cor,
                borderColor: form.cor + '40'
              }"
            >
              {{ form.nome || 'Nome da Tag' }}
            </span>
          </div>
        </div>
      </form>

      <template #footer>
        <Button variant="secondary" @click="fecharModal">
          Cancelar
        </Button>
        <Button variant="primary" @click="salvar" :disabled="!form.nome.trim()">
          {{ tagEditando ? 'Salvar Alterações' : 'Criar Tag' }}
        </Button>
      </template>
    </Modal>

    <!-- Modal de Aviso de Uso -->
    <Modal
      :model-value="mostrarAvisoUso"
      @update:model-value="mostrarAvisoUso = false"
      titulo="Tag em Uso"
      largura="md"
    >
      <div class="flex gap-4">
        <div class="flex-shrink-0">
          <div class="w-12 h-12 bg-yellow-100 dark:bg-yellow-900/30 rounded-full flex items-center justify-center">
            <AlertCircle class="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
          </div>
        </div>
        <div class="flex-1">
          <p class="text-gray-900 dark:text-slate-100 font-medium mb-2">
            Esta tag está em uso
          </p>
          <p class="text-sm text-gray-600 dark:text-slate-400">
            Esta tag está vinculada a <strong>{{ quantidadeUso }}</strong> {{ quantidadeUso === 1 ? 'registro' : 'registros' }}. 
            Você deve reatribuir os registros antes de excluí-la.
          </p>
        </div>
      </div>

      <template #footer>
        <Button variant="primary" @click="mostrarAvisoUso = false">
          Entendi
        </Button>
      </template>
    </Modal>
  </div>
</template>
