<script setup lang="ts">
import { ref, computed } from 'vue'
import { X, AlertCircle, CheckCircle, AlertTriangle, Info } from 'lucide-vue-next'

export interface AlertDialogOptions {
  title?: string
  message: string
  type?: 'info' | 'success' | 'warning' | 'error' | 'confirm'
  confirmText?: string
  cancelText?: string
  onConfirm?: () => void
  onCancel?: () => void
}

const isOpen = ref(false)
const options = ref<AlertDialogOptions>({
  message: '',
  type: 'info',
  confirmText: 'OK',
  cancelText: 'Cancelar'
})

function show(opts: AlertDialogOptions) {
  options.value = {
    type: 'info',
    confirmText: 'OK',
    cancelText: 'Cancelar',
    ...opts
  }
  isOpen.value = true
  
  return new Promise<boolean>((resolve) => {
    const originalConfirm = options.value.onConfirm
    const originalCancel = options.value.onCancel
    
    options.value.onConfirm = () => {
      originalConfirm?.()
      resolve(true)
      close()
    }
    
    options.value.onCancel = () => {
      originalCancel?.()
      resolve(false)
      close()
    }
  })
}

function close() {
  isOpen.value = false
}

function handleConfirm() {
  options.value.onConfirm?.()
}

function handleCancel() {
  options.value.onCancel?.()
}

const iconComponent = computed(() => {
  switch (options.value.type) {
    case 'success':
      return CheckCircle
    case 'warning':
      return AlertTriangle
    case 'error':
      return AlertCircle
    case 'confirm':
      return AlertCircle
    default:
      return Info
  }
})

const colorClasses = computed(() => {
  switch (options.value.type) {
    case 'success':
      return {
        bg: 'bg-green-100 dark:bg-green-900/30',
        text: 'text-green-600 dark:text-green-400',
        button: 'bg-green-600 hover:bg-green-700 dark:bg-green-700 dark:hover:bg-green-800'
      }
    case 'warning':
      return {
        bg: 'bg-yellow-100 dark:bg-yellow-900/30',
        text: 'text-yellow-600 dark:text-yellow-400',
        button: 'bg-yellow-600 hover:bg-yellow-700 dark:bg-yellow-700 dark:hover:bg-yellow-800'
      }
    case 'error':
      return {
        bg: 'bg-red-100 dark:bg-red-900/30',
        text: 'text-red-600 dark:text-red-400',
        button: 'bg-red-600 hover:bg-red-700 dark:bg-red-700 dark:hover:bg-red-800'
      }
    case 'confirm':
      return {
        bg: 'bg-blue-100 dark:bg-blue-900/30',
        text: 'text-blue-600 dark:text-blue-400',
        button: 'bg-blue-600 hover:bg-blue-700 dark:bg-blue-700 dark:hover:bg-blue-800'
      }
    default:
      return {
        bg: 'bg-blue-100 dark:bg-blue-900/30',
        text: 'text-blue-600 dark:text-blue-400',
        button: 'bg-primary-600 hover:bg-primary-700 dark:bg-primary-700 dark:hover:bg-primary-800'
      }
  }
})

defineExpose({
  show
})
</script>

<template>
  <Transition
    enter-active-class="transition ease-out duration-200"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition ease-in duration-150"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="isOpen"
      class="fixed inset-0 bg-black bg-opacity-50 z-[9999] flex items-center justify-center p-4"
      @click.self="options.type === 'confirm' ? handleCancel() : close()"
    >
      <Transition
        enter-active-class="transition ease-out duration-200"
        enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition ease-in duration-150"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div
          v-if="isOpen"
          class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full overflow-hidden"
        >
          <!-- Header com ícone -->
          <div class="p-6">
            <div class="flex items-start gap-4">
              <div
                :class="[colorClasses.bg, colorClasses.text, 'p-3 rounded-full flex-shrink-0']"
              >
                <component :is="iconComponent" class="w-6 h-6" />
              </div>
              
              <div class="flex-1 min-w-0">
                <h3
                  v-if="options.title"
                  class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2"
                >
                  {{ options.title }}
                </h3>
                
                <p class="text-gray-600 dark:text-gray-400 whitespace-pre-wrap">
                  {{ options.message }}
                </p>
              </div>

              <button
                v-if="options.type !== 'confirm'"
                @click="close"
                class="flex-shrink-0 p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded transition-colors"
              >
                <X class="w-5 h-5" />
              </button>
            </div>
          </div>

          <!-- Footer com botões -->
          <div class="bg-gray-50 dark:bg-gray-900/50 px-6 py-4 flex items-center justify-end gap-3">
            <button
              v-if="options.type === 'confirm'"
              @click="handleCancel"
              class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-lg font-medium transition-colors"
            >
              {{ options.cancelText }}
            </button>
            
            <button
              @click="handleConfirm"
              :class="[
                colorClasses.button,
                'px-4 py-2 text-white rounded-lg font-medium transition-colors'
              ]"
            >
              {{ options.confirmText }}
            </button>
          </div>
        </div>
      </Transition>
    </div>
  </Transition>
</template>
