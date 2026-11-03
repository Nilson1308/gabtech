<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { Loader2, AlertCircle, ImagePlus, Trash2 } from 'lucide-vue-next'
import { criarCadastroGabinete } from '@/services/platform'
import { ApiError } from '@/services/api'
import LogoIdentidadeCropper from '@/components/public/LogoIdentidadeCropper.vue'
import { logoPreviewStyle, type LogoFormato } from '@/constants/logoIdentidade'

const router = useRouter()

const domainSuffix = (import.meta.env.VITE_TENANT_DOMAIN_SUFFIX as string | undefined)?.trim() || 'localhost'
const exigeConvite = Boolean((import.meta.env.VITE_SIGNUP_CODIGO_CONVITE as string | undefined)?.trim())

const darkMode = ref(false)

const form = ref({
  nome_gabinete: '',
  slug: '',
  admin_nome: '',
  admin_email: '',
  admin_senha: '',
  admin_senha_confirmacao: '',
  aceite_termos: false,
  codigo_convite: '',
})

const logoDataUrl = ref<string | null>(null)
const logoFormato = ref<LogoFormato>('1:1')
const logoPreviewBoxStyle = computed(() => logoPreviewStyle(logoFormato.value))
const logoOrigemUrl = ref('')
const mostrarCropper = ref(false)
const inputLogoRef = ref<HTMLInputElement | null>(null)

const loading = ref(false)
const erro = ref<string | null>(null)

const dominioPreview = computed(() => {
  const slug = form.value.slug.trim().toLowerCase() || 'seu-gabinete'
  return domainSuffix ? `${slug}.${domainSuffix}` : slug
})

onMounted(() => {
  darkMode.value = document.documentElement.classList.contains('dark')
})

function slugify() {
  form.value.slug = form.value.slug
    .toLowerCase()
    .replace(/[^a-z0-9-]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

function abrirSeletorLogo() {
  inputLogoRef.value?.click()
}

function onArquivoLogo(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (!file.type.startsWith('image/')) {
    erro.value = 'Selecione um arquivo de imagem (PNG, JPG ou WebP).'
    input.value = ''
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    erro.value = 'Arquivo muito grande. Use uma imagem de até 5 MB antes do recorte.'
    input.value = ''
    return
  }
  erro.value = null
  const reader = new FileReader()
  reader.onload = () => {
    logoOrigemUrl.value = String(reader.result)
    mostrarCropper.value = true
  }
  reader.readAsDataURL(file)
  input.value = ''
}

function onLogoCropado(payload: { dataUrl: string; formato: LogoFormato }) {
  logoDataUrl.value = payload.dataUrl
  logoFormato.value = payload.formato
}

function removerLogo() {
  logoDataUrl.value = null
  logoFormato.value = '1:1'
  logoOrigemUrl.value = ''
}

async function enviar() {
  erro.value = null
  loading.value = true
  try {
    slugify()
    const res = await criarCadastroGabinete({
      ...form.value,
      slug: form.value.slug,
      logo: logoDataUrl.value || undefined,
      logo_formato: logoDataUrl.value ? logoFormato.value : undefined,
    })
    await router.push({ name: 'CadastroGabineteStatus', params: { id: res.id } })
  } catch (e) {
    erro.value = e instanceof ApiError ? e.message : 'Não foi possível iniciar o cadastro.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-slate-900 py-10 px-4">
    <div class="max-w-xl mx-auto">
      <div class="text-center mb-8">
        <img
          :src="darkMode ? '/logo_gt_tema_escuro_completo.png' : '/logo_gt_tema_claro_completo.png'"
          alt="GabTech"
          class="h-11 w-auto mx-auto mb-5"
        >
        <h1 class="text-2xl font-bold text-gray-900 dark:text-slate-100">
          Criar seu gabinete
        </h1>
        <p class="text-sm text-gray-600 dark:text-slate-400 mt-2">
          Ambiente isolado na plataforma GabTech. Provisionamento automático em poucos minutos.
        </p>
      </div>

      <form
        class="card p-6 space-y-4"
        @submit.prevent="enviar"
      >
        <div v-if="erro" class="p-3 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 text-sm flex gap-2">
          <AlertCircle class="w-5 h-5 shrink-0" />
          <span>{{ erro }}</span>
        </div>

        <div>
          <label class="label">Identidade visual (logo ou brasão)</label>
          <p class="text-xs text-gray-500 dark:text-slate-400 mb-3">
            Opcional. Escolha quadrado (1:1), vertical (1:3) ou horizontal (3:1) no recorte.
          </p>
          <div class="flex items-center gap-4">
            <div
              class="rounded-xl border-2 border-dashed border-gray-300 dark:border-slate-600 flex items-center justify-center overflow-hidden bg-white dark:bg-slate-800 shrink-0"
              :style="logoPreviewBoxStyle"
            >
              <img
                v-if="logoDataUrl"
                :src="logoDataUrl"
                alt="Logo do gabinete"
                class="w-full h-full object-contain p-1"
              >
              <ImagePlus v-else class="w-8 h-8 text-gray-400 dark:text-slate-500" />
            </div>
            <div class="flex flex-col gap-2">
              <button
                type="button"
                class="btn btn-secondary text-sm"
                @click="abrirSeletorLogo"
              >
                {{ logoDataUrl ? 'Trocar imagem' : 'Enviar imagem' }}
              </button>
              <button
                v-if="logoDataUrl"
                type="button"
                class="text-sm text-red-600 dark:text-red-400 inline-flex items-center gap-1"
                @click="removerLogo"
              >
                <Trash2 class="w-4 h-4" />
                Remover
              </button>
            </div>
          </div>
          <input
            ref="inputLogoRef"
            type="file"
            accept="image/png,image/jpeg,image/webp,image/gif"
            class="hidden"
            @change="onArquivoLogo"
          >
        </div>

        <div>
          <label class="label">Nome do gabinete / mandato</label>
          <input v-model="form.nome_gabinete" class="input" required maxlength="200">
        </div>

        <div>
          <label class="label">Identificador (URL)</label>
          <input
            v-model="form.slug"
            class="input"
            required
            minlength="3"
            maxlength="50"
            pattern="[a-z0-9\\-]+"
            placeholder="ex: vereador-silva"
            @blur="slugify"
          >
          <p class="text-xs text-gray-500 dark:text-slate-400 mt-1">
            Endereço: <strong>{{ dominioPreview }}</strong>
          </p>
        </div>

        <div>
          <label class="label">Seu nome (administrador)</label>
          <input v-model="form.admin_nome" class="input" required maxlength="300">
        </div>

        <div>
          <label class="label">E-mail de acesso</label>
          <input v-model="form.admin_email" type="email" class="input" required>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="label">Senha</label>
            <input v-model="form.admin_senha" type="password" class="input" required minlength="8">
          </div>
          <div>
            <label class="label">Confirmar senha</label>
            <input v-model="form.admin_senha_confirmacao" type="password" class="input" required minlength="8">
          </div>
        </div>

        <div v-if="exigeConvite">
          <label class="label">Código de convite</label>
          <input v-model="form.codigo_convite" class="input" required>
        </div>

        <label class="flex items-start gap-2 text-sm text-gray-700 dark:text-slate-300">
          <input v-model="form.aceite_termos" type="checkbox" class="mt-1" required>
          <span>
            Li e aceito os
            <RouterLink to="/privacidade" class="text-primary-600 dark:text-primary-400 underline">
              termos e a política de privacidade
            </RouterLink>.
          </span>
        </label>

        <button type="submit" class="btn btn-primary w-full flex items-center justify-center gap-2" :disabled="loading">
          <Loader2 v-if="loading" class="w-4 h-4 animate-spin" />
          Criar gabinete
        </button>

        <p class="text-center text-sm text-gray-600 dark:text-slate-400">
          Já tem acesso?
          <RouterLink to="/login" class="text-primary-600 dark:text-primary-400 font-medium">
            Entrar
          </RouterLink>
        </p>
      </form>
    </div>

    <LogoIdentidadeCropper
      v-if="logoOrigemUrl"
      v-model="mostrarCropper"
      :image-url="logoOrigemUrl"
      :formato-inicial="logoFormato"
      @crop="onLogoCropado"
    />
  </div>
</template>
