<script setup lang="ts">
import { onUnmounted, watch, ref } from 'vue'
import { X } from 'lucide-vue-next'

interface Props {
  modelValue: boolean
  titulo: string
  largura?: 'sm' | 'md' | 'lg' | 'xl' | '2xl'
}

const props = withDefaults(defineProps<Props>(), {
  largura: 'lg'
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const modalRef = ref<HTMLElement | null>(null)

const fechar = () => {
  emit('update:modelValue', false)
}

const handleEscape = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && props.modelValue) {
    fechar()
  }
}

// Adicionar/remover listener de ESC
watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    document.addEventListener('keydown', handleEscape)
    // Focar no modal quando abrir
    setTimeout(() => {
      modalRef.value?.focus()
    }, 100)
  } else {
    document.removeEventListener('keydown', handleEscape)
  }
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscape)
})

const larguraClasses = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-xl',
  '2xl': 'max-w-2xl',
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
        class="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 z-50 flex items-center justify-center p-4"
        @click.self="fechar"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="`modal-title-${titulo}`"
      >
        <Transition
          enter-active-class="transition-all duration-300"
          enter-from-class="opacity-0 scale-95"
          enter-to-class="opacity-100 scale-100"
          leave-active-class="transition-all duration-300"
          leave-from-class="opacity-100 scale-100"
          leave-to-class="opacity-0 scale-95"
        >
          <div 
            v-if="modelValue"
            ref="modalRef"
            :class="larguraClasses[largura]"
            class="bg-white dark:bg-slate-800 rounded-lg shadow-xl w-full overflow-hidden"
            tabindex="-1"
          >
            <!-- Header -->
            <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-slate-700">
              <h3 
                :id="`modal-title-${titulo}`"
                class="text-lg font-semibold text-gray-900 dark:text-slate-100"
              >
                {{ titulo }}
              </h3>
              <button 
                @click="fechar"
                class="text-gray-400 hover:text-gray-600 dark:text-slate-400 dark:hover:text-slate-300 transition-colors"
                type="button"
                aria-label="Fechar modal"
              >
                <X class="w-5 h-5" />
              </button>
            </div>
            
            <!-- Body -->
            <div class="px-6 py-4 max-h-[calc(100vh-200px)] overflow-y-auto bg-white dark:bg-slate-800">
              <slot />
            </div>
            
            <!-- Footer (opcional) -->
            <div v-if="$slots.footer" class="px-6 py-4 border-t border-gray-200 dark:border-slate-700 bg-gray-50 dark:bg-slate-900 flex justify-end gap-3">
              <slot name="footer" />
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>
