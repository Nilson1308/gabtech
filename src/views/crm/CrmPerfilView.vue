<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCrmStore } from '@/stores/crm'
import { useAtendimentosStore } from '@/stores/atendimentos'
import type { Cidadao } from '@/types'
import Avatar from '@/components/common/Avatar.vue'
import Button from '@/components/common/Button.vue'
import CidadaoModal from '@/components/crm/CidadaoModal.vue'
import AtendimentosTimeline from '@/components/crm/AtendimentosTimeline.vue'
import DocumentosUpload from '@/components/crm/DocumentosUpload.vue'
import { ArrowLeft, Edit, Trash2, Phone, Mail, MapPin, FileText } from 'lucide-vue-next'
import RastreabilidadeMeta from '@/components/common/RastreabilidadeMeta.vue'
import { AUDITORIA_ALVO } from '@/services/auditoria'
import { useFormatters } from '@/composables/useFormatters'
import { useAuthStore } from '@/stores/auth'
import { PERMS } from '@/constants/rbac'

const route = useRoute()
const router = useRouter()
const crmStore = useCrmStore()
const atendimentosStore = useAtendimentosStore()
const authStore = useAuthStore()
const { formatDate } = useFormatters()

const podeEditarAnexos = computed(() => authStore.hasPermission(PERMS.crmEdit))

// Estado
const cidadao = ref<Cidadao | null>(null)
const loading = ref(true)
const mostrarModalEdicao = ref(false)
const confirmandoExclusao = ref(false)
const abaAtiva = ref<'atendimentos' | 'documentos'>('atendimentos')

// Atendimentos vinculados
const atendimentosVinculados = computed(() => {
  if (!cidadao.value) return []
  return atendimentosStore.atendimentos.filter(a => a.cidadaoId === cidadao.value!.id)
})

// Carregar dados
onMounted(async () => {
  const id = route.params.id as string
  
  await Promise.all([
    carregarCidadao(id),
    atendimentosStore.fetchAtendimentos()
  ])
  
  loading.value = false
})

const carregarCidadao = async (id: string) => {
  cidadao.value = await crmStore.getCidadaoById(id)
  
  if (!cidadao.value) {
    router.push('/crm')
  }
}

// Handlers
const voltar = () => {
  router.push('/crm')
}

const handleEditar = () => {
  mostrarModalEdicao.value = true
}

const handleSuccess = async () => {
  if (cidadao.value) {
    await carregarCidadao(cidadao.value.id)
  }
}

const handleExcluir = async () => {
  if (!cidadao.value) return
  
  if (!confirmandoExclusao.value) {
    confirmandoExclusao.value = true
    setTimeout(() => {
      confirmandoExclusao.value = false
    }, 3000)
    return
  }
  
  await crmStore.deleteCidadao(cidadao.value.id)
  router.push('/crm')
}

// Endereço completo formatado
const enderecoCompleto = computed(() => {
  if (!cidadao.value?.endereco) return null
  
  const { logradouro, numero, complemento, bairro, cidade, estado, cep } = cidadao.value.endereco
  
  let endereco = ''
  if (logradouro) endereco += logradouro
  if (numero) endereco += `, ${numero}`
  if (complemento) endereco += ` - ${complemento}`
  if (bairro) endereco += `\n${bairro}`
  if (cidade) endereco += ` - ${cidade}/${estado}`
  if (cep) endereco += `\nCEP: ${cep}`
  
  return endereco
})
</script>

<template>
  <div class="space-y-6">
    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>

    <!-- Conteúdo -->
    <template v-else-if="cidadao">
      <!-- Header -->
      <div class="flex items-center gap-4">
        <Button variant="ghost" @click="voltar" class="p-2">
          <ArrowLeft class="w-5 h-5" />
        </Button>
        <div>
          <h2 class="text-2xl font-bold text-gray-900 dark:text-slate-100">Perfil do Cidadão</h2>
          <RastreabilidadeMeta
            :rastreabilidade="cidadao.rastreabilidade"
            :alvo-auditoria="AUDITORIA_ALVO.cidadao(cidadao.id)"
            historico-titulo="Histórico do cidadão"
            show-criacao
            class="mt-1"
          />
          <p
            v-if="!cidadao.rastreabilidade?.ultimaAcaoEm && cidadao.createdAt"
            class="text-sm text-gray-600 dark:text-slate-400 mt-1"
          >
            Cadastrado em {{ formatDate(cidadao.createdAt) }}
          </p>
        </div>
      </div>

      <!-- Layout Split -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Lado Esquerdo: Card de Perfil -->
        <div class="lg:col-span-1">
          <div class="card sticky top-6">
            <!-- Avatar -->
            <div class="flex flex-col items-center mb-6">
              <Avatar :nome="cidadao.nome_social || cidadao.nome" tamanho="xl" class="mb-4" />
              <h3 class="text-xl font-bold text-gray-900 dark:text-slate-100 text-center">
                {{ cidadao.nome_social || cidadao.nome }}
              </h3>
              <p v-if="cidadao.nome_social" class="text-xs text-gray-500 dark:text-slate-400 mt-1">
                Nome civil: {{ cidadao.nome }}
              </p>
              <p v-if="cidadao.cpf" class="text-sm text-gray-600 dark:text-slate-400 mt-1">
                CPF: {{ cidadao.cpf }}
              </p>
            </div>

            <!-- Contato -->
            <div class="space-y-3 mb-6">
              <h4 class="text-xs font-semibold text-gray-500 dark:text-slate-400 uppercase tracking-wide">
                Contato
              </h4>
              
              <div class="flex items-center gap-3 text-sm text-gray-700 dark:text-slate-300">
                <Phone class="w-4 h-4 text-gray-400 dark:text-slate-500 flex-shrink-0" />
                <span>{{ cidadao.telefone }}</span>
              </div>

              <div v-if="cidadao.email" class="flex items-center gap-3 text-sm text-gray-700 dark:text-slate-300">
                <Mail class="w-4 h-4 text-gray-400 dark:text-slate-500 flex-shrink-0" />
                <span class="break-all">{{ cidadao.email }}</span>
              </div>
            </div>

            <!-- Endereço -->
            <div v-if="enderecoCompleto" class="space-y-3 mb-6">
              <h4 class="text-xs font-semibold text-gray-500 dark:text-slate-400 uppercase tracking-wide">
                Endereço
              </h4>
              <div class="flex items-start gap-3 text-sm text-gray-700 dark:text-slate-300">
                <MapPin class="w-4 h-4 text-gray-400 dark:text-slate-500 flex-shrink-0 mt-0.5" />
                <span class="whitespace-pre-line">{{ enderecoCompleto }}</span>
              </div>
            </div>

            <!-- Marcadores -->
            <div v-if="cidadao.tag_ids && cidadao.tag_ids.length > 0" class="space-y-3 mb-6">
              <h4 class="text-xs font-semibold text-gray-500 dark:text-slate-400 uppercase tracking-wide">
                Marcadores
              </h4>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="tagId in cidadao.tag_ids"
                  :key="tagId"
                  :style="{
                    backgroundColor: crmStore.tagsDisponiveis.find(t => t.id === tagId)?.cor + '20' || '#e5e7eb',
                    color: crmStore.tagsDisponiveis.find(t => t.id === tagId)?.cor || '#6b7280',
                    borderColor: crmStore.tagsDisponiveis.find(t => t.id === tagId)?.cor + '40' || '#d1d5db',
                  }"
                  class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border"
                >
                  {{ crmStore.tagsDisponiveis.find(t => t.id === tagId)?.nome }}
                </span>
              </div>
            </div>

            <!-- Perfis Profissionais -->
            <div v-if="cidadao.perfis_profissionais && cidadao.perfis_profissionais.length > 0" class="space-y-3 mb-6">
              <h4 class="text-xs font-semibold text-gray-500 dark:text-slate-400 uppercase tracking-wide">
                Perfis Profissionais
              </h4>
              <div class="space-y-3">
                <div
                  v-for="perfil in cidadao.perfis_profissionais"
                  :key="perfil.id"
                  class="p-3 rounded-lg border border-gray-200 dark:border-slate-700 bg-gray-50 dark:bg-slate-800/50"
                >
                  <div class="space-y-1">
                    <p class="text-sm font-medium text-gray-900 dark:text-slate-100">
                      {{ perfil.cargo }}
                    </p>
                    <p class="text-xs text-gray-600 dark:text-slate-400">
                      em {{ perfil.instituicao }}
                    </p>
                    <span
                      v-if="perfil.tag_id"
                      :style="{
                        backgroundColor: crmStore.tagsDisponiveis.find(t => t.id === perfil.tag_id)?.cor + '20' || '#e5e7eb',
                        color: crmStore.tagsDisponiveis.find(t => t.id === perfil.tag_id)?.cor || '#6b7280',
                        borderColor: crmStore.tagsDisponiveis.find(t => t.id === perfil.tag_id)?.cor + '40' || '#d1d5db'
                      }"
                      class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border mt-1"
                    >
                      {{ crmStore.tagsDisponiveis.find(t => t.id === perfil.tag_id)?.nome || 'Sem Tag' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Observações -->
            <div v-if="cidadao && cidadao.observacoes" class="space-y-3 mb-6">
              <h4 class="text-xs font-semibold text-gray-500 dark:text-slate-400 uppercase tracking-wide">
                Observações
              </h4>
              <div class="flex items-start gap-3 text-sm text-gray-700 dark:text-slate-300">
                <FileText class="w-4 h-4 text-gray-400 dark:text-slate-500 flex-shrink-0 mt-0.5" />
                <span>{{ cidadao.observacoes }}</span>
              </div>
            </div>

            <!-- Ações -->
            <div class="flex flex-col gap-2 pt-4 border-t border-gray-200 dark:border-slate-700">
              <Button
                v-permission="PERMS.crmEdit"
                variant="primary"
                @click="handleEditar"
                full-width
              >
                <Edit class="w-4 h-4" />
                Editar Perfil
              </Button>

              <Button
                v-permission="PERMS.crmDelete"
                :variant="confirmandoExclusao ? 'danger' : 'ghost'"
                @click="handleExcluir"
                full-width
              >
                <Trash2 class="w-4 h-4" />
                {{ confirmandoExclusao ? 'Confirmar Exclusão' : 'Excluir Cidadão' }}
              </Button>
            </div>
          </div>
        </div>

        <!-- Lado Direito: Tabs -->
        <div class="lg:col-span-2">
          <div class="card">
            <!-- Tabs Header -->
            <div class="border-b border-gray-200 dark:border-slate-700 mb-6">
              <nav class="flex gap-4" aria-label="Tabs">
                <button
                  @click="abaAtiva = 'atendimentos'"
                  :class="[
                    abaAtiva === 'atendimentos'
                      ? 'border-primary-600 text-primary-600 dark:text-primary-400'
                      : 'border-transparent text-gray-600 dark:text-slate-400 hover:text-gray-900 dark:hover:text-slate-200 hover:border-gray-300 dark:hover:border-slate-600',
                    'border-b-2 py-2 px-1 font-medium text-sm transition-colors'
                  ]"
                >
                  Atendimentos ({{ atendimentosVinculados.length }})
                </button>
                <button
                  @click="abaAtiva = 'documentos'"
                  :class="[
                    abaAtiva === 'documentos'
                      ? 'border-primary-600 text-primary-600 dark:text-primary-400'
                      : 'border-transparent text-gray-600 dark:text-slate-400 hover:text-gray-900 dark:hover:text-slate-200 hover:border-gray-300 dark:hover:border-slate-600',
                    'border-b-2 py-2 px-1 font-medium text-sm transition-colors'
                  ]"
                >
                  Documentos
                </button>
              </nav>
            </div>

            <!-- Tab: Atendimentos -->
            <div v-if="abaAtiva === 'atendimentos'">
              <div class="mb-4">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-slate-100">
                  Histórico de Atendimentos
                </h3>
                <p class="text-sm text-gray-600 dark:text-slate-400 mt-1">
                  {{ atendimentosVinculados.length }} {{ atendimentosVinculados.length === 1 ? 'atendimento vinculado' : 'atendimentos vinculados' }}
                </p>
              </div>
              <AtendimentosTimeline :atendimentos="atendimentosVinculados" />
            </div>

            <!-- Tab: Documentos -->
            <div v-else-if="abaAtiva === 'documentos'">
              <div class="mb-4">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-slate-100">
                  Documentos e Anexos
                </h3>
                <p class="text-sm text-gray-600 dark:text-slate-400 mt-1">
                  Faça upload de documentos do cidadão (RG, comprovantes, currículos, etc.)
                </p>
              </div>
              <DocumentosUpload
                v-if="cidadao"
                :cidadao-id="cidadao.id"
                :pode-editar="podeEditarAnexos"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Modal de Edição -->
      <CidadaoModal
        v-model="mostrarModalEdicao"
        :cidadao="cidadao"
        @success="handleSuccess"
      />
    </template>
  </div>
</template>
