<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { CONFIG_SECTION_PERMS, PERMS } from '@/constants/rbac'
import { 
  LayoutDashboard, 
  Users, 
  Inbox,
  Calendar,
  FileText,
  Settings,
  LogOut, 
  ChevronLeft,
  ChevronRight,
  X,
  Sparkles,
  BookOpen,
  Info,
  MapPin,
  Briefcase,
} from 'lucide-vue-next'

interface Props {
  modelValue: boolean // Para controle mobile
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const collapsed = ref(false)

const menuItems = [
  {
    nome: 'Dashboard',
    rota: '/dashboard',
    icone: LayoutDashboard,
    permissionAny: [PERMS.dashboardOperacional, PERMS.dashboard],
  },
  {
    nome: 'CRM',
    rota: '/crm',
    icone: Users,
    permission: PERMS.crm
  },
  {
    nome: 'Atendimentos',
    rota: '/atendimentos',
    icone: Inbox,
    permission: PERMS.atendimentos
  },
  {
    nome: 'Serviços',
    rota: '/servicos',
    icone: Briefcase,
    permission: PERMS.servicos,
  },
  {
    nome: 'Agenda',
    rota: '/agenda',
    icone: Calendar,
    permission: PERMS.agenda
  },
  {
    nome: 'Documentos',
    rota: '/documentos',
    icone: FileText,
    permission: PERMS.docs
  },
  {
    nome: 'Eventos & Cerimonial',
    rota: '/eventos',
    icone: Sparkles,
    permission: PERMS.eventos
  },
  {
    nome: 'Inteligência Territorial',
    rota: '/mapa',
    icone: MapPin,
    permission: PERMS.mapa
  },
  {
    nome: 'Configurações',
    rota: '/configuracoes',
    icone: Settings,
    permissionAny: [...CONFIG_SECTION_PERMS],
  },
]

const menuItemsFiltrados = computed(() => {
  return menuItems.filter(item => {
    const any = (item as { permissionAny?: string[] }).permissionAny
    if (any?.length) {
      return any.some(p => authStore.hasPermission(p))
    }
    return !item.permission || authStore.hasPermission(item.permission)
  })
})

const isAtivo = (rota: string) => {
  return route.path.startsWith(rota)
}

const navegar = (rota: string) => {
  router.push(rota)
  // Fechar sidebar no mobile após navegação
  if (window.innerWidth < 1024) {
    emit('update:modelValue', false)
  }
}

const toggleCollapse = () => {
  collapsed.value = !collapsed.value
}

const logout = async () => {
  authStore.logout()
  router.push('/login')
}

const fecharMobile = () => {
  emit('update:modelValue', false)
}
</script>

<template>
  <!-- Overlay Mobile -->
  <Transition
    enter-active-class="transition-opacity duration-300"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition-opacity duration-300"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div 
      v-if="modelValue"
      class="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
      @click="fecharMobile"
    />
  </Transition>

  <!-- Sidebar -->
  <aside 
    :class="[
      collapsed ? 'w-20' : 'w-64',
      modelValue ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
      'fixed lg:sticky inset-y-0 lg:top-0 left-0 z-50 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-all duration-300 flex flex-col h-screen lg:h-screen'
    ]"
  >
    <!-- Header da Sidebar -->
    <div class="h-16 flex items-center justify-between px-4 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
      <div v-if="!collapsed" class="flex items-center gap-2">
        <img 
          src="/logo_gt_tema_claro.png" 
          alt="GabTech" 
          class="h-8 w-auto dark:hidden"
        />
        <img 
          src="/logo_gt_tema_escuro.png" 
          alt="GabTech" 
          class="h-8 w-auto hidden dark:block"
        />
      </div>
      
      <div v-else class="flex items-center justify-center w-full">
        <img
          src="/favicon.png"
          alt="GabTech"
          class="h-9 w-9 object-contain"
        />
      </div>

      <!-- Botão de fechar (mobile) -->
      <button 
        @click="fecharMobile"
        class="lg:hidden text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300"
        aria-label="Fechar menu"
      >
        <X class="w-5 h-5" />
      </button>
    </div>

      <!-- Menu de Navegação -->
      <nav class="flex-1 px-3 py-4 space-y-1 overflow-y-auto min-h-0">
        <button
          v-for="item in menuItemsFiltrados"
          :key="item.rota"
          @click="navegar(item.rota)"
          :class="[
            isAtivo(item.rota)
              ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400 font-medium'
              : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700',
            collapsed ? 'justify-center' : 'justify-start',
            'w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors'
          ]"
          :title="collapsed ? item.nome : undefined"
          :aria-label="item.nome"
        >
          <component :is="item.icone" class="w-5 h-5 flex-shrink-0" />
          <span v-if="!collapsed" class="text-sm">{{ item.nome }}</span>
        </button>
      </nav>

      <!-- Footer da Sidebar -->
      <div class="border-t border-gray-200 dark:border-gray-700 p-3 space-y-1 flex-shrink-0">
        <!-- Links de Suporte -->
        <div class="space-y-1 pb-2 mb-2 border-b border-gray-200 dark:border-gray-700">
          <!-- Manual -->
          <button
            @click="navegar('/manual')"
            :class="[
              isAtivo('/manual')
                ? 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-700/50',
              collapsed ? 'justify-center' : 'justify-start',
              'w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors'
            ]"
            :title="collapsed ? 'Manual' : undefined"
            :aria-label="'Manual do Usuário'"
          >
            <BookOpen class="w-4 h-4 flex-shrink-0" />
            <span v-if="!collapsed" class="text-xs">Manual</span>
          </button>

          <!-- Sobre -->
          <button
            @click="navegar('/sobre')"
            :class="[
              isAtivo('/sobre')
                ? 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-50 dark:hover:bg-gray-700/50',
              collapsed ? 'justify-center' : 'justify-start',
              'w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors'
            ]"
            :title="collapsed ? 'Sobre' : undefined"
            :aria-label="'Sobre o GabTech'"
          >
            <Info class="w-4 h-4 flex-shrink-0" />
            <span v-if="!collapsed" class="text-xs">Sobre</span>
          </button>
        </div>

        <!-- Botão de Collapse (Desktop) -->
        <button
          @click="toggleCollapse"
          :class="[
            collapsed ? 'justify-center' : 'justify-between',
            'hidden lg:flex w-full items-center px-3 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors'
          ]"
          :title="collapsed ? (collapsed ? 'Expandir' : 'Recolher') : undefined"
          :aria-label="collapsed ? 'Expandir sidebar' : 'Recolher sidebar'"
        >
          <span v-if="!collapsed" class="text-sm">Recolher</span>
          <ChevronLeft v-if="!collapsed" class="w-4 h-4" />
          <ChevronRight v-else class="w-4 h-4" />
        </button>

        <!-- Botão de Logout -->
        <button
          @click="logout"
          :class="[
            collapsed ? 'justify-center' : 'justify-start',
            'w-full flex items-center gap-3 px-3 py-2.5 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors'
          ]"
          :title="collapsed ? 'Sair' : undefined"
          aria-label="Sair do sistema"
        >
          <LogOut class="w-5 h-5 flex-shrink-0" />
          <span v-if="!collapsed" class="text-sm font-medium">Sair</span>
        </button>
      </div>
    </aside>
</template>
