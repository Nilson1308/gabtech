<script setup lang="ts">
import { Pencil, Trash2 } from 'lucide-vue-next'

interface Props {
  disabled?: boolean
  showEdit?: boolean
  showDelete?: boolean
}

withDefaults(defineProps<Props>(), {
  showEdit: true,
  showDelete: true,
})

const emit = defineEmits<{
  edit: []
  delete: []
}>()
</script>

<template>
  <div v-if="showEdit || showDelete" class="flex items-center gap-0.5 shrink-0" @click.stop>
    <button
      v-if="showEdit"
      type="button"
      class="p-1.5 rounded-lg text-gray-500 hover:text-primary-600 hover:bg-gray-100 dark:hover:bg-slate-700 disabled:opacity-40"
      title="Editar"
      :disabled="disabled"
      @click="emit('edit')"
    >
      <Pencil class="w-3.5 h-3.5" />
    </button>
    <button
      v-if="showDelete"
      type="button"
      class="p-1.5 rounded-lg text-gray-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/40 disabled:opacity-40"
      title="Excluir"
      :disabled="disabled"
      @click="emit('delete')"
    >
      <Trash2 class="w-3.5 h-3.5" />
    </button>
  </div>
</template>
