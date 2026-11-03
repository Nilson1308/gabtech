<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useAlertDialog } from '@/composables/useAlertDialog'
import Avatar from '@/components/common/Avatar.vue'
import Button from '@/components/common/Button.vue'
import AvatarCropper from '@/components/crm/AvatarCropper.vue'
import { User, Lock, Upload, X, Eye, EyeOff } from 'lucide-vue-next'

const authStore = useAuthStore()
const { showSuccess, showError } = useAlertDialog()

// Forms
const formPerfil = ref({
  nome: authStore.usuario?.nome || '',
  email: authStore.usuario?.email || ''
})

const formSenha = ref({
  senhaAtual: '',
  novaSenha: '',
  confirmarSenha: ''
})

// Estado
const avatarPreview = ref<string | null>(authStore.usuario?.avatar || null)
const avatarOriginal = ref<string | null>(null)
const mostrarCropper = ref(false)
const loadingPerfil = ref(false)
const loadingSenha = ref(false)
const mostrarSenhaAtual = ref(false)
const mostrarNovaSenha = ref(false)
const mostrarConfirmarSenha = ref(false)

// Avatar
const handleAvatarUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (file) {
    if (!file.type.startsWith('image/')) {
      showError('Por favor, selecione uma imagem')
      return
    }

    if (file.size > 5 * 1024 * 1024) {
      showError('Imagem deve ter no máximo 5MB')
      return
    }

    const reader = new FileReader()
    reader.onload = (e) => {
      avatarOriginal.value = e.target?.result as string
      mostrarCropper.value = true
    }
    reader.readAsDataURL(file)
  }
}

const handleCrop = (croppedImage: string) => {
  avatarPreview.value = croppedImage
  mostrarCropper.value = false
}

const removerAvatar = () => {
  avatarPreview.value = null
}

// Salvar perfil
const salvarPerfil = async () => {
  if (!formPerfil.value.nome.trim()) {
    showError('Nome é obrigatório')
    return
  }

  if (!formPerfil.value.email.trim()) {
    showError('E-mail é obrigatório')
    return
  }

  loadingPerfil.value = true
  
  try {
    // Mock: Em produção, faria chamada à API
    await new Promise(resolve => setTimeout(resolve, 800))
    
    showSuccess('Perfil atualizado com sucesso!')
  } catch (error) {
    showError('Erro ao atualizar perfil')
  } finally {
    loadingPerfil.value = false
  }
}

// Alterar senha
const alterarSenha = async () => {
  if (!formSenha.value.senhaAtual.trim()) {
    showError('Senha atual é obrigatória')
    return
  }

  if (!formSenha.value.novaSenha.trim()) {
    showError('Nova senha é obrigatória')
    return
  }

  if (formSenha.value.novaSenha.length < 6) {
    showError('A nova senha deve ter no mínimo 6 caracteres')
    return
  }

  if (formSenha.value.novaSenha !== formSenha.value.confirmarSenha) {
    showError('As senhas não conferem')
    return
  }

  loadingSenha.value = true
  
  try {
    // Mock: Em produção, faria chamada à API
    await new Promise(resolve => setTimeout(resolve, 800))
    
    // Limpar formulário
    formSenha.value = {
      senhaAtual: '',
      novaSenha: '',
      confirmarSenha: ''
    }
    
    showSuccess('Senha alterada com sucesso!')
  } catch (error) {
    showError('Erro ao alterar senha. Verifique sua senha atual.')
  } finally {
    loadingSenha.value = false
  }
}
</script>

<template>
  <div class="max-w-4xl mx-auto space-y-6">
    <!-- Header -->
    <div>
      <h2 class="text-2xl font-bold text-gray-900 dark:text-slate-100">Meu Perfil</h2>
      <p class="text-sm text-gray-600 dark:text-slate-400 mt-1">
        Gerencie suas informações pessoais e preferências de conta
      </p>
    </div>

    <!-- Informações do Perfil -->
    <div class="card">
      <div class="flex items-center justify-between mb-6 pb-4 border-b border-gray-200 dark:border-slate-700">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-slate-100 flex items-center gap-2">
          <User class="w-5 h-5" />
          Informações do Perfil
        </h3>
      </div>

      <form @submit.prevent="salvarPerfil" class="space-y-6">
        <!-- Avatar -->
        <div>
          <label class="label mb-3">Foto do Perfil</label>
          <div class="flex items-center gap-4">
            <div class="relative">
              <div class="w-24 h-24 rounded-full overflow-hidden bg-gray-100 dark:bg-slate-700 border-2 border-gray-300 dark:border-slate-600">
                <Avatar
                  v-if="!avatarPreview"
                  :nome="formPerfil.nome"
                  tamanho="xl"
                />
                <img
                  v-else
                  :src="avatarPreview"
                  alt="Avatar"
                  class="w-full h-full object-cover"
                />
              </div>
              <button
                v-if="avatarPreview"
                @click="removerAvatar"
                type="button"
                class="absolute -top-1 -right-1 w-6 h-6 bg-red-500 hover:bg-red-600 rounded-full flex items-center justify-center text-white transition-colors"
              >
                <X class="w-4 h-4" />
              </button>
            </div>

            <div class="flex-1">
              <label class="btn btn-secondary cursor-pointer inline-flex items-center gap-2">
                <Upload class="w-4 h-4" />
                {{ avatarPreview ? 'Alterar foto' : 'Carregar foto' }}
                <input
                  type="file"
                  accept="image/*"
                  @change="handleAvatarUpload"
                  class="hidden"
                />
              </label>
              <p class="text-xs text-gray-500 dark:text-slate-400 mt-2">
                PNG, JPG ou JPEG. Máximo 5MB.
              </p>
            </div>
          </div>
        </div>

        <!-- Nome -->
        <div>
          <label class="label">Nome Completo *</label>
          <input
            v-model="formPerfil.nome"
            type="text"
            class="input"
            required
          />
        </div>

        <!-- Email -->
        <div>
          <label class="label">E-mail *</label>
          <input
            v-model="formPerfil.email"
            type="email"
            class="input"
            required
          />
        </div>

        <!-- Cargo e Perfil (somente leitura) -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="label">Cargo</label>
            <input
              :value="authStore.usuario?.cargo || 'Não definido'"
              type="text"
              class="input bg-gray-50 dark:bg-slate-800"
              readonly
              disabled
            />
          </div>
        </div>

        <!-- Footer -->
        <div class="flex justify-end pt-4 border-t border-gray-200 dark:border-slate-700">
          <Button
            variant="primary"
            type="submit"
            :disabled="loadingPerfil"
          >
            <span v-if="!loadingPerfil">Salvar Alterações</span>
            <span v-else class="flex items-center gap-2">
              <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Salvando...
            </span>
          </Button>
        </div>
      </form>
    </div>

    <!-- Segurança -->
    <div class="card">
      <div class="flex items-center justify-between mb-6 pb-4 border-b border-gray-200 dark:border-slate-700">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-slate-100 flex items-center gap-2">
          <Lock class="w-5 h-5" />
          Segurança
        </h3>
      </div>

      <form @submit.prevent="alterarSenha" class="space-y-4">
        <!-- Senha Atual -->
        <div>
          <label class="label">Senha Atual *</label>
          <div class="relative">
            <input
              v-model="formSenha.senhaAtual"
              :type="mostrarSenhaAtual ? 'text' : 'password'"
              class="input pr-10"
              required
            />
            <button
              type="button"
              @click="mostrarSenhaAtual = !mostrarSenhaAtual"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <Eye v-if="!mostrarSenhaAtual" class="w-5 h-5" />
              <EyeOff v-else class="w-5 h-5" />
            </button>
          </div>
        </div>

        <!-- Nova Senha -->
        <div>
          <label class="label">Nova Senha *</label>
          <div class="relative">
            <input
              v-model="formSenha.novaSenha"
              :type="mostrarNovaSenha ? 'text' : 'password'"
              class="input pr-10"
              required
              minlength="6"
            />
            <button
              type="button"
              @click="mostrarNovaSenha = !mostrarNovaSenha"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <Eye v-if="!mostrarNovaSenha" class="w-5 h-5" />
              <EyeOff v-else class="w-5 h-5" />
            </button>
          </div>
          <p class="text-xs text-gray-500 dark:text-slate-400 mt-1">
            Mínimo de 6 caracteres
          </p>
        </div>

        <!-- Confirmar Nova Senha -->
        <div>
          <label class="label">Confirmar Nova Senha *</label>
          <div class="relative">
            <input
              v-model="formSenha.confirmarSenha"
              :type="mostrarConfirmarSenha ? 'text' : 'password'"
              class="input pr-10"
              required
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

        <!-- Footer -->
        <div class="flex justify-end pt-4 border-t border-gray-200 dark:border-slate-700">
          <Button
            variant="primary"
            type="submit"
            :disabled="loadingSenha"
          >
            <span v-if="!loadingSenha">Alterar Senha</span>
            <span v-else class="flex items-center gap-2">
              <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Alterando...
            </span>
          </Button>
        </div>
      </form>
    </div>
  </div>

  <!-- Avatar Cropper Modal -->
  <AvatarCropper
    v-model="mostrarCropper"
    :image-url="avatarOriginal || ''"
    @crop="handleCrop"
  />
</template>
