<script setup lang="ts">
import { ref } from 'vue'
import { useCrmStore } from '@/stores/crm'
import Button from '@/components/common/Button.vue'
import { Plus, Check } from 'lucide-vue-next'

const emit = defineEmits<{
  created: [tagId: string]
}>()

const crmStore = useCrmStore()

const mostrarForm = ref(false)
const criando = ref(false)
const form = ref({
  nome: '',
  cor: '#3b82f6',
  modulos: ['crm'] as ('crm' | 'atendimentos')[]
})

const cores = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444',
  '#8b5cf6', '#ec4899', '#6b7280', '#6366f1'
]

const toggleForm = () => {
  mostrarForm.value = !mostrarForm.value
  if (!mostrarForm.value) {
    form.value = { nome: '', cor: '#3b82f6', modulos: ['crm'] }
  }
}

const criar = async () => {
  if (!form.value.nome.trim()) return

  criando.value = true
  try {
    const novaTag = await crmStore.createTag(form.value)
    emit('created', novaTag.id)
    form.value = { nome: '', cor: '#3b82f6', modulos: ['crm'] }
    mostrarForm.value = false
  } finally {
    criando.value = false
  }
}
</script>

<template>
  <div class="space-y-2">
    <!-- Botão de Toggle -->
    <button
      v-if="!mostrarForm"
      @click="toggleForm"
      type="button"
      class="w-full flex items-center justify-center gap-2 px-3 py-2 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg text-sm text-gray-600 dark:text-gray-400 hover:border-primary-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
    >
      <Plus class="w-4 h-4" />
      Criar Nova Tag
    </button>

    <!-- Formulário Inline -->
    <div
      v-else
      class="p-3 border-2 border-primary-300 dark:border-primary-700 rounded-lg bg-primary-50 dark:bg-primary-900/20 space-y-3"
    >
      <div>
        <input
          v-model="form.nome"
          type="text"
          placeholder="Nome da tag"
          class="input text-sm"
          @keyup.enter="criar"
          @keyup.esc="toggleForm"
        />
      </div>

      <div class="flex gap-1">
        <button
          v-for="cor in cores"
          :key="cor"
          @click="form.cor = cor"
          type="button"
          :class="[
            form.cor === cor ? 'ring-2 ring-primary-600 ring-offset-2 dark:ring-offset-gray-800' : '',
            'w-8 h-8 rounded-full transition-all hover:scale-110'
          ]"
          :style="{ backgroundColor: cor }"
          :title="cor"
        ></button>
      </div>

      <div class="flex items-center gap-2">
        <Button
          variant="primary"
          @click="criar"
          :loading="criando"
          :disabled="!form.nome.trim()"
          class="flex-1 text-sm py-1.5"
        >
          <Check class="w-4 h-4" />
          {{ criando ? 'Criando...' : 'Criar' }}
        </Button>
        <Button
          variant="ghost"
          @click="toggleForm"
          :disabled="criando"
          class="text-sm py-1.5"
        >
          Cancelar
        </Button>
      </div>
    </div>
  </div>
</template>
