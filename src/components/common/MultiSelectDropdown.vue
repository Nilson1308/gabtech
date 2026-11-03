<script setup lang="ts">
import { ref, computed } from 'vue'
import { onClickOutside } from '@vueuse/core'
import { ChevronDown, X, Check } from 'lucide-vue-next'

interface Option {
  id: string
  nome: string
}

interface Props {
  modelValue: string[]
  options: Option[]
  placeholder?: string
  label?: string
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Selecione...',
  label: 'itens'
})

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
}>()

// Estado
const isOpen = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)
const searchQuery = ref('')

// Fechar ao clicar fora
onClickOutside(dropdownRef, () => {
  isOpen.value = false
  searchQuery.value = ''
})

// Opções selecionadas
const selectedOptions = computed(() => {
  return props.options.filter(opt => props.modelValue.includes(opt.id))
})

// Opções filtradas pela busca
const filteredOptions = computed(() => {
  if (!searchQuery.value) return props.options
  
  const query = searchQuery.value.toLowerCase()
  return props.options.filter(opt => 
    opt.nome.toLowerCase().includes(query)
  )
})

// Texto do botão
const buttonText = computed(() => {
  if (props.modelValue.length === 0) return props.placeholder
  if (props.modelValue.length === 1) return selectedOptions.value[0]?.nome || ''
  return `${props.modelValue.length} ${props.label} selecionados`
})

// Handlers
const toggleDropdown = () => {
  isOpen.value = !isOpen.value
  if (!isOpen.value) searchQuery.value = ''
}

const toggleOption = (optionId: string) => {
  const newValue = props.modelValue.includes(optionId)
    ? props.modelValue.filter(id => id !== optionId)
    : [...props.modelValue, optionId]
  
  emit('update:modelValue', newValue)
}

const clearAll = (event: Event) => {
  event.stopPropagation()
  emit('update:modelValue', [])
}

const isSelected = (optionId: string) => {
  return props.modelValue.includes(optionId)
}
</script>

<template>
  <div ref="dropdownRef" class="relative">
    <!-- Botão Principal -->
    <button
      type="button"
      @click="toggleDropdown"
      class="relative w-full bg-white dark:bg-slate-700 border border-gray-300 dark:border-slate-600 text-gray-900 dark:text-slate-100 text-sm rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 px-3 py-2.5 text-left transition-colors flex items-center justify-between gap-2"
      :class="{ 'ring-2 ring-primary-500': isOpen }"
    >
      <span class="truncate flex-1">{{ buttonText }}</span>
      
      <div class="flex items-center gap-1 flex-shrink-0">
        <!-- Botão Limpar (se houver seleções) -->
        <button
          v-if="modelValue.length > 0"
          @click="clearAll"
          type="button"
          class="p-0.5 hover:bg-gray-200 dark:hover:bg-slate-600 rounded transition-colors"
          title="Limpar seleção"
        >
          <X class="w-3.5 h-3.5 text-gray-500 dark:text-slate-400" />
        </button>
        
        <!-- Chevron -->
        <ChevronDown 
          class="w-4 h-4 text-gray-500 dark:text-slate-400 transition-transform"
          :class="{ 'rotate-180': isOpen }"
        />
      </div>
    </button>

    <!-- Dropdown -->
    <Transition
      enter-active-class="transition ease-out duration-100"
      enter-from-class="transform opacity-0 scale-95"
      enter-to-class="transform opacity-100 scale-100"
      leave-active-class="transition ease-in duration-75"
      leave-from-class="transform opacity-100 scale-100"
      leave-to-class="transform opacity-0 scale-95"
    >
      <div
        v-show="isOpen"
        class="absolute z-50 w-full mt-1 bg-white dark:bg-slate-800 border border-gray-300 dark:border-slate-600 rounded-lg shadow-lg max-h-64 overflow-hidden flex flex-col"
      >
        <!-- Campo de Busca -->
        <div class="p-2 border-b border-gray-200 dark:border-slate-700">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar..."
            class="w-full px-3 py-1.5 text-sm bg-gray-50 dark:bg-slate-900 border border-gray-300 dark:border-slate-600 rounded focus:ring-2 focus:ring-primary-500 focus:outline-none text-gray-900 dark:text-slate-100"
            @click.stop
          />
        </div>

        <!-- Lista de Opções -->
        <div class="overflow-y-auto flex-1">
          <div
            v-for="option in filteredOptions"
            :key="option.id"
            @click="toggleOption(option.id)"
            class="flex items-center gap-2 px-3 py-2 hover:bg-gray-100 dark:hover:bg-slate-700 cursor-pointer transition-colors"
            :class="{ 'bg-primary-50 dark:bg-primary-900/20': isSelected(option.id) }"
          >
            <!-- Checkbox -->
            <div
              class="w-4 h-4 border rounded flex items-center justify-center flex-shrink-0 transition-colors"
              :class="
                isSelected(option.id)
                  ? 'bg-primary-600 border-primary-600'
                  : 'border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-700'
              "
            >
              <Check
                v-if="isSelected(option.id)"
                class="w-3 h-3 text-white"
              />
            </div>
            
            <!-- Nome -->
            <span class="text-sm text-gray-900 dark:text-slate-100 flex-1">
              {{ option.nome }}
            </span>
          </div>

          <!-- Sem resultados -->
          <div
            v-if="filteredOptions.length === 0"
            class="px-3 py-6 text-center text-sm text-gray-500 dark:text-slate-400"
          >
            Nenhum resultado encontrado
          </div>
        </div>

        <!-- Footer com contador -->
        <div
          v-if="modelValue.length > 0"
          class="px-3 py-2 border-t border-gray-200 dark:border-slate-700 bg-gray-50 dark:bg-slate-900 text-xs text-gray-600 dark:text-slate-400 text-center"
        >
          {{ modelValue.length }} {{ modelValue.length === 1 ? 'item selecionado' : 'itens selecionados' }}
        </div>
      </div>
    </Transition>
  </div>
</template>
