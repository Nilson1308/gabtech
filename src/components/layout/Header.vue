<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTheme } from '@/composables/useTheme'
import Avatar from '@/components/common/Avatar.vue'
import { Menu, Settings, Sun, Moon, User, LogOut, ChevronDown } from 'lucide-vue-next'

const emit = defineEmits<{
  toggleSidebar: []
}>()

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { isDark, toggleTheme } = useTheme()

const mostrarDropdown = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

const tituloPagina = computed(() => {
  for (let i = route.matched.length - 1; i >= 0; i--) {
    const title = route.matched[i].meta.headerTitle
    if (typeof title === 'string' && title.trim()) {
      return title
    }
  }
  return 'GabTech'
})

const irParaConfiguracoes = () => {
  router.push('/configuracoes')
}

const toggleDropdown = () => {
  mostrarDropdown.value = !mostrarDropdown.value
}

const irParaPerfil = () => {
  mostrarDropdown.value = false
  router.push('/perfil')
}

const sair = async () => {
  mostrarDropdown.value = false
  await authStore.logout()
  router.push('/login')
}

// Fechar dropdown ao clicar fora
const handleClickOutside = (event: MouseEvent) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    mostrarDropdown.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <header class="h-16 bg-white dark:bg-slate-800 border-b border-gray-200 dark:border-slate-700 flex items-center justify-between px-4 lg:px-6 z-30 transition-colors">
    <!-- Lado Esquerdo: Botão Mobile + Título -->
    <div class="flex items-center gap-4">
      <button
        @click="emit('toggleSidebar')"
        class="lg:hidden text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100 p-2 -ml-2"
        aria-label="Menu"
      >
        <Menu class="w-6 h-6" />
      </button>
      
      <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
        {{ tituloPagina }}
      </h2>
    </div>

    <!-- Lado Direito: Tema + Configurações + Perfil do Usuário -->
    <div v-if="authStore.usuario" class="flex items-center gap-2">
      <!-- Toggle Tema -->
      <button
        @click="toggleTheme"
        class="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
        :aria-label="isDark ? 'Ativar modo claro' : 'Ativar modo escuro'"
        :title="isDark ? 'Modo claro' : 'Modo escuro'"
      >
        <Sun v-if="isDark" class="w-5 h-5" />
        <Moon v-else class="w-5 h-5" />
      </button>

      <!-- Botão Configurações -->
      <button
        @click="irParaConfiguracoes"
        class="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
        aria-label="Configurações"
        title="Configurações"
      >
        <Settings class="w-5 h-5" />
      </button>

      <!-- Dropdown de Perfil -->
      <div class="relative" ref="dropdownRef">
        <button
          @click="toggleDropdown"
          class="flex items-center gap-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg p-2 transition-colors"
        >
          <!-- Info do Usuário (desktop) -->
          <div class="hidden sm:block text-right">
            <p class="text-sm font-medium text-gray-900 dark:text-gray-100">
              {{ authStore.usuario.nome }}
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              {{ authStore.usuario.cargo }}
            </p>
          </div>
          
          <Avatar 
            :nome="authStore.usuario.nome"
            :avatar="authStore.usuario.avatar"
            tamanho="md"
          />

          <ChevronDown 
            class="w-4 h-4 text-gray-500 dark:text-gray-400 transition-transform"
            :class="{ 'rotate-180': mostrarDropdown }"
          />
        </button>

        <!-- Menu Dropdown -->
        <Transition
          enter-active-class="transition ease-out duration-100"
          enter-from-class="transform opacity-0 scale-95"
          enter-to-class="transform opacity-100 scale-100"
          leave-active-class="transition ease-in duration-75"
          leave-from-class="transform opacity-100 scale-100"
          leave-to-class="transform opacity-0 scale-95"
        >
          <div
            v-if="mostrarDropdown"
            class="absolute right-0 mt-2 w-56 bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-gray-200 dark:border-slate-700 py-1 z-50"
          >
            <!-- Meu Perfil -->
            <button
              @click="irParaPerfil"
              class="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700 transition-colors"
            >
              <User class="w-4 h-4" />
              Meu Perfil
            </button>

            <div class="my-1 border-t border-gray-200 dark:border-slate-700"></div>

            <!-- Sair -->
            <button
              @click="sair"
              class="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
            >
              <LogOut class="w-4 h-4" />
              Sair
            </button>
          </div>
        </Transition>
      </div>
    </div>
  </header>
</template>
