<script setup lang="ts">
import { ChevronDown } from 'lucide-vue-next'

interface Props {
  modelValue: string | string[]
  placeholder?: string
  options: Array<{ id: string; nome: string }>
  multiple?: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: string | string[]]
}>()

const handleChange = (event: Event) => {
  const target = event.target as HTMLSelectElement
  if (props.multiple) {
    const selected = Array.from(target.selectedOptions).map(option => option.value)
    emit('update:modelValue', selected)
  } else {
    emit('update:modelValue', target.value)
  }
}
</script>

<template>
  <div class="relative">
    <select
      :value="modelValue"
      @change="handleChange"
      :multiple="multiple"
      :size="multiple ? 4 : 1"
      class="appearance-none bg-white dark:bg-slate-700 border border-gray-300 dark:border-slate-600 text-gray-900 dark:text-slate-100 text-sm rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 block w-full p-2.5 pr-10 transition-colors"
      :class="{ 'h-auto': multiple }"
    >
      <option v-if="!multiple" value="" disabled>{{ placeholder || 'Selecione...' }}</option>
      <option
        v-for="option in options"
        :key="option.id"
        :value="option.id"
        class="py-2"
      >
        {{ option.nome }}
      </option>
    </select>
    
    <!-- Chevron Icon -->
    <div 
      v-if="!multiple"
      class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none"
    >
      <ChevronDown class="w-4 h-4 text-gray-500 dark:text-slate-400" />
    </div>
  </div>
</template>
