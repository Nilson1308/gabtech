<script setup lang="ts">
import { computed } from 'vue'
import type { SugestaoMatchmaking } from '@/types'
import Button from '@/components/common/Button.vue'
import { CheckCircle2, Loader2, Sparkles } from 'lucide-vue-next'

interface Props {
  sugestoes: SugestaoMatchmaking[]
  /** IDs que já participaram (oculta ação ou mostra badge) */
  idsJaVinculados?: string[]
  acaoLabel?: string
  processandoId?: string | null
  vazio?: string
  carregando?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  idsJaVinculados: () => [],
  acaoLabel: 'Selecionar',
  vazio: 'Nenhuma sugestão no momento.',
})

const emit = defineEmits<{
  acao: [s: SugestaoMatchmaking]
}>()

const listaVisivel = computed(() =>
  props.sugestoes.filter(s => !props.idsJaVinculados.includes(s.cidadao.id)),
)

function iniciais(nome: string) {
  return nome.trim().charAt(0).toUpperCase() || '?'
}
</script>

<template>
  <div class="rounded-xl border border-indigo-200/80 dark:border-indigo-900/60 overflow-hidden">
    <div
      class="flex items-center gap-2 px-3 py-2.5 bg-indigo-50 dark:bg-indigo-950/40 text-indigo-900 dark:text-indigo-200 text-sm font-medium"
    >
      <Sparkles class="w-4 h-4 shrink-0" />
      Sugestões inteligentes
    </div>

    <div v-if="carregando" class="flex items-center justify-center gap-2 py-8 text-sm text-gray-500">
      <Loader2 class="w-4 h-4 animate-spin" />
      Calculando compatibilidade…
    </div>

    <ul v-else-if="listaVisivel.length" class="divide-y divide-gray-100 dark:divide-slate-800">
      <li
        v-for="s in listaVisivel"
        :key="s.cidadao.id"
        class="flex flex-col sm:flex-row sm:items-center gap-3 px-3 py-3 hover:bg-gray-50/80 dark:hover:bg-slate-800/40"
      >
        <div class="flex items-start gap-3 flex-1 min-w-0">
          <div
            class="w-10 h-10 rounded-full bg-indigo-100 dark:bg-indigo-900/40 flex items-center justify-center text-indigo-700 dark:text-indigo-300 font-semibold shrink-0"
          >
            {{ iniciais(s.cidadao.nome) }}
          </div>
          <div class="min-w-0 flex-1">
            <p class="font-medium text-sm text-gray-900 dark:text-slate-100 truncate">
              {{ s.cidadao.nome }}
            </p>
            <p class="text-xs text-gray-500 dark:text-slate-400">
              {{ s.cidadao.telefone }}
              <span v-if="s.cidadao.bairro"> · {{ s.cidadao.bairro }}</span>
            </p>
            <div v-if="s.tagsCoincidentes.length" class="flex flex-wrap gap-1 mt-1.5">
              <span
                v-for="tag in s.tagsCoincidentes"
                :key="tag.id"
                class="text-[10px] px-1.5 py-0.5 rounded-full font-medium"
                :style="{ backgroundColor: tag.cor + '22', color: tag.cor }"
              >
                {{ tag.nome }}
              </span>
            </div>
          </div>
          <span
            v-if="s.score > 0"
            class="text-xs font-semibold text-indigo-600 dark:text-indigo-400 shrink-0 tabular-nums"
          >
            {{ s.score }} tag{{ s.score === 1 ? '' : 's' }}
          </span>
        </div>

        <Button
          variant="primary"
          tamanho="sm"
          class="shrink-0 w-full sm:w-auto"
          :loading="processandoId === s.cidadao.id"
          :disabled="!!processandoId && processandoId !== s.cidadao.id"
          @click="emit('acao', s)"
        >
          {{ acaoLabel }}
        </Button>
      </li>
    </ul>

    <p v-else class="text-sm text-center text-gray-500 dark:text-slate-400 py-8 px-4">
      {{ vazio }}
    </p>

    <p
      v-if="!carregando && idsJaVinculados.length > 0 && sugestoes.some(s => idsJaVinculados.includes(s.cidadao.id))"
      class="text-xs text-gray-500 dark:text-slate-400 px-3 py-2 border-t border-gray-100 dark:border-slate-800 flex items-center gap-1.5"
    >
      <CheckCircle2 class="w-3.5 h-3.5 text-emerald-500" />
      Cidadãos já vinculados à ação não aparecem na lista.
    </p>
  </div>
</template>
