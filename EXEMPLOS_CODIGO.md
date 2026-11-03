# Exemplos de Código - Templates Reutilizáveis

## 🧩 Estrutura Básica de Componente

```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { MinhaInterface } from '@/types'

// Props (se necessário)
interface Props {
  titulo?: string
  dados: MinhaInterface[]
}

const props = withDefaults(defineProps<Props>(), {
  titulo: 'Título Padrão'
})

// Emits (se necessário)
const emit = defineEmits<{
  salvar: [dados: MinhaInterface]
  cancelar: []
}>()

// State local
const loading = ref(false)
const erro = ref<string | null>(null)

// Computed
const dadosProcessados = computed(() => {
  return props.dados.filter(/* ... */)
})

// Methods
const handleSalvar = () => {
  emit('salvar', /* dados */)
}

// Lifecycle
onMounted(() => {
  // Inicialização
})
</script>

<template>
  <div class="component-container">
    <!-- Template aqui -->
  </div>
</template>
```

---

## 🎴 Card de Métrica (Dashboard)

```vue
<script setup lang="ts">
import { TrendingUp, TrendingDown } from 'lucide-vue-next'

interface Props {
  label: string
  valor: string | number
  icone: any // Componente do Lucide
  cor?: string
  variacao?: {
    valor: number
    tipo: 'aumento' | 'reducao'
  }
}

const props = withDefaults(defineProps<Props>(), {
  cor: 'blue'
})

const corClasses = {
  blue: 'bg-blue-100 text-blue-600',
  green: 'bg-green-100 text-green-600',
  red: 'bg-red-100 text-red-600',
  yellow: 'bg-yellow-100 text-yellow-600',
}
</script>

<template>
  <div class="card">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm text-gray-600 mb-1">{{ label }}</p>
        <p class="text-3xl font-bold text-gray-900">{{ valor }}</p>
        
        <div v-if="variacao" class="flex items-center gap-1 mt-2">
          <TrendingUp v-if="variacao.tipo === 'aumento'" class="w-4 h-4 text-green-600" />
          <TrendingDown v-else class="w-4 h-4 text-red-600" />
          <span 
            class="text-sm font-medium"
            :class="variacao.tipo === 'aumento' ? 'text-green-600' : 'text-red-600'"
          >
            {{ variacao.valor }}%
          </span>
        </div>
      </div>
      
      <div :class="corClasses[cor]" class="w-12 h-12 rounded-lg flex items-center justify-center">
        <component :is="icone" class="w-6 h-6" />
      </div>
    </div>
  </div>
</template>
```

---

## 📋 Tabela de Dados com Paginação

```vue
<script setup lang="ts">
import { ref } from 'vue'
import type { Cidadao, PaginationMeta } from '@/types'
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'

interface Props {
  dados: Cidadao[]
  meta: PaginationMeta
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

const emit = defineEmits<{
  pageChange: [page: number]
  edit: [id: string]
  delete: [id: string]
}>()
</script>

<template>
  <div class="card">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>
    
    <!-- Tabela -->
    <div v-else class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Nome
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Telefone
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Bairro
            </th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
              Ações
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="item in dados" :key="item.id" class="hover:bg-gray-50">
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm font-medium text-gray-900">{{ item.nome }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm text-gray-500">{{ item.telefone }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm text-gray-500">{{ item.bairro }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <button @click="emit('edit', item.id)" class="text-primary-600 hover:text-primary-900 mr-4">
                Editar
              </button>
              <button @click="emit('delete', item.id)" class="text-red-600 hover:text-red-900">
                Excluir
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Paginação -->
    <div class="flex items-center justify-between px-6 py-4 border-t border-gray-200">
      <div class="text-sm text-gray-700">
        Mostrando {{ ((meta.currentPage - 1) * meta.perPage) + 1 }} 
        a {{ Math.min(meta.currentPage * meta.perPage, meta.totalItems) }} 
        de {{ meta.totalItems }} resultados
      </div>
      
      <div class="flex gap-2">
        <button
          @click="emit('pageChange', meta.currentPage - 1)"
          :disabled="meta.currentPage === 1"
          class="btn btn-secondary disabled:opacity-50"
        >
          <ChevronLeft class="w-4 h-4" />
        </button>
        
        <span class="px-4 py-2 text-sm font-medium text-gray-700">
          {{ meta.currentPage }} / {{ meta.totalPages }}
        </span>
        
        <button
          @click="emit('pageChange', meta.currentPage + 1)"
          :disabled="meta.currentPage === meta.totalPages"
          class="btn btn-secondary disabled:opacity-50"
        >
          <ChevronRight class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>
```

---

## 🪟 Modal Base Reutilizável

```vue
<script setup lang="ts">
import { X } from 'lucide-vue-next'

interface Props {
  modelValue: boolean
  titulo: string
  largura?: 'sm' | 'md' | 'lg' | 'xl'
}

const props = withDefaults(defineProps<Props>(), {
  largura: 'md'
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const fechar = () => {
  emit('update:modelValue', false)
}

const larguraClasses = {
  sm: 'max-w-md',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
  xl: 'max-w-4xl',
}
</script>

<template>
  <Teleport to="body">
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
        class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
        @click.self="fechar"
      >
        <div 
          :class="larguraClasses[largura]"
          class="bg-white rounded-lg shadow-xl w-full overflow-hidden"
        >
          <!-- Header -->
          <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-semibold text-gray-900">{{ titulo }}</h3>
            <button 
              @click="fechar"
              class="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X class="w-5 h-5" />
            </button>
          </div>
          
          <!-- Body -->
          <div class="px-6 py-4">
            <slot />
          </div>
          
          <!-- Footer (opcional) -->
          <div v-if="$slots.footer" class="px-6 py-4 border-t border-gray-200 bg-gray-50">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
```

**Uso:**
```vue
<Modal v-model="mostrarModal" titulo="Novo Contato" largura="lg">
  <!-- Conteúdo do modal -->
  <form>...</form>
  
  <!-- Footer com botões -->
  <template #footer>
    <div class="flex justify-end gap-2">
      <button @click="mostrarModal = false" class="btn btn-secondary">
        Cancelar
      </button>
      <button @click="salvar" class="btn btn-primary">
        Salvar
      </button>
    </div>
  </template>
</Modal>
```

---

## 🏷️ Badge/Tag Colorido

```vue
<script setup lang="ts">
interface Props {
  label: string
  cor?: string
  removivel?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  cor: '#3b82f6',
  removivel: false
})

const emit = defineEmits<{
  remove: []
}>()

// Gerar classes de cor dinâmicas
const estilos = computed(() => ({
  backgroundColor: props.cor + '20', // 20 = 12% opacity
  color: props.cor,
  borderColor: props.cor + '40',
}))
</script>

<template>
  <span 
    :style="estilos"
    class="inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full border"
  >
    {{ label }}
    <button 
      v-if="removivel"
      @click="emit('remove')"
      class="hover:opacity-70"
    >
      <X class="w-3 h-3" />
    </button>
  </span>
</template>
```

---

## 👤 Avatar com Iniciais

```vue
<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  nome: string
  avatar?: string
  tamanho?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  tamanho: 'md'
})

const iniciais = computed(() => {
  return props.nome
    .split(' ')
    .map(palavra => palavra[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
})

const tamanhoClasses = {
  sm: 'w-8 h-8 text-xs',
  md: 'w-10 h-10 text-sm',
  lg: 'w-12 h-12 text-base',
}
</script>

<template>
  <div 
    v-if="avatar"
    :class="tamanhoClasses[tamanho]"
    class="rounded-full overflow-hidden"
  >
    <img :src="avatar" :alt="nome" class="w-full h-full object-cover" />
  </div>
  
  <div 
    v-else
    :class="tamanhoClasses[tamanho]"
    class="rounded-full bg-primary-600 text-white flex items-center justify-center font-semibold"
  >
    {{ iniciais }}
  </div>
</template>
```

---

## 📅 Timeline de Eventos

```vue
<script setup lang="ts">
import type { Despacho } from '@/types'
import { useFormatters } from '@/composables/useFormatters'

interface Props {
  eventos: Despacho[]
}

const props = defineProps<Props>()
const { formatRelativeTime } = useFormatters()

const tipoIcone = (tipo: string) => {
  switch (tipo) {
    case 'nota_interna': return 'MessageCircle'
    case 'nota_publica': return 'MessageSquare'
    case 'mudanca_status': return 'RefreshCw'
    case 'reatribuicao': return 'UserCheck'
    default: return 'Circle'
  }
}
</script>

<template>
  <div class="space-y-4">
    <div 
      v-for="evento in eventos" 
      :key="evento.id"
      class="flex gap-3"
    >
      <!-- Linha vertical -->
      <div class="flex flex-col items-center">
        <div class="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
          <component :is="tipoIcone(evento.tipo)" class="w-4 h-4 text-primary-600" />
        </div>
        <div class="w-0.5 flex-1 bg-gray-200 mt-2"></div>
      </div>
      
      <!-- Conteúdo -->
      <div class="flex-1 pb-8">
        <div class="flex items-start justify-between mb-1">
          <p class="font-medium text-gray-900">{{ evento.autor.nome }}</p>
          <span class="text-xs text-gray-500">
            {{ formatRelativeTime(evento.createdAt) }}
          </span>
        </div>
        <p class="text-sm text-gray-600">{{ evento.conteudo }}</p>
      </div>
    </div>
  </div>
</template>
```

---

## 🔍 Barra de Pesquisa

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { Search, X } from 'lucide-vue-next'

const emit = defineEmits<{
  search: [query: string]
}>()

const query = ref('')

const limpar = () => {
  query.value = ''
  emit('search', '')
}

const pesquisar = () => {
  emit('search', query.value)
}
</script>

<template>
  <div class="relative">
    <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
    <input 
      v-model="query"
      @input="pesquisar"
      type="text"
      placeholder="Buscar..."
      class="input pl-10 pr-10"
    />
    <button 
      v-if="query"
      @click="limpar"
      class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
    >
      <X class="w-5 h-5" />
    </button>
  </div>
</template>
```

---

## 📊 Gráfico de Barras Simples (CSS puro)

```vue
<script setup lang="ts">
import type { DadosGraficoMacrotema } from '@/types'

interface Props {
  dados: DadosGraficoMacrotema[]
}

const props = defineProps<Props>()

const maxValor = computed(() => {
  return Math.max(...props.dados.map(d => d.quantidade))
})
</script>

<template>
  <div class="space-y-3">
    <div 
      v-for="item in dados" 
      :key="item.macrotema"
      class="flex items-center gap-3"
    >
      <div class="w-32 text-sm text-gray-700 font-medium">
        {{ item.macrotema }}
      </div>
      
      <div class="flex-1 bg-gray-100 rounded-full h-8 relative overflow-hidden">
        <div 
          :style="{ 
            width: `${(item.quantidade / maxValor) * 100}%`,
            backgroundColor: item.cor
          }"
          class="h-full rounded-full transition-all duration-500 flex items-center justify-end pr-3"
        >
          <span class="text-xs font-semibold text-white">
            {{ item.quantidade }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
```

---

## 🎯 Estado Vazio

```vue
<script setup lang="ts">
import { Inbox } from 'lucide-vue-next'

interface Props {
  titulo: string
  descricao?: string
  icone?: any
  acaoPrimaria?: {
    label: string
    onClick: () => void
  }
}

const props = withDefaults(defineProps<Props>(), {
  icone: Inbox
})
</script>

<template>
  <div class="flex flex-col items-center justify-center py-12 px-4">
    <component :is="icone" class="w-16 h-16 text-gray-300 mb-4" />
    <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ titulo }}</h3>
    <p v-if="descricao" class="text-gray-500 text-center mb-6 max-w-sm">
      {{ descricao }}
    </p>
    <button 
      v-if="acaoPrimaria"
      @click="acaoPrimaria.onClick"
      class="btn btn-primary"
    >
      {{ acaoPrimaria.label }}
    </button>
  </div>
</template>
```

---

**Estes templates devem acelerar significativamente o desenvolvimento! 🚀**
