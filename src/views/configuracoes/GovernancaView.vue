<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useGovernancaStore } from '@/stores/governanca'
import { useAlertDialog } from '@/composables/useAlertDialog'
import { ApiError } from '@/services/api'
import type { Perfil } from '@/stores/governanca'
import Button from '@/components/common/Button.vue'
import Modal from '@/components/common/Modal.vue'
import RastreabilidadeMeta from '@/components/common/RastreabilidadeMeta.vue'
import { AUDITORIA_ALVO } from '@/services/auditoria'
import { 
  Plus, 
  Shield, 
  ShieldCheck, 
  User, 
  UserCheck, 
  UserPlus,
  Users,
  Inbox,
  Calendar,
  Settings,
  Edit,
  Trash2,
  AlertCircle,
  FileText,
  ChartBar,
  Briefcase,
} from 'lucide-vue-next'
import type { Component } from 'vue'

const governancaStore = useGovernancaStore()
const { showError } = useAlertDialog()

// Estado
const mostrarModalPerfil = ref(false)
const perfilEditando = ref<Perfil | null>(null)
const confirmandoExclusao = ref<string | null>(null)
const modoVisualizacao = ref<'tabela' | 'accordion'>('tabela')

// Form de Perfil
const formPerfil = ref({
  nome: '',
  cor: '#3b82f6',
  icone: 'user',
  descricao: ''
})

const coresDisponiveis = [
  { nome: 'Azul', valor: '#3b82f6' },
  { nome: 'Verde', valor: '#10b981' },
  { nome: 'Amarelo', valor: '#f59e0b' },
  { nome: 'Vermelho', valor: '#ef4444' },
  { nome: 'Roxo', valor: '#8b5cf6' },
  { nome: 'Rosa', valor: '#ec4899' },
  { nome: 'Cinza', valor: '#6b7280' },
  { nome: 'Indigo', valor: '#6366f1' },
]

const iconesDisponiveis = [
  { nome: 'Usuário', valor: 'user' },
  { nome: 'Usuário +', valor: 'user-plus' },
  { nome: 'Usuário ✓', valor: 'user-check' },
  { nome: 'Escudo', valor: 'shield' },
  { nome: 'Escudo ✓', valor: 'shield-check' },
]

// Mapa de ícones
const iconeMap: Record<string, Component> = {
  user: User,
  'user-plus': UserPlus,
  'user-check': UserCheck,
  shield: Shield,
  'shield-check': ShieldCheck,
  users: Users,
  inbox: Inbox,
  calendar: Calendar,
  settings: Settings,
  'file-text': FileText,
  'bar-chart': ChartBar,
  briefcase: Briefcase,
}

function iconeModulo(nome: string | undefined): Component {
  return iconeMap[nome ?? ''] ?? Settings
}

function iconePerfil(nome: string | undefined): Component {
  return iconeMap[nome ?? ''] ?? User
}

// Carregar dados
onMounted(async () => {
  await governancaStore.initialize()
  
  // Detectar modo mobile
  if (window.innerWidth < 1024) {
    modoVisualizacao.value = 'accordion'
  }
})

// Handlers
const abrirNovoPerfil = () => {
  perfilEditando.value = null
  formPerfil.value = {
    nome: '',
    cor: '#3b82f6',
    icone: 'user',
    descricao: ''
  }
  mostrarModalPerfil.value = true
}

const abrirEdicaoPerfil = (perfil: Perfil) => {
  if (perfil.isAdmin) return
  
  perfilEditando.value = perfil
  formPerfil.value = {
    nome: perfil.nome,
    cor: perfil.cor,
    icone: perfil.icone || 'user',
    descricao: perfil.descricao || ''
  }
  mostrarModalPerfil.value = true
}

const salvarPerfil = async () => {
  if (!formPerfil.value.nome.trim()) return

  try {
    if (perfilEditando.value) {
      await governancaStore.updatePerfil(perfilEditando.value.id, formPerfil.value)
    } else {
      await governancaStore.createPerfil(formPerfil.value)
    }
    fecharModalPerfil()
  } catch (err) {
    const msg = err instanceof ApiError ? err.message : 'Não foi possível salvar o perfil.'
    showError(msg)
  }
}

const fecharModalPerfil = () => {
  mostrarModalPerfil.value = false
  perfilEditando.value = null
  formPerfil.value = {
    nome: '',
    cor: '#3b82f6',
    icone: 'user',
    descricao: ''
  }
}

const handleExcluirPerfil = async (perfil: Perfil) => {
  if (perfil.isAdmin) return

  if (confirmandoExclusao.value !== perfil.id) {
    confirmandoExclusao.value = perfil.id
    setTimeout(() => {
      confirmandoExclusao.value = null
    }, 3000)
    return
  }

  try {
    await governancaStore.deletePerfil(perfil.id)
    confirmandoExclusao.value = null
  } catch (err) {
    const msg = err instanceof ApiError ? err.message : err instanceof Error ? err.message : 'Erro ao excluir perfil.'
    showError(msg)
    confirmandoExclusao.value = null
  }
}

const togglePermissao = async (perfilId: string, permissaoId: string) => {
  try {
    await governancaStore.togglePermissao(perfilId, permissaoId)
  } catch (err) {
    const msg = err instanceof ApiError ? err.message : 'Não foi possível salvar a permissão.'
    showError(msg)
  }
}

const onTogglePermissao = (perfil: Perfil, permissaoId: string) => {
  if (perfil.isAdmin) return
  void togglePermissao(perfil.id, permissaoId)
}
</script>

<template>
  <div class="space-y-6" @click.stop>
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <p class="text-sm text-gray-600 dark:text-slate-400">
        Gerencie permissões de acesso por perfil de usuário
      </p>

      <Button variant="primary" @click="abrirNovoPerfil">
        <Plus class="w-4 h-4" />
        Novo Perfil
      </Button>
    </div>

    <!-- Controle de Visualização (Mobile/Desktop) -->
    <div class="lg:hidden flex items-center gap-2 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
      <AlertCircle class="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0" />
      <p class="text-sm text-blue-900 dark:text-blue-300">
        Em telas pequenas, a matriz é exibida como acordeão por perfil
      </p>
    </div>

    <!-- Matriz de Permissões - TABELA (Desktop) -->
    <div v-if="modoVisualizacao === 'tabela'" class="card p-0 overflow-hidden hidden lg:block">
      <div class="overflow-x-auto">
        <table class="w-full border-collapse">
          <!-- Header -->
          <thead class="sticky top-0 z-10">
            <tr class="bg-gray-50 dark:bg-slate-900 border-b border-gray-200 dark:border-slate-700">
              <th class="sticky left-0 bg-gray-50 dark:bg-slate-900 px-6 py-4 text-left z-20">
                <span class="text-sm font-semibold text-gray-700 dark:text-slate-300 uppercase tracking-wide">
                  Módulo / Permissão
                </span>
              </th>
              <th
                v-for="perfil in governancaStore.perfis"
                :key="perfil.id"
                class="px-4 py-4 text-center min-w-[140px]"
              >
                <div class="flex flex-col items-center gap-2">
                  <!-- Ícone -->
                  <div
                    class="w-10 h-10 rounded-full flex items-center justify-center"
                    :style="{ backgroundColor: perfil.cor + '20' }"
                  >
                    <component
                      :is="iconePerfil(perfil.icone)"
                      class="w-5 h-5"
                      :style="{ color: perfil.cor }"
                    />
                  </div>
                  <!-- Nome -->
                  <div class="text-sm font-semibold text-gray-900 dark:text-slate-100">
                    {{ perfil.nome }}
                  </div>
                  <RastreabilidadeMeta
                    :rastreabilidade="perfil.rastreabilidade"
                    :alvo-auditoria="AUDITORIA_ALVO.perfil(perfil.id)"
                    historico-titulo="Histórico do perfil"
                    compact
                    class="mt-1"
                  />
                  <!-- Ações (apenas não-admin) -->
                  <div v-if="!perfil.isAdmin" class="flex items-center gap-1">
                    <button
                      @click="abrirEdicaoPerfil(perfil)"
                      class="p-1 hover:bg-gray-100 dark:hover:bg-slate-700 rounded text-gray-600 dark:text-slate-400 transition-colors"
                      title="Editar perfil"
                    >
                      <Edit class="w-3.5 h-3.5" />
                    </button>
                    <button
                      @click="handleExcluirPerfil(perfil)"
                      :class="[
                        confirmandoExclusao === perfil.id
                          ? 'bg-red-500 text-white'
                          : 'hover:bg-red-50 dark:hover:bg-red-900/30 text-red-600 dark:text-red-400',
                        'p-1 rounded transition-colors'
                      ]"
                      :title="confirmandoExclusao === perfil.id ? 'Confirmar exclusão' : 'Excluir perfil'"
                    >
                      <Trash2 class="w-3.5 h-3.5" />
                    </button>
                  </div>
                  <div v-else class="text-xs text-gray-500 dark:text-slate-500">
                    (Protegido)
                  </div>
                </div>
              </th>
            </tr>
          </thead>

          <!-- Body -->
          <tbody>
            <template v-for="modulo in governancaStore.modulos" :key="modulo.id">
              <!-- Header do Módulo -->
              <tr class="bg-gray-100 dark:bg-slate-800 border-t-2 border-gray-300 dark:border-slate-600">
                <td class="sticky left-0 bg-gray-100 dark:bg-slate-800 px-6 py-3" :colspan="governancaStore.perfis.length + 1">
                  <div class="flex items-center gap-2">
                    <component
                      :is="iconeModulo(modulo.icone)"
                      class="w-5 h-5"
                      :style="{ color: modulo.cor }"
                    />
                    <span class="font-semibold text-gray-900 dark:text-slate-100">
                      {{ modulo.nome }}
                    </span>
                  </div>
                </td>
              </tr>

              <!-- Permissões do Módulo -->
              <tr
                v-for="permissao in modulo.permissoes"
                :key="permissao.id"
                class="border-b border-gray-200 dark:border-slate-700 hover:bg-gray-50 dark:hover:bg-slate-800/50 transition-colors"
              >
                <!-- Nome da Permissão -->
                <td class="sticky left-0 bg-white dark:bg-slate-800 hover:bg-gray-50 dark:hover:bg-slate-800/50 px-6 py-4">
                  <div class="flex flex-col">
                    <span class="text-sm font-medium text-gray-900 dark:text-slate-100">
                      {{ permissao.nome }}
                    </span>
                    <span class="text-xs text-gray-500 dark:text-slate-400 mt-0.5">
                      {{ permissao.descricao }}
                    </span>
                  </div>
                </td>

                <!-- Toggles por Perfil -->
                <td
                  v-for="perfil in governancaStore.perfis"
                  :key="perfil.id"
                  class="px-4 py-4 text-center"
                >
                  <button
                    type="button"
                    role="switch"
                    :aria-checked="governancaStore.hasPermissao(perfil.id, permissao.id)"
                    :disabled="perfil.isAdmin"
                    class="inline-flex items-center rounded-full focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 disabled:opacity-70"
                    @click.stop="onTogglePermissao(perfil, permissao.id)"
                  >
                    <span
                      :class="[
                        'relative w-11 h-6 rounded-full transition-colors block',
                        governancaStore.hasPermissao(perfil.id, permissao.id)
                          ? perfil.isAdmin
                            ? 'bg-gray-400 dark:bg-slate-600'
                            : 'bg-primary-600 dark:bg-primary-500'
                          : 'bg-gray-200 dark:bg-slate-700',
                        perfil.isAdmin ? 'cursor-not-allowed' : 'cursor-pointer',
                      ]"
                    >
                      <span
                        :class="[
                          'absolute top-0.5 left-0.5 bg-white rounded-full h-5 w-5 transition-transform shadow-sm',
                          governancaStore.hasPermissao(perfil.id, permissao.id) ? 'translate-x-5' : 'translate-x-0',
                        ]"
                      />
                    </span>
                  </button>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>

      <!-- Legenda -->
      <div class="px-6 py-4 bg-gray-50 dark:bg-slate-900 border-t border-gray-200 dark:border-slate-700">
        <div class="flex items-center gap-6 text-sm text-gray-600 dark:text-slate-400">
          <div class="flex items-center gap-2">
            <div class="w-11 h-6 bg-primary-600 dark:bg-primary-500 rounded-full"></div>
            <span>Permissão Ativa</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-11 h-6 bg-gray-200 dark:bg-slate-700 rounded-full"></div>
            <span>Permissão Inativa</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-11 h-6 bg-gray-400 dark:bg-slate-600 rounded-full"></div>
            <span>Bloqueado (Admin)</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Matriz de Permissões - ACCORDION (Mobile) -->
    <div v-else class="space-y-4 lg:hidden">
      <div
        v-for="perfil in governancaStore.perfis"
        :key="perfil.id"
        class="card"
      >
        <!-- Header do Perfil -->
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-3">
            <div
              class="w-12 h-12 rounded-full flex items-center justify-center"
              :style="{ backgroundColor: perfil.cor + '20' }"
            >
              <component
                :is="iconePerfil(perfil.icone)"
                class="w-6 h-6"
                :style="{ color: perfil.cor }"
              />
            </div>
            <div>
              <h3 class="font-semibold text-gray-900 dark:text-slate-100">
                {{ perfil.nome }}
              </h3>
              <p v-if="perfil.descricao" class="text-xs text-gray-500 dark:text-slate-400">
                {{ perfil.descricao }}
              </p>
            </div>
          </div>

          <!-- Ações -->
          <div v-if="!perfil.isAdmin" class="flex items-center gap-1">
            <button
              @click="abrirEdicaoPerfil(perfil)"
              class="p-2 hover:bg-gray-100 dark:hover:bg-slate-700 rounded text-gray-600 dark:text-slate-400"
            >
              <Edit class="w-4 h-4" />
            </button>
            <button
              @click="handleExcluirPerfil(perfil)"
              :class="[
                confirmandoExclusao === perfil.id
                  ? 'bg-red-500 text-white'
                  : 'text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30',
                'p-2 rounded'
              ]"
            >
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Permissões por Módulo -->
        <div class="space-y-4">
          <div v-for="modulo in governancaStore.modulos" :key="modulo.id">
            <!-- Título do Módulo -->
            <div class="flex items-center gap-2 mb-2">
              <component
                :is="iconeModulo(modulo.icone)"
                class="w-4 h-4"
                :style="{ color: modulo.cor }"
              />
              <h4 class="text-sm font-semibold text-gray-900 dark:text-slate-100">
                {{ modulo.nome }}
              </h4>
            </div>

            <!-- Lista de Permissões -->
            <div class="space-y-2 pl-6">
              <div
                v-for="permissao in modulo.permissoes"
                :key="permissao.id"
                class="flex items-center justify-between py-2"
              >
                <div class="flex-1">
                  <p class="text-sm text-gray-900 dark:text-slate-100">
                    {{ permissao.nome }}
                  </p>
                  <p class="text-xs text-gray-500 dark:text-slate-400">
                    {{ permissao.descricao }}
                  </p>
                </div>

                <button
                  type="button"
                  role="switch"
                  :aria-checked="governancaStore.hasPermissao(perfil.id, permissao.id)"
                  :disabled="perfil.isAdmin"
                  class="inline-flex items-center ml-4 rounded-full focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 disabled:opacity-70"
                  @click.stop="onTogglePermissao(perfil, permissao.id)"
                >
                  <span
                    :class="[
                      'relative w-11 h-6 rounded-full transition-colors block',
                      governancaStore.hasPermissao(perfil.id, permissao.id)
                        ? perfil.isAdmin
                          ? 'bg-gray-400 dark:bg-slate-600'
                          : 'bg-primary-600 dark:bg-primary-500'
                        : 'bg-gray-200 dark:bg-slate-700',
                      perfil.isAdmin ? 'cursor-not-allowed' : 'cursor-pointer',
                    ]"
                  >
                    <span
                      :class="[
                        'absolute top-0.5 left-0.5 bg-white rounded-full h-5 w-5 transition-transform shadow-sm',
                        governancaStore.hasPermissao(perfil.id, permissao.id) ? 'translate-x-5' : 'translate-x-0',
                      ]"
                    />
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal de Perfil -->
    <Modal
      :model-value="mostrarModalPerfil"
      @update:model-value="fecharModalPerfil"
      :titulo="perfilEditando ? 'Editar Perfil' : 'Novo Perfil'"
      largura="md"
    >
      <form @submit.prevent="salvarPerfil" class="space-y-4">
        <!-- Nome -->
        <div>
          <label class="label">Nome do Perfil *</label>
          <input
            v-model="formPerfil.nome"
            type="text"
            class="input"
            placeholder="Ex: Estagiário, Coordenador"
            required
          />
        </div>

        <!-- Descrição -->
        <div>
          <label class="label">Descrição</label>
          <textarea
            v-model="formPerfil.descricao"
            rows="2"
            class="input"
            placeholder="Breve descrição do perfil (opcional)"
          ></textarea>
        </div>

        <!-- Cor -->
        <div>
          <label class="label">Cor do Perfil</label>
          <div class="grid grid-cols-4 gap-2">
            <button
              v-for="cor in coresDisponiveis"
              :key="cor.valor"
              @click="formPerfil.cor = cor.valor"
              type="button"
              :class="[
                formPerfil.cor === cor.valor
                  ? 'ring-2 ring-offset-2 ring-primary-600 dark:ring-offset-slate-800'
                  : '',
                'w-full h-10 rounded-lg transition-all hover:scale-105'
              ]"
              :style="{ backgroundColor: cor.valor }"
              :title="cor.nome"
            ></button>
          </div>
        </div>

        <!-- Ícone -->
        <div>
          <label class="label">Ícone</label>
          <div class="grid grid-cols-5 gap-2">
            <button
              v-for="icone in iconesDisponiveis"
              :key="icone.valor"
              @click="formPerfil.icone = icone.valor"
              type="button"
              :class="[
                formPerfil.icone === icone.valor
                  ? 'bg-primary-100 dark:bg-primary-900/30 border-primary-500 dark:border-primary-600'
                  : 'bg-white dark:bg-slate-800 border-gray-300 dark:border-slate-600',
                'h-12 border-2 rounded-lg flex items-center justify-center transition-all hover:scale-105'
              ]"
              :title="icone.nome"
            >
              <component
                :is="iconeMap[icone.valor]"
                class="w-5 h-5"
                :class="formPerfil.icone === icone.valor ? 'text-primary-600 dark:text-primary-400' : 'text-gray-600 dark:text-slate-400'"
              />
            </button>
          </div>
        </div>

        <!-- Preview -->
        <div class="p-3 bg-gray-50 dark:bg-slate-900 rounded-lg">
          <p class="text-xs text-gray-600 dark:text-slate-400 mb-2">Preview:</p>
          <div class="flex items-center gap-3">
            <div
              class="w-10 h-10 rounded-full flex items-center justify-center"
              :style="{ backgroundColor: formPerfil.cor + '20' }"
            >
              <component
                :is="iconeMap[formPerfil.icone]"
                class="w-5 h-5"
                :style="{ color: formPerfil.cor }"
              />
            </div>
            <div>
              <p class="font-semibold text-gray-900 dark:text-slate-100">
                {{ formPerfil.nome || 'Nome do Perfil' }}
              </p>
              <p v-if="formPerfil.descricao" class="text-xs text-gray-500 dark:text-slate-400">
                {{ formPerfil.descricao }}
              </p>
            </div>
          </div>
        </div>
      </form>

      <template #footer>
        <Button variant="secondary" @click="fecharModalPerfil">
          Cancelar
        </Button>
        <Button variant="primary" @click="salvarPerfil" :disabled="!formPerfil.nome.trim()">
          {{ perfilEditando ? 'Salvar Alterações' : 'Criar Perfil' }}
        </Button>
      </template>
    </Modal>
  </div>
</template>
