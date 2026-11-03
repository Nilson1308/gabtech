<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useCrmStore } from '@/stores/crm'
import {
  HINT_TAGS_CONTEXTO_PROFISSIONAL,
  HINT_TAGS_SEGMENTACAO,
  LABEL_TAGS_CONTEXTO_PROFISSIONAL,
  LABEL_TAGS_SEGMENTACAO,
} from '@/constants/servicosTags'

const model = defineModel<string[]>({ default: () => [] })

interface Props {
  /** profissional = vagas/cursos/currículo; segmentacao = assistência social */
  variant?: 'profissional' | 'segmentacao'
  label?: string
  hint?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'profissional',
})

const crmStore = useCrmStore()
const { tagsContextoProfissional, tagsSegmentacaoServicos } = storeToRefs(crmStore)

const label = computed(() => {
  if (props.label) return props.label
  return props.variant === 'segmentacao'
    ? LABEL_TAGS_SEGMENTACAO
    : LABEL_TAGS_CONTEXTO_PROFISSIONAL
})

const hint = computed(() => {
  if (props.hint) return props.hint
  return props.variant === 'segmentacao'
    ? HINT_TAGS_SEGMENTACAO
    : HINT_TAGS_CONTEXTO_PROFISSIONAL
})

const tags = computed(() =>
  props.variant === 'segmentacao'
    ? tagsSegmentacaoServicos.value
    : tagsContextoProfissional.value,
)

function toggle(id: string) {
  const i = model.value.indexOf(id)
  if (i >= 0) {
    model.value = model.value.filter(x => x !== id)
  } else {
    model.value = [...model.value, id]
  }
}

onMounted(() => {
  crmStore.fetchTags()
})
</script>

<template>
  <div>
    <p class="label text-xs mb-1">{{ label }}</p>
    <p v-if="hint" class="text-xs text-gray-500 dark:text-slate-400 mb-2">{{ hint }}</p>
    <div v-if="tags.length === 0" class="text-xs text-gray-500">
      Nenhuma tag compatível no CRM. Crie em Configurações → Classificações (tipo
      {{ variant === 'segmentacao' ? 'Segmentação' : 'Contexto profissional' }}).
    </div>
    <div v-else class="flex flex-wrap gap-2">
      <button
        v-for="tag in tags"
        :key="tag.id"
        type="button"
        class="text-xs px-2.5 py-1 rounded-full border transition-colors"
        :style="
          model.includes(tag.id)
            ? { backgroundColor: tag.cor, borderColor: tag.cor, color: '#fff' }
            : { borderColor: tag.cor + '66', color: tag.cor }
        "
        @click="toggle(tag.id)"
      >
        {{ tag.nome }}
      </button>
    </div>
  </div>
</template>
