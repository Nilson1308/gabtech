<script setup lang="ts">
import { ref, watch } from 'vue'
import { History, X } from 'lucide-vue-next'
import Button from '@/components/common/Button.vue'
import { useFormatters } from '@/composables/useFormatters'
import type { AuditoriaAlvo } from '@/services/auditoria'
import { fetchHistoricoAuditoria, type EventoAuditoriaItem } from '@/services/auditoria'

const props = defineProps<{
  open: boolean
  alvo: AuditoriaAlvo | null
  titulo?: string
}>()

const emit = defineEmits<{ close: [] }>()

const { formatDate } = useFormatters()
const loading = ref(false)
const erro = ref<string | null>(null)
const eventos = ref<EventoAuditoriaItem[]>([])

async function carregar() {
  if (!props.alvo) return
  loading.value = true
  erro.value = null
  try {
    eventos.value = await fetchHistoricoAuditoria(props.alvo)
  } catch (e) {
    erro.value = e instanceof Error ? e.message : 'Não foi possível carregar o histórico.'
    eventos.value = []
  } finally {
    loading.value = false
  }
}

watch(
  () => [props.open, props.alvo?.objectId, props.alvo?.model] as const,
  ([open]) => {
    if (open) void carregar()
  },
)
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/50"
      @click.self="emit('close')"
    >
      <div
        class="bg-white dark:bg-slate-900 rounded-xl shadow-xl w-full max-w-lg max-h-[85vh] flex flex-col border border-gray-200 dark:border-slate-700"
        role="dialog"
        aria-labelledby="historico-auditoria-titulo"
      >
        <div class="flex items-start justify-between gap-3 p-4 border-b border-gray-100 dark:border-slate-800">
          <div class="flex items-center gap-2 min-w-0">
            <History class="w-5 h-5 text-gray-500 shrink-0" />
            <div class="min-w-0">
              <h2 id="historico-auditoria-titulo" class="font-semibold text-gray-900 dark:text-slate-100 truncate">
                {{ titulo ?? 'Histórico de ações' }}
              </h2>
              <p v-if="alvo" class="text-xs text-gray-500 dark:text-slate-400 truncate">
                {{ alvo.appLabel }} · {{ alvo.model }} #{{ alvo.objectId }}
              </p>
            </div>
          </div>
          <button
            type="button"
            class="p-1 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-slate-800"
            aria-label="Fechar"
            @click="emit('close')"
          >
            <X class="w-5 h-5" />
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-4">
          <div v-if="loading" class="py-8 text-center text-sm text-gray-500">Carregando…</div>
          <p v-else-if="erro" class="text-sm text-red-600">{{ erro }}</p>
          <p v-else-if="!eventos.length" class="text-sm text-gray-500">
            Nenhuma ação registrada ainda (alterações anteriores à auditoria podem não aparecer).
          </p>
          <ul v-else class="space-y-3">
            <li
              v-for="ev in eventos"
              :key="ev.id"
              class="text-sm border-l-2 border-gray-200 dark:border-slate-700 pl-3 py-0.5"
            >
              <p class="font-medium text-gray-900 dark:text-slate-100">
                {{ ev.acaoLabel }}
                <span v-if="ev.usuarioNome" class="font-normal text-gray-600 dark:text-slate-400">
                  · {{ ev.usuarioNome }}
                </span>
              </p>
              <p class="text-xs text-gray-500 dark:text-slate-400 mt-0.5">
                {{ formatDate(ev.ocorridoEm, true) }}
              </p>
              <p v-if="ev.objectRepr" class="text-xs text-gray-400 mt-0.5 truncate">{{ ev.objectRepr }}</p>
            </li>
          </ul>
        </div>

        <div class="p-4 border-t border-gray-100 dark:border-slate-800 flex justify-end">
          <Button variant="secondary" @click="emit('close')">Fechar</Button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
