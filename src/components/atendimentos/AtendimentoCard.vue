<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { PERMS } from '@/constants/rbac'
import type { Atendimento } from '@/types'
import Avatar from '@/components/common/Avatar.vue'
import RastreabilidadeMeta from '@/components/common/RastreabilidadeMeta.vue'
import { AUDITORIA_ALVO } from '@/services/auditoria'
import { AlertCircle, User, MoreVertical, Trash2, Pencil } from 'lucide-vue-next'

interface Props {
  atendimento: Atendimento
}

const props = defineProps<Props>()
const emit = defineEmits<{
  delete: [id: string]
  edit: [id: string]
}>()

const router = useRouter()
const authStore = useAuthStore()
const mostrarMenu = ref(false)

const statusAberto = computed(() => props.atendimento.status === 'aberto')

const podeEditar = computed(
  () => authStore.hasPermission(PERMS.atendEdit) && statusAberto.value,
)

const podeExcluir = computed(
  () => authStore.hasPermission(PERMS.atendDelete) && statusAberto.value,
)

const mostrarMenuAcoes = computed(() => podeEditar.value || podeExcluir.value)

const verDetalhes = () => {
  router.push(`/atendimentos/${props.atendimento.id}`)
}

const verCidadao = (event: Event) => {
  event.stopPropagation()
  router.push(`/crm/${props.atendimento.cidadaoId}`)
}

const toggleMenu = (event: Event) => {
  event.stopPropagation()
  mostrarMenu.value = !mostrarMenu.value
}

const handleEditar = (event: Event) => {
  event.stopPropagation()
  mostrarMenu.value = false
  emit('edit', props.atendimento.id)
}

const handleExcluir = (event: Event) => {
  event.stopPropagation()
  mostrarMenu.value = false
  emit('delete', props.atendimento.id)
}
</script>

<template>
  <div
    @click="verDetalhes"
    class="bg-white dark:bg-slate-800 rounded-lg border-2 border-gray-200 dark:border-slate-700 p-4 hover:border-primary-300 dark:hover:border-primary-500 hover:shadow-md transition-all cursor-pointer group relative"
    :class="{ 'border-red-300 dark:border-red-500': atendimento.slaAtrasado }"
  >
    <!-- Protocolo e SLA -->
    <div class="flex items-start justify-between mb-2">
      <span class="text-xs font-mono text-gray-500 dark:text-slate-400">
        #{{ atendimento.protocolo }}
      </span>
      <div class="flex items-center gap-1">
        <AlertCircle 
          v-if="atendimento.slaAtrasado"
          class="w-4 h-4 text-red-600 dark:text-red-400"
          title="SLA Atrasado"
        />
        
        <!-- Menu Contextual -->
        <div v-if="mostrarMenuAcoes" class="relative">
          <button
            @click="toggleMenu"
            class="p-1 hover:bg-gray-100 dark:hover:bg-slate-700 rounded transition-colors opacity-0 group-hover:opacity-100"
          >
            <MoreVertical class="w-4 h-4 text-gray-600 dark:text-slate-400" />
          </button>

          <!-- Dropdown Menu -->
          <Transition
            enter-active-class="transition ease-out duration-100"
            enter-from-class="transform opacity-0 scale-95"
            enter-to-class="transform opacity-100 scale-100"
            leave-active-class="transition ease-in duration-75"
            leave-from-class="transform opacity-100 scale-100"
            leave-to-class="transform opacity-0 scale-95"
          >
            <div
              v-if="mostrarMenu"
              @click.stop
              class="absolute right-0 mt-1 w-40 bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-gray-200 dark:border-slate-700 py-1 z-10"
            >
              <button
                v-if="podeEditar"
                type="button"
                @click="handleEditar"
                class="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 dark:text-slate-200 hover:bg-gray-50 dark:hover:bg-slate-700 transition-colors"
              >
                <Pencil class="w-4 h-4" />
                Editar
              </button>
              <button
                v-if="podeExcluir"
                type="button"
                @click="handleExcluir"
                class="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
              >
                <Trash2 class="w-4 h-4" />
                Excluir
              </button>
            </div>
          </Transition>
        </div>
      </div>
    </div>

    <!-- Assunto -->
    <h4 class="font-semibold text-gray-900 dark:text-slate-100 mb-2 line-clamp-2 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
      {{ atendimento.assunto }}
    </h4>

    <!-- Cidadão -->
    <button
      @click="verCidadao"
      class="text-sm text-gray-600 dark:text-slate-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors mb-2 block"
    >
      {{ atendimento.cidadao.nome }}
    </button>

    <RastreabilidadeMeta
      :rastreabilidade="atendimento.rastreabilidade"
      :alvo-auditoria="AUDITORIA_ALVO.atendimento(atendimento.id)"
      historico-titulo="Histórico do atendimento"
      compact
      class="mb-3"
      @click.stop
    />

    <!-- Footer: Macrotema + Responsável -->
    <div class="flex items-center justify-between">
      <!-- Macrotema -->
      <span
        :style="{
          backgroundColor: atendimento.macrotema.cor + '20',
          color: atendimento.macrotema.cor
        }"
        class="inline-flex items-center px-2 py-1 rounded text-xs font-medium"
      >
        {{ atendimento.macrotema.nome }}
      </span>

      <!-- Responsável -->
      <div class="flex items-center gap-1" :title="atendimento.responsavel.nome">
        <Avatar 
          v-if="atendimento.responsavel"
          :nome="atendimento.responsavel.nome"
          tamanho="sm"
        />
        <User v-else class="w-6 h-6 text-gray-400" />
      </div>
    </div>
  </div>
</template>
