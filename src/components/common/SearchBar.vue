<script setup lang="ts">
import { Search, X } from 'lucide-vue-next'

interface Props {
  modelValue: string
  placeholder?: string
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Buscar...'
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}

const limpar = () => {
  emit('update:modelValue', '')
}
</script>

<template>
  <div class="relative">
    <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
    <input 
      :value="modelValue"
      @input="handleInput"
      type="text"
      :placeholder="placeholder"
      class="input pl-10 pr-10"
    />
    <button 
      v-if="modelValue"
      @click="limpar"
      class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
      type="button"
    >
      <X class="w-5 h-5" />
    </button>
  </div>
</template>
