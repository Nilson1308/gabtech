<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useCrmStore } from '@/stores/crm'
import { useAuthStore } from '@/stores/auth'
import { PERMS } from '@/constants/rbac'
import type { Cidadao } from '@/types'
import DocumentosUpload from '@/components/crm/DocumentosUpload.vue'
import Modal from '@/components/common/Modal.vue'
import Button from '@/components/common/Button.vue'
import AvatarCropper from '@/components/crm/AvatarCropper.vue'
import { Loader2, Upload, X } from 'lucide-vue-next'
import { geocodificarEndereco } from '@/utils/geocode'

interface Props {
  modelValue: boolean
  cidadao?: Cidadao | null
}

const props = withDefaults(defineProps<Props>(), {
  cidadao: null
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  success: []
}>()

const crmStore = useCrmStore()
const authStore = useAuthStore()

const podeEditarDocumentos = computed(() => authStore.hasPermission(PERMS.crmEdit))

// Form data
const form = ref({
  nome: '',
  nome_social: '',
  cpf: '',
  telefone: '',
  email: '',
  logradouro: '',
  numero: '',
  complemento: '',
  bairro: '',
  cidade: '',
  estado: '',
  cep: '',
  observacoes: '',
  tag_ids: [] as string[],
  perfis_profissionais: [] as Array<{ id: string; instituicao: string; cargo: string; tag_id: string }>
})

const loading = ref(false)
const erro = ref<string | null>(null)

// Avatar (declarar antes de resetForm / watch immediate)
const avatarPreview = ref<string | null>(null)
const avatarOriginal = ref<string | null>(null)
const mostrarCropper = ref(false)

// Título do modal
const titulo = computed(() => {
  return props.cidadao ? 'Editar Cidadão' : 'Novo Cidadão'
})

const resetForm = () => {
  form.value = {
    nome: '',
    nome_social: '',
    cpf: '',
    telefone: '',
    email: '',
    logradouro: '',
    numero: '',
    complemento: '',
    bairro: '',
    cidade: '',
    estado: '',
    cep: '',
    observacoes: '',
    tag_ids: [],
    perfis_profissionais: [],
  }
  avatarPreview.value = null
  avatarOriginal.value = null
  erro.value = null
}

// Carregar dados do cidadão ao abrir para edição
watch(() => props.cidadao, (novoCidadao) => {
  if (novoCidadao) {
    form.value = {
      nome: novoCidadao.nome,
      nome_social: novoCidadao.nome_social || '',
      cpf: novoCidadao.cpf || '',
      telefone: novoCidadao.telefone,
      email: novoCidadao.email || '',
      logradouro: novoCidadao.endereco?.logradouro || '',
      numero: novoCidadao.endereco?.numero || '',
      complemento: novoCidadao.endereco?.complemento || '',
      bairro: novoCidadao.endereco?.bairro || '',
      cidade: novoCidadao.endereco?.cidade || '',
      estado: novoCidadao.endereco?.estado || '',
      cep: novoCidadao.endereco?.cep || '',
      observacoes: novoCidadao.observacoes || '',
      tag_ids: [...(novoCidadao.tag_ids ?? [])],
      perfis_profissionais: novoCidadao.perfis_profissionais || [],
    }
    avatarPreview.value = novoCidadao.avatar || null
    avatarOriginal.value = null
  } else {
    resetForm()
  }
}, { immediate: true })

// Máscaras de formatação
const formatCPF = (value: string) => {
  const cleaned = value.replace(/\D/g, '')
  return cleaned
    .replace(/(\d{3})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d)/, '$1.$2')
    .replace(/(\d{3})(\d{1,2})$/, '$1-$2')
    .substring(0, 14)
}

const formatTelefone = (value: string) => {
  const cleaned = value.replace(/\D/g, '')
  if (cleaned.length <= 10) {
    return cleaned
      .replace(/(\d{2})(\d)/, '($1) $2')
      .replace(/(\d{4})(\d)/, '$1-$2')
  }
  return cleaned
    .replace(/(\d{2})(\d)/, '($1) $2')
    .replace(/(\d{5})(\d)/, '$1-$2')
    .substring(0, 15)
}

const formatCEP = (value: string) => {
  const cleaned = value.replace(/\D/g, '')
  return cleaned
    .replace(/(\d{5})(\d)/, '$1-$2')
    .substring(0, 9)
}

// Estados para ViaCEP
const buscandoCep = ref(false)
const erroCep = ref<string | null>(null)

// Buscar CEP na API ViaCEP
const buscarCep = async (cep: string) => {
  const cepLimpo = cep.replace(/\D/g, '')
  
  if (cepLimpo.length !== 8) {
    erroCep.value = null
    return
  }

  buscandoCep.value = true
  erroCep.value = null

  try {
    const response = await fetch(`https://viacep.com.br/ws/${cepLimpo}/json/`)
    const data = await response.json()

    if (data.erro) {
      erroCep.value = 'CEP não encontrado'
      return
    }

    // Preencher campos automaticamente
    form.value.logradouro = data.logradouro || ''
    form.value.bairro = data.bairro || ''
    form.value.cidade = data.localidade || ''
    form.value.estado = data.uf || ''
  } catch (error) {
    erroCep.value = 'Erro ao buscar CEP'
  } finally {
    buscandoCep.value = false
  }
}

// Handlers de input com máscara
const handleCPFInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  form.value.cpf = formatCPF(target.value)
}

const handleTelefoneInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  form.value.telefone = formatTelefone(target.value)
}

const handleCEPInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  form.value.cep = formatCEP(target.value)
}

// Handler de upload de avatar
const handleAvatarUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (file) {
    if (!file.type.startsWith('image/')) {
      erro.value = 'Por favor, selecione uma imagem'
      return
    }

    if (file.size > 5 * 1024 * 1024) {
      erro.value = 'Imagem deve ter no máximo 5MB'
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

const handleCrop = (dataUrl: string) => {
  avatarPreview.value = dataUrl
}

const removerAvatar = () => {
  avatarPreview.value = null
  avatarOriginal.value = null
}

// Watch no CEP para buscar automaticamente
watch(() => form.value.cep, (novoCep) => {
  const cepLimpo = novoCep.replace(/\D/g, '')
  if (cepLimpo.length === 8) {
    buscarCep(novoCep)
  }
})

// Gerenciamento de Perfis Profissionais
const adicionarPerfilProfissional = () => {
  form.value.perfis_profissionais.push({
    id: `perfil-${Date.now()}`,
    instituicao: '',
    cargo: '',
    tag_id: ''
  })
}

const removerPerfilProfissional = (id: string) => {
  const index = form.value.perfis_profissionais.findIndex(p => p.id === id)
  if (index > -1) {
    form.value.perfis_profissionais.splice(index, 1)
  }
}

const selecionarTagPerfil = (perfilId: string, tagId: string) => {
  const perfil = form.value.perfis_profissionais.find(p => p.id === perfilId)
  if (perfil) {
    // Toggle: se já está selecionada, desmarca; senão, seleciona
    perfil.tag_id = perfil.tag_id === tagId ? '' : tagId
  }
}

const toggleMarcador = (tagId: string) => {
  const index = form.value.tag_ids.indexOf(tagId)
  if (index > -1) {
    form.value.tag_ids.splice(index, 1)
  } else {
    form.value.tag_ids.push(tagId)
  }
}

// Validação
const validar = (): boolean => {
  if (!form.value.nome.trim()) {
    erro.value = 'Nome é obrigatório'
    return false
  }
  if (!form.value.telefone.trim()) {
    erro.value = 'Telefone é obrigatório'
    return false
  }
  erro.value = null
  return true
}

// Salvar
const salvar = async () => {
  if (!validar()) return

  loading.value = true
  erro.value = null

  try {
    const dadosCidadao: Partial<Cidadao> = {
      nome: form.value.nome,
      nome_social: form.value.nome_social || undefined,
      cpf: form.value.cpf || undefined,
      telefone: form.value.telefone,
      email: form.value.email || undefined,
      bairro: form.value.bairro,
      observacoes: form.value.observacoes || undefined,
      avatar: avatarPreview.value ?? '',
      tag_ids: [...form.value.tag_ids],
      perfis_profissionais: form.value.perfis_profissionais.filter(p => p.instituicao && p.cargo),
    }

    // Adicionar endereço se pelo menos um campo foi preenchido
    if (form.value.logradouro || form.value.bairro || form.value.cidade) {
      const enderecoBase = {
        logradouro: form.value.logradouro,
        numero: form.value.numero,
        complemento: form.value.complemento || undefined,
        bairro: form.value.bairro,
        cidade: form.value.cidade,
        estado: form.value.estado,
        cep: form.value.cep,
      }

      const coords = await geocodificarEndereco(enderecoBase)
      dadosCidadao.endereco = {
        ...enderecoBase,
        latitude: coords?.latitude ?? props.cidadao?.endereco?.latitude ?? null,
        longitude: coords?.longitude ?? props.cidadao?.endereco?.longitude ?? null,
      }
    }

    if (props.cidadao) {
      // Editar
      await crmStore.updateCidadao(props.cidadao.id, dadosCidadao)
    } else {
      // Criar
      await crmStore.createCidadao(dadosCidadao)
    }

    emit('success')
    fechar()
  } catch (error) {
    erro.value = 'Erro ao salvar. Tente novamente.'
  } finally {
    loading.value = false
  }
}

const fechar = () => {
  emit('update:modelValue', false)
  if (!props.cidadao) {
    resetForm()
  }
}
</script>

<template>
  <Modal
    :model-value="modelValue"
    @update:model-value="fechar"
    :titulo="titulo"
    largura="2xl"
  >
    <!-- Alerta de Erro -->
    <div
      v-if="erro"
      class="mb-4 p-3 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg text-sm text-red-800 dark:text-red-300"
    >
      {{ erro }}
    </div>

    <!-- Formulário -->
    <form @submit.prevent="salvar" class="space-y-6">
      <!-- Foto/Avatar -->
      <div>
        <h4 class="text-sm font-semibold text-gray-900 dark:text-slate-100 mb-3">Foto do Cidadão</h4>
        <div class="flex items-center gap-4">
          <!-- Preview do Avatar -->
          <div class="relative">
            <div 
              class="w-24 h-24 rounded-full bg-gray-100 dark:bg-slate-700 border-2 border-gray-300 dark:border-slate-600 overflow-hidden flex items-center justify-center"
            >
              <img 
                v-if="avatarPreview" 
                :src="avatarPreview" 
                alt="Preview" 
                class="w-full h-full object-cover"
              />
              <Upload v-else class="w-8 h-8 text-gray-400 dark:text-slate-500" />
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

          <!-- Upload -->
          <div class="flex-1">
            <label class="btn btn-secondary cursor-pointer inline-flex items-center gap-2">
              <Upload class="w-4 h-4" />
              {{ avatarPreview ? 'Alterar foto' : 'Selecionar foto' }}
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

      <!-- Dados Básicos -->
      <div>
        <h4 class="text-sm font-semibold text-gray-900 dark:text-slate-100 mb-3">Dados Básicos</h4>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="md:col-span-2">
            <label class="label">Nome Completo *</label>
            <input
              v-model="form.nome"
              type="text"
              class="input"
              required
            />
          </div>

          <div class="md:col-span-2">
            <label class="label">Nome Social</label>
            <input
              v-model="form.nome_social"
              type="text"
              class="input"
              placeholder="Nome pelo qual prefere ser chamado(a)"
            />
            <p class="text-xs text-gray-500 dark:text-slate-400 mt-1">
              O nome social será exibido com prioridade quando cadastrado (Decreto 8.727/2016)
            </p>
          </div>

          <div>
            <label class="label">CPF</label>
            <input
              :value="form.cpf"
              @input="handleCPFInput"
              type="text"
              class="input"
              placeholder="000.000.000-00"
            />
          </div>

          <div>
            <label class="label">Telefone *</label>
            <input
              :value="form.telefone"
              @input="handleTelefoneInput"
              type="text"
              class="input"
              placeholder="(00) 00000-0000"
              required
            />
          </div>

          <div class="md:col-span-2">
            <label class="label">E-mail</label>
            <input
              v-model="form.email"
              type="email"
              class="input"
            />
          </div>
        </div>
      </div>

      <!-- Marcadores do cidadão -->
      <div>
        <h4 class="text-sm font-semibold text-gray-900 dark:text-slate-100 mb-1">Marcadores do cidadão</h4>
        <p class="text-xs text-gray-500 dark:text-slate-400 mb-3">
          Classifique o munícipe para filtros e relatórios (ex.: Idoso, PCD, Liderança de bairro). Não exige vínculo com órgão.
        </p>
        <div
          v-if="crmStore.tagsParaMarcadores().length === 0"
          class="p-4 border-2 border-dashed border-gray-300 dark:border-slate-600 rounded-lg text-center text-sm text-gray-500 dark:text-slate-400"
        >
          Nenhuma tag de segmentação cadastrada. Crie em Configurações → Classificações (tipo “Segmentação”).
        </div>
        <div
          v-else
          class="flex flex-wrap gap-2 p-3 border border-gray-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-900/50 min-h-[60px]"
        >
          <button
            v-for="tag in crmStore.tagsParaMarcadores()"
            :key="tag.id"
            type="button"
            @click.prevent="toggleMarcador(tag.id)"
            :style="{
              backgroundColor: form.tag_ids.includes(tag.id) ? tag.cor : tag.cor + '20',
              color: form.tag_ids.includes(tag.id) ? '#fff' : tag.cor,
              borderColor: tag.cor,
            }"
            class="px-3 py-1.5 rounded-full text-xs font-medium border-2 transition-all hover:scale-105 hover:shadow-md"
            :class="{ 'ring-2 ring-offset-2 ring-offset-gray-50 dark:ring-offset-slate-800': form.tag_ids.includes(tag.id) }"
          >
            {{ tag.nome }}
          </button>
        </div>
      </div>

      <!-- Perfis Profissionais -->
      <div>
        <div class="flex items-center justify-between mb-3">
          <h4 class="text-sm font-semibold text-gray-900 dark:text-slate-100">Perfis Profissionais</h4>
          <button
            type="button"
            @click="adicionarPerfilProfissional"
            class="text-sm text-primary-600 dark:text-primary-400 hover:underline flex items-center gap-1"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Adicionar Perfil
          </button>
        </div>

        <div v-if="form.perfis_profissionais.length === 0" class="p-4 border-2 border-dashed border-gray-300 dark:border-slate-600 rounded-lg text-center">
          <p class="text-sm text-gray-500 dark:text-slate-400">
            Nenhum perfil profissional cadastrado. Clique em "Adicionar Perfil" para incluir cargos e instituições.
          </p>
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="perfil in form.perfis_profissionais"
            :key="perfil.id"
            class="p-4 border border-gray-200 dark:border-slate-700 rounded-lg bg-gray-50 dark:bg-slate-800/50"
          >
            <div class="flex items-start gap-3">
              <div class="flex-1 space-y-3">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <label class="label text-xs">Órgão/Instituição *</label>
                    <input
                      v-model="perfil.instituicao"
                      type="text"
                      class="input text-sm"
                      placeholder="Ex: Prefeitura Municipal"
                    />
                  </div>
                  <div>
                    <label class="label text-xs">Cargo *</label>
                    <input
                      v-model="perfil.cargo"
                      type="text"
                      class="input text-sm"
                      placeholder="Ex: Secretário de Saúde"
                    />
                  </div>
                </div>
                
                <!-- Tag de Contexto Visual -->
                <div>
                  <label class="label text-xs">Tag de contexto (opcional)</label>
                  <div class="flex flex-wrap gap-2 p-3 border border-gray-200 dark:border-slate-700 rounded-lg bg-white dark:bg-slate-900/50 min-h-[60px]">
                    <button
                      v-for="tag in crmStore.tagsParaPerfil()"
                      :key="tag.id"
                      @click.prevent="selecionarTagPerfil(perfil.id, tag.id)"
                      type="button"
                      :style="{ 
                        backgroundColor: perfil.tag_id === tag.id ? tag.cor : tag.cor + '20',
                        color: perfil.tag_id === tag.id ? '#fff' : tag.cor,
                        borderColor: tag.cor
                      }"
                      class="px-3 py-1.5 rounded-full text-xs font-medium border-2 transition-all hover:scale-105 hover:shadow-md"
                      :class="{ 'ring-2 ring-offset-2 ring-offset-gray-50 dark:ring-offset-slate-800': perfil.tag_id === tag.id }"
                    >
                      {{ tag.nome }}
                    </button>
                  </div>
                  <p class="text-xs text-gray-500 dark:text-slate-400 mt-1">
                    Clique na tag que melhor representa este perfil
                  </p>
                </div>
              </div>
              <button
                type="button"
                @click="removerPerfilProfissional(perfil.id)"
                class="p-1.5 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 rounded transition-colors"
                title="Remover perfil"
              >
                <X class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Endereço -->
      <div>
        <h4 class="text-sm font-semibold text-gray-900 dark:text-slate-100 mb-3">Endereço</h4>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="label">CEP</label>
            <div class="relative">
              <input
                :value="form.cep"
                @input="handleCEPInput"
                type="text"
                class="input pr-10"
                placeholder="00000-000"
                :disabled="buscandoCep"
              />
              <div class="absolute right-3 top-1/2 -translate-y-1/2">
                <Loader2 v-if="buscandoCep" class="w-5 h-5 text-primary-600 dark:text-primary-400 animate-spin" />
              </div>
            </div>
            <p v-if="erroCep" class="text-xs text-red-600 dark:text-red-400 mt-1">{{ erroCep }}</p>
            <p v-else class="text-xs text-gray-500 dark:text-slate-400 mt-1">Digite o CEP para buscar automaticamente</p>
          </div>

          <div>
            <label class="label">Bairro</label>
            <input
              v-model="form.bairro"
              type="text"
              class="input"
            />
          </div>

          <div class="md:col-span-2">
            <label class="label">Logradouro</label>
            <input
              v-model="form.logradouro"
              type="text"
              class="input"
            />
          </div>

          <div>
            <label class="label">Número</label>
            <input
              v-model="form.numero"
              type="text"
              class="input"
            />
          </div>

          <div>
            <label class="label">Complemento</label>
            <input
              v-model="form.complemento"
              type="text"
              class="input"
            />
          </div>

          <div>
            <label class="label">Cidade</label>
            <input
              v-model="form.cidade"
              type="text"
              class="input"
            />
          </div>

          <div>
            <label class="label">Estado</label>
            <input
              v-model="form.estado"
              type="text"
              class="input"
              maxlength="2"
              placeholder="SP"
            />
          </div>
        </div>
      </div>

      <!-- Observações -->
      <div>
        <label class="label">Observações</label>
        <textarea
          v-model="form.observacoes"
          rows="3"
          class="input"
          placeholder="Notas adicionais sobre o cidadão..."
        ></textarea>
      </div>

      <!-- Anexos (após cadastro) -->
      <div v-if="cidadao?.id" class="border-t border-gray-200 dark:border-slate-700 pt-4">
        <h4 class="text-sm font-semibold text-gray-900 dark:text-slate-100 mb-3">
          Arquivos do cidadão
        </h4>
        <DocumentosUpload
          :cidadao-id="cidadao.id"
          :pode-editar="podeEditarDocumentos"
        />
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
        {{ loading ? 'Salvando...' : 'Salvar' }}
      </Button>
    </template>
  </Modal>

  <!-- Avatar Cropper Modal -->
  <AvatarCropper
    v-model="mostrarCropper"
    :image-url="avatarOriginal || ''"
    @crop="handleCrop"
  />
</template>
