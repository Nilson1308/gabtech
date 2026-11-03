<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
const route = useRoute()

const abas = [
  { name: 'Servicos', to: '/servicos', label: 'Visão geral' },
  { name: 'BancoTalentos', to: '/servicos/talentos', label: 'Banco de Talentos' },
  { name: 'ServicosBeneficios', to: '/servicos/beneficios', label: 'Assistência Social' },
  { name: 'ServicosCursos', to: '/servicos/cursos', label: 'Cursos' },
] as const

const abaAtiva = computed(() => {
  const match = abas.find(a => a.name === route.name)
  return match?.name ?? 'Servicos'
})
</script>

<template>
  <div class="space-y-6">
    <header class="border-b border-gray-200 dark:border-slate-700 pb-4">
      <p class="text-sm text-gray-600 dark:text-slate-400 max-w-2xl">
        Talentos, benefícios e capacitação com matchmaking por tags do CRM.
      </p>

      <nav
        class="mt-3 flex flex-wrap gap-1 p-1 bg-gray-100 dark:bg-slate-800/80 rounded-lg w-full sm:w-auto"
        aria-label="Seções de serviços"
      >
        <RouterLink
          v-for="aba in abas"
          :key="aba.name"
          :to="aba.to"
          class="px-3 py-2 rounded-md text-sm font-medium transition-colors"
          :class="
            abaAtiva === aba.name
              ? 'bg-white dark:bg-slate-900 text-indigo-700 dark:text-indigo-300 shadow-sm'
              : 'text-gray-600 dark:text-slate-400 hover:text-gray-900 dark:hover:text-slate-200'
          "
        >
          {{ aba.label }}
        </RouterLink>
      </nav>
    </header>

    <RouterView />
  </div>
</template>
