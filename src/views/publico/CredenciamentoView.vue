<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useCerimonialStore } from '@/stores/cerimonial'
import PublicBrandHeader from '@/components/public/PublicBrandHeader.vue'
import {
  DEFAULT_CREDENCIAMENTO_CONFIG,
  urlPoliticaPrivacidade,
} from '@/constants/credenciamento'
import { CheckCircle2, AlertCircle, Calendar, MapPin, Clock } from 'lucide-vue-next'

const route = useRoute()
const cerimonialStore = useCerimonialStore()

const eventoId = computed(() => route.params.id as string)
const evento = computed(
  () => cerimonialStore.eventoPublico ?? cerimonialStore.getEventoById(eventoId.value),
)

const configFormulario = computed(() => {
  const fromEvento = evento.value?.credenciamentoConfig
  return fromEvento ?? DEFAULT_CREDENCIAMENTO_CONFIG
})

const linkPolitica = computed(() =>
  urlPoliticaPrivacidade(configFormulario.value, eventoId.value),
)

const nome = ref('')
const dataNascimento = ref('')
const telefone = ref('')
const orgaoInstituicao = ref('')
const email = ref('')
const aceitouLgpd = ref(false)

const loading = ref(false)
const sucesso = ref(false)
const erro = ref('')

onMounted(async () => {
  try {
    await cerimonialStore.fetchEventoPublico(eventoId.value)
  } catch {
    erro.value = 'Evento não encontrado ou indisponível.'
  }
})

function formatarTelefone(value: string) {
  return value
    .replace(/\D/g, '')
    .replace(/(\d{2})(\d)/, '($1) $2')
    .replace(/(\d{5})(\d)/, '$1-$2')
    .replace(/(-\d{4})\d+?$/, '$1')
}

function handleTelefoneInput(event: Event) {
  const input = event.target as HTMLInputElement
  telefone.value = formatarTelefone(input.value)
}

function formatarData(data: string) {
  const d = new Date(data)
  return d.toLocaleDateString('pt-BR', { day: '2-digit', month: 'long', year: 'numeric' })
}

async function handleSubmit() {
  erro.value = ''

  if (!nome.value.trim() || !telefone.value || !aceitouLgpd.value) {
    erro.value = 'Preencha nome, telefone/WhatsApp e aceite o termo de privacidade.'
    return
  }

  const telefoneNumeros = telefone.value.replace(/\D/g, '')
  if (telefoneNumeros.length < 10) {
    erro.value = 'Telefone ou WhatsApp inválido.'
    return
  }

  if (
    configFormulario.value.mostrar_email &&
    email.value.trim() &&
    !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim())
  ) {
    erro.value = 'E-mail inválido.'
    return
  }

  loading.value = true

  try {
    await cerimonialStore.registrarCredenciamento(
      eventoId.value,
      {
        nome: nome.value.trim(),
        telefone: telefoneNumeros,
        email: configFormulario.value.mostrar_email
          ? email.value.trim() || undefined
          : undefined,
        data_nascimento: configFormulario.value.mostrar_data_nascimento
          ? dataNascimento.value || undefined
          : undefined,
        orgao_instituicao: configFormulario.value.mostrar_orgao_instituicao
          ? orgaoInstituicao.value.trim() || undefined
          : undefined,
        aceitou_lgpd: true,
      },
      { publico: true },
    )

    sucesso.value = true
  } catch (e: unknown) {
    erro.value = e instanceof Error ? e.message : 'Erro ao registrar credenciamento'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
    <div class="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm border-b border-gray-200 dark:border-gray-700 sticky top-0 z-10">
      <div class="max-w-4xl mx-auto px-4 py-4 flex justify-center">
        <PublicBrandHeader subtitle="Credenciamento de evento" />
      </div>
    </div>

    <div class="max-w-2xl mx-auto px-4 py-8 pb-16">
      <div v-if="sucesso" class="text-center space-y-6 animate-fade-in">
        <div class="inline-flex items-center justify-center w-24 h-24 bg-green-100 dark:bg-green-900/30 rounded-full">
          <CheckCircle2 class="w-14 h-14 text-green-600 dark:text-green-400" />
        </div>

        <div class="space-y-2">
          <h2 class="text-3xl font-bold text-gray-900 dark:text-white">
            Registo concluído!
          </h2>
          <p class="text-lg text-gray-600 dark:text-gray-300">
            Apresente o seu nome na receção do evento.
          </p>
        </div>

        <div class="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-6 space-y-3">
          <div class="flex items-center gap-3 text-gray-700 dark:text-gray-300">
            <Calendar class="w-5 h-5 text-blue-600 dark:text-blue-400" />
            <span class="font-medium">{{ evento ? formatarData(evento.data) : '' }}</span>
          </div>
          <div class="flex items-center gap-3 text-gray-700 dark:text-gray-300">
            <Clock class="w-5 h-5 text-blue-600 dark:text-blue-400" />
            <span class="font-medium">{{ evento?.horaInicio }} - {{ evento?.horaFim }}</span>
          </div>
          <div class="flex items-center gap-3 text-gray-700 dark:text-gray-300">
            <MapPin class="w-5 h-5 text-blue-600 dark:text-blue-400" />
            <span class="font-medium">{{ evento?.local }}</span>
          </div>
        </div>

        <p class="text-sm text-gray-500 dark:text-gray-400">
          Até breve!
        </p>
      </div>

      <div v-else class="space-y-6">
        <div v-if="evento" class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
          <div class="bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-8 text-white">
            <h2 class="text-2xl font-bold mb-2">{{ evento.titulo }}</h2>
            <div class="space-y-2 text-blue-50">
              <div class="flex items-center gap-2">
                <Calendar class="w-4 h-4" />
                <span class="text-sm">{{ formatarData(evento.data) }}</span>
              </div>
              <div class="flex items-center gap-2">
                <Clock class="w-4 h-4" />
                <span class="text-sm">{{ evento.horaInicio }} - {{ evento.horaFim }}</span>
              </div>
              <div class="flex items-center gap-2">
                <MapPin class="w-4 h-4" />
                <span class="text-sm">{{ evento.local }}</span>
              </div>
            </div>
          </div>

          <div class="p-6 space-y-6">
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Credenciamento público
              </h3>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                Informe seus dados para controle de acesso e comunicação sobre este evento.
                Não solicitamos CPF neste formulário.
              </p>
            </div>

            <div v-if="erro" class="flex items-start gap-3 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <AlertCircle class="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
              <p class="text-sm text-red-700 dark:text-red-300">{{ erro }}</p>
            </div>

            <form @submit.prevent="handleSubmit" class="space-y-5">
              <div>
                <label for="nome" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Nome completo *
                </label>
                <input
                  id="nome"
                  v-model="nome"
                  type="text"
                  required
                  placeholder="Seu nome completo"
                  class="w-full px-4 py-3 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-gray-900 dark:text-white"
                />
              </div>

              <div>
                <label for="telefone" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Telefone / WhatsApp *
                </label>
                <input
                  id="telefone"
                  :value="telefone"
                  @input="handleTelefoneInput"
                  type="tel"
                  required
                  placeholder="(00) 00000-0000"
                  maxlength="15"
                  class="w-full px-4 py-3 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-gray-900 dark:text-white"
                />
              </div>

              <div v-if="configFormulario.mostrar_email">
                <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  E-mail
                </label>
                <input
                  id="email"
                  v-model="email"
                  type="email"
                  placeholder="seu@email.com"
                  class="w-full px-4 py-3 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-gray-900 dark:text-white"
                />
              </div>

              <div v-if="configFormulario.mostrar_data_nascimento">
                <label for="nascimento" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Data de nascimento
                </label>
                <input
                  id="nascimento"
                  v-model="dataNascimento"
                  type="date"
                  class="w-full px-4 py-3 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-gray-900 dark:text-white"
                />
              </div>

              <div v-if="configFormulario.mostrar_orgao_instituicao">
                <label for="orgao" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Órgão / instituição
                </label>
                <input
                  id="orgao"
                  v-model="orgaoInstituicao"
                  type="text"
                  placeholder="Ex.: Secretaria Municipal de Saúde"
                  class="w-full px-4 py-3 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-gray-900 dark:text-white"
                />
              </div>

              <div class="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                <label class="flex items-start gap-3 cursor-pointer group">
                  <input
                    v-model="aceitouLgpd"
                    type="checkbox"
                    required
                    class="mt-1 w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 focus:ring-2 cursor-pointer"
                  />
                  <span class="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                    Li e concordo com o tratamento dos meus dados para
                    <strong>controle de acesso, presença e comunicação sobre este evento</strong>,
                    conforme a
                    <a
                      :href="linkPolitica"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="font-semibold text-blue-600 dark:text-blue-400 underline hover:no-underline"
                      @click.stop
                    >política de privacidade</a>.
                  </span>
                </label>
              </div>

              <button
                type="submit"
                :disabled="loading"
                class="w-full py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span v-if="loading">A processar...</span>
                <span v-else>Confirmar credenciamento</span>
              </button>
            </form>
          </div>
        </div>

        <div v-else class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-8 text-center">
          <AlertCircle class="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            Evento não encontrado
          </h3>
          <p class="text-gray-600 dark:text-gray-400">
            Verifique o link de credenciamento e tente novamente.
          </p>
        </div>
      </div>
    </div>

    <div class="fixed bottom-0 left-0 right-0 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm border-t border-gray-200 dark:border-gray-700 py-3">
      <p class="text-center text-xs text-gray-500 dark:text-gray-400">
        GabTech · credenciamento seguro
      </p>
    </div>
  </div>
</template>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.6s ease-out;
}
</style>
