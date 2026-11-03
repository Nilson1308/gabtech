<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUsuariosStore } from '@/stores/usuarios'
import { useGovernancaStore } from '@/stores/governanca'
import type { Usuario } from '@/stores/usuarios'
import { useAlertDialog } from '@/composables/useAlertDialog'
import Button from '@/components/common/Button.vue'
import Modal from '@/components/common/Modal.vue'
import Avatar from '@/components/common/Avatar.vue'
import RastreabilidadeMeta from '@/components/common/RastreabilidadeMeta.vue'
import { AUDITORIA_ALVO } from '@/services/auditoria'
import { 
  Plus, 
  Edit, 
  Trash2,
  UserCheck,
  UserX,
  Mail,
  Shield,
  Eye,
  EyeOff
} from 'lucide-vue-next'

const usuariosStore = useUsuariosStore()
const governancaStore = useGovernancaStore()
const { showSuccess, showError, showWarning } = useAlertDialog()

// Estado
const mostrarModal = ref(false)
const usuarioEditando = ref<Usuario | null>(null)
const confirmandoExclusao = ref<string | null>(null)
const mostrarSenha = ref(false)
const mostrarConfirmarSenha = ref(false)

// Form
const form = ref({
  nome: '',
  email: '',
  senha: '',
  confirmarSenha: '',
  perfilId: '',
  status: 'ativo' as 'ativo' | 'inativo'
})

// Carregar dados
onMounted(async () => {
  await Promise.all([
    usuariosStore.fetchUsuarios(),
    governancaStore.fetchPerfis(),
  ])
})

// Computed
const usuariosOrdenados = computed(() => {
  return [...usuariosStore.usuarios].sort((a, b) => {
    // Ativos primeiro
    if (a.status === 'ativo' && b.status === 'inativo') return -1
    if (a.status === 'inativo' && b.status === 'ativo') return 1
    // Por nome
    return a.nome.localeCompare(b.nome)
  })
})

const getPerfilNome = (usuario: Usuario) => {
  if (usuario.perfilNome) return usuario.perfilNome
  const perfil = governancaStore.perfis.find(p => p.id === usuario.perfilId)
  return perfil?.nome || usuario.cargo || 'Sem perfil'
}

const getPerfilCor = (usuario: Usuario) => {
  if (usuario.perfilCor) return usuario.perfilCor
  const perfil = governancaStore.perfis.find(p => p.id === usuario.perfilId)
  return perfil?.cor || '#6b7280'
}

const getPerfilNomeById = (perfilId: string) => {
  const perfil = governancaStore.perfis.find(p => p.id === perfilId)
  return perfil?.nome || 'Sem perfil'
}

const getPerfilCorById = (perfilId: string) => {
  const perfil = governancaStore.perfis.find(p => p.id === perfilId)
  return perfil?.cor || '#6b7280'
}

// Handlers
const abrirNovo = () => {
  usuarioEditando.value = null
  form.value = {
    nome: '',
    email: '',
    senha: '',
    confirmarSenha: '',
    perfilId: governancaStore.perfis[0]?.id || '',
    status: 'ativo'
  }
  mostrarModal.value = true
}

const abrirEdicao = (usuario: Usuario) => {
  usuarioEditando.value = usuario
  form.value = {
    nome: usuario.nome,
    email: usuario.email,
    senha: '',
    confirmarSenha: '',
    perfilId: usuario.perfilId,
    status: usuario.status
  }
  mostrarModal.value = true
}

const salvar = async () => {
  // Validação básica
  if (!form.value.nome.trim() || !form.value.email.trim() || !form.value.perfilId) {
    await showWarning('Preencha nome, e-mail e perfil de acesso.')
    return
  }

  // Validação de senha (obrigatória apenas na criação)
  if (!usuarioEditando.value) {
    if (!form.value.senha.trim()) {
      await showWarning('Senha é obrigatória para novos usuários.')
      return
    }

    if (form.value.senha.length < 6) {
      await showWarning('A senha deve ter no mínimo 6 caracteres.')
      return
    }

    if (form.value.senha !== form.value.confirmarSenha) {
      await showWarning('As senhas não conferem.')
      return
    }
  }

  // Validação de senha na edição (se preenchida)
  if (usuarioEditando.value && form.value.senha.trim()) {
    if (form.value.senha.length < 6) {
      await showWarning('A senha deve ter no mínimo 6 caracteres.')
      return
    }

    if (form.value.senha !== form.value.confirmarSenha) {
      await showWarning('As senhas não conferem.')
      return
    }
  }

  try {
    if (usuarioEditando.value) {
      await usuariosStore.updateUsuario(usuarioEditando.value.id, {
        nome: form.value.nome,
        email: form.value.email,
        perfilId: form.value.perfilId,
        status: form.value.status,
        senha: form.value.senha.trim() || undefined,
      })
      await showSuccess('Usuário atualizado com sucesso!')
    } else {
      await usuariosStore.createUsuario({
        nome: form.value.nome,
        email: form.value.email,
        perfilId: form.value.perfilId,
        status: form.value.status,
        senha: form.value.senha,
      })
      await showSuccess('Usuário criado com sucesso!')
    }
    fecharModal()
  } catch {
    await showError(usuariosStore.error || 'Não foi possível salvar o usuário.')
  }
}

const fecharModal = () => {
  mostrarModal.value = false
  usuarioEditando.value = null
  mostrarSenha.value = false
  mostrarConfirmarSenha.value = false
  form.value = {
    nome: '',
    email: '',
    senha: '',
    confirmarSenha: '',
    perfilId: '',
    status: 'ativo'
  }
}

const handleExcluir = async (usuario: Usuario) => {
  if (confirmandoExclusao.value !== usuario.id) {
    confirmandoExclusao.value = usuario.id
    setTimeout(() => {
      confirmandoExclusao.value = null
    }, 3000)
    return
  }

  await usuariosStore.deleteUsuario(usuario.id)
  confirmandoExclusao.value = null
}

const toggleStatus = async (usuario: Usuario) => {
  await usuariosStore.toggleStatus(usuario.id)
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm text-gray-600 dark:text-slate-400 mt-1">
          {{ usuariosStore.usuarios.length }} {{ usuariosStore.usuarios.length === 1 ? 'usuário cadastrado' : 'usuários cadastrados' }}
        </p>
      </div>

      <Button variant="primary" @click="abrirNovo">
        <Plus class="w-4 h-4" />
        Novo Usuário
      </Button>
    </div>

    <!-- Lista de Usuários -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="usuario in usuariosOrdenados"
        :key="usuario.id"
        class="card group hover:shadow-lg transition-all"
        :class="{ 'opacity-60': usuario.status === 'inativo' }"
      >
        <!-- Header do Card -->
        <div class="flex items-start gap-3 mb-3">
          <Avatar :nome="usuario.nome" tamanho="md" />
          
          <div class="flex-1 min-w-0">
            <h3 class="font-semibold text-gray-900 dark:text-slate-100 truncate">
              {{ usuario.nome }}
            </h3>
            <div class="flex items-center gap-2 text-sm text-gray-600 dark:text-slate-400 mt-1">
              <Mail class="w-3 h-3" />
              <span class="truncate">{{ usuario.email }}</span>
            </div>
            <RastreabilidadeMeta
              :rastreabilidade="usuario.rastreabilidade"
              :alvo-auditoria="AUDITORIA_ALVO.usuario(usuario.id)"
              historico-titulo="Histórico do usuário"
              compact
              class="mt-2"
            />
          </div>

          <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              @click="abrirEdicao(usuario)"
              class="p-1.5 hover:bg-gray-100 dark:hover:bg-slate-700 rounded text-gray-600 dark:text-slate-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
              title="Editar"
            >
              <Edit class="w-4 h-4" />
            </button>
            <button
              @click="handleExcluir(usuario)"
              :class="[
                confirmandoExclusao === usuario.id
                  ? 'bg-red-500 text-white'
                  : 'hover:bg-red-50 dark:hover:bg-red-900/30 text-red-600 dark:text-red-400',
                'p-1.5 rounded transition-colors'
              ]"
              :title="confirmandoExclusao === usuario.id ? 'Confirmar exclusão' : 'Excluir'"
            >
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Perfil RBAC -->
        <div class="mb-3">
          <div class="flex items-center gap-2">
            <Shield class="w-4 h-4 text-gray-400 dark:text-slate-500" />
            <span
              class="px-2 py-1 rounded text-xs font-medium"
              :style="{
                backgroundColor: getPerfilCor(usuario) + '20',
                color: getPerfilCor(usuario)
              }"
            >
              {{ getPerfilNome(usuario) }}
            </span>
          </div>
        </div>

        <!-- Status e Ações -->
        <div class="flex items-center justify-between pt-3 border-t border-gray-200 dark:border-slate-700">
          <button
            @click="toggleStatus(usuario)"
            class="flex items-center gap-2 text-sm font-medium transition-colors"
            :class="usuario.status === 'ativo' 
              ? 'text-green-600 dark:text-green-400 hover:text-green-700 dark:hover:text-green-300'
              : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'"
          >
            <UserCheck v-if="usuario.status === 'ativo'" class="w-4 h-4" />
            <UserX v-else class="w-4 h-4" />
            {{ usuario.status === 'ativo' ? 'Ativo' : 'Inativo' }}
          </button>

          <span class="text-xs text-gray-500 dark:text-slate-400">
            {{ new Date(usuario.createdAt).toLocaleDateString('pt-BR') }}
          </span>
        </div>
      </div>
    </div>

    <div v-if="usuariosStore.loading && usuariosStore.usuarios.length === 0" class="card text-center py-12">
      <p class="text-gray-500 dark:text-slate-400">Carregando usuários...</p>
    </div>

    <div v-else-if="usuariosStore.usuarios.length === 0" class="card text-center py-12">
      <Shield class="w-16 h-16 text-gray-300 dark:text-slate-600 mx-auto mb-4" />
      <p class="text-gray-500 dark:text-slate-400">Nenhum usuário cadastrado</p>
    </div>

    <!-- Modal de Usuário -->
    <Modal
      :model-value="mostrarModal"
      @update:model-value="fecharModal"
      :titulo="usuarioEditando ? 'Editar Usuário' : 'Novo Usuário'"
      largura="md"
    >
      <form @submit.prevent="salvar" class="space-y-4">
        <div>
          <label class="label">Nome Completo *</label>
          <input
            v-model="form.nome"
            type="text"
            class="input"
            placeholder="Ex: João da Silva"
            required
          />
        </div>

        <div>
          <label class="label">E-mail *</label>
          <input
            v-model="form.email"
            type="email"
            class="input"
            placeholder="usuario@gabinete.gov.br"
            required
          />
          <p class="text-xs text-gray-500 dark:text-slate-400 mt-1">
            O e-mail será usado para login no sistema
          </p>
        </div>

        <!-- Senha -->
        <div>
          <label class="label">
            {{ usuarioEditando ? 'Nova Senha (deixe em branco para manter)' : 'Senha *' }}
          </label>
          <div class="relative">
            <input
              v-model="form.senha"
              :type="mostrarSenha ? 'text' : 'password'"
              class="input pr-10"
              placeholder="Mínimo 6 caracteres"
              :required="!usuarioEditando"
            />
            <button
              type="button"
              @click="mostrarSenha = !mostrarSenha"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <Eye v-if="!mostrarSenha" class="w-5 h-5" />
              <EyeOff v-else class="w-5 h-5" />
            </button>
          </div>
        </div>

        <!-- Confirmar Senha -->
        <div>
          <label class="label">
            {{ usuarioEditando ? 'Confirmar Nova Senha' : 'Confirmar Senha *' }}
          </label>
          <div class="relative">
            <input
              v-model="form.confirmarSenha"
              :type="mostrarConfirmarSenha ? 'text' : 'password'"
              class="input pr-10"
              placeholder="Digite a senha novamente"
              :required="!usuarioEditando"
            />
            <button
              type="button"
              @click="mostrarConfirmarSenha = !mostrarConfirmarSenha"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <Eye v-if="!mostrarConfirmarSenha" class="w-5 h-5" />
              <EyeOff v-else class="w-5 h-5" />
            </button>
          </div>
        </div>

        <div>
          <label class="label">Perfil de Acesso (RBAC) *</label>
          <select
            v-model="form.perfilId"
            class="input"
            required
          >
            <option value="">Selecione um perfil...</option>
            <option
              v-for="perfil in governancaStore.perfis"
              :key="perfil.id"
              :value="perfil.id"
            >
              {{ perfil.nome }}
              <span v-if="perfil.isAdmin"> (Administrador)</span>
            </option>
          </select>
          <p class="text-xs text-gray-500 dark:text-slate-400 mt-1">
            Define as permissões de acesso do usuário
          </p>
        </div>

        <div>
          <label class="label">Status</label>
          <div class="flex gap-4">
            <label class="flex items-center gap-2 cursor-pointer">
              <input
                v-model="form.status"
                type="radio"
                value="ativo"
                class="w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 focus:ring-primary-500"
              />
              <span class="text-sm text-gray-700 dark:text-slate-300">Ativo</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input
                v-model="form.status"
                type="radio"
                value="inativo"
                class="w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 focus:ring-primary-500"
              />
              <span class="text-sm text-gray-700 dark:text-slate-300">Inativo</span>
            </label>
          </div>
        </div>

        <!-- Preview do Perfil -->
        <div v-if="form.perfilId" class="p-3 bg-gray-50 dark:bg-slate-900 rounded-lg">
          <p class="text-xs text-gray-600 dark:text-slate-400 mb-2">Preview:</p>
          <div class="flex items-center gap-3">
            <Avatar :nome="form.nome || 'Usuário'" tamanho="sm" />
            <div class="flex-1">
              <p class="font-semibold text-gray-900 dark:text-slate-100 text-sm">
                {{ form.nome || 'Nome do Usuário' }}
              </p>
              <div class="flex items-center gap-2 mt-1">
                <span
                  class="px-2 py-0.5 rounded text-xs font-medium"
                  :style="{
                    backgroundColor: getPerfilCorById(form.perfilId) + '20',
                    color: getPerfilCorById(form.perfilId)
                  }"
                >
                  {{ getPerfilNomeById(form.perfilId) }}
                </span>
                <span
                  class="px-2 py-0.5 rounded text-xs font-medium"
                  :class="form.status === 'ativo'
                    ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'"
                >
                  {{ form.status === 'ativo' ? 'Ativo' : 'Inativo' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </form>

      <template #footer>
        <Button variant="secondary" @click="fecharModal">
          Cancelar
        </Button>
        <Button variant="primary" @click="salvar" :disabled="!form.nome.trim() || !form.email.trim() || !form.perfilId">
          {{ usuarioEditando ? 'Salvar Alterações' : 'Criar Usuário' }}
        </Button>
      </template>
    </Modal>
  </div>
</template>
