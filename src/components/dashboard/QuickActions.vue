<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Plus, UserPlus, Inbox, Users } from 'lucide-vue-next'

const router = useRouter()

const acoes = [
  {
    label: 'Novo Atendimento',
    icone: Plus,
    cor: 'primary',
    rota: '/atendimentos',
    descricao: 'Registrar novo protocolo'
  },
  {
    label: 'Novo Cidadão',
    icone: UserPlus,
    cor: 'secondary',
    rota: '/crm',
    descricao: 'Adicionar contato ao CRM'
  }
]

const atalhos = [
  {
    label: 'Atendimentos',
    icone: Inbox,
    rota: '/atendimentos',
    cor: 'text-primary-600 bg-primary-50'
  },
  {
    label: 'CRM',
    icone: Users,
    rota: '/crm',
    cor: 'text-green-600 bg-green-50'
  }
]

const navegar = (rota: string) => {
  router.push(rota)
}
</script>

<template>
  <div class="card">
    <div class="mb-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-slate-100">
        Ações Rápidas
      </h3>
      <p class="text-sm text-gray-600 dark:text-slate-400 mt-1">
        Acesso direto às principais funcionalidades
      </p>
    </div>

    <!-- Botões de Ação Principal -->
    <div class="space-y-3 mb-6">
      <button
        v-for="acao in acoes"
        :key="acao.label"
        @click="navegar(acao.rota)"
        :class="[
          acao.cor === 'primary' ? 'bg-primary-600 hover:bg-primary-700 text-white' : 'bg-gray-100 hover:bg-gray-200 dark:bg-slate-700 dark:hover:bg-slate-600 text-gray-900 dark:text-slate-100',
          'w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors font-medium'
        ]"
      >
        <component :is="acao.icone" class="w-5 h-5" />
        <div class="flex-1 text-left">
          <div class="text-sm font-semibold">{{ acao.label }}</div>
          <div :class="acao.cor === 'primary' ? 'text-primary-100' : 'text-gray-600 dark:text-slate-400'" class="text-xs">
            {{ acao.descricao }}
          </div>
        </div>
      </button>
    </div>

    <!-- Atalhos -->
    <div class="pt-4 border-t border-gray-200 dark:border-slate-700">
      <p class="text-xs font-medium text-gray-500 dark:text-slate-400 uppercase tracking-wide mb-3">
        Atalhos
      </p>
      <div class="grid grid-cols-2 gap-2">
        <button
          v-for="atalho in atalhos"
          :key="atalho.label"
          @click="navegar(atalho.rota)"
          :class="[atalho.cor, 'p-3 rounded-lg hover:opacity-80 transition-opacity dark:brightness-90']"
        >
          <component :is="atalho.icone" class="w-5 h-5 mx-auto mb-1" />
          <div class="text-xs font-medium">{{ atalho.label }}</div>
        </button>
      </div>
    </div>
  </div>
</template>
