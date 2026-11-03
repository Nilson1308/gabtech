<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useCrmStore } from '@/stores/crm'
import type { Cidadao } from '@/types'
import { Mail, Phone } from 'lucide-vue-next'
import RastreabilidadeMeta from '@/components/common/RastreabilidadeMeta.vue'
import { AUDITORIA_ALVO } from '@/services/auditoria'

const crmStore = useCrmStore()

function tagPorId(id: string) {
  return crmStore.tagsDisponiveis.find(t => t.id === id)
}

interface Props {
  cidadaos: Cidadao[]
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

const router = useRouter()

const verPerfil = (id: string) => {
  router.push(`/crm/${id}`)
}
</script>

<template>
  <div class="overflow-x-auto">
    <!-- Loading State -->
    <div v-if="loading" class="space-y-3 p-6 bg-white dark:bg-slate-900">
      <div v-for="i in 5" :key="i" class="animate-pulse flex gap-4">
        <div class="h-12 bg-gray-200 dark:bg-slate-700 rounded flex-1"></div>
      </div>
    </div>

    <!-- Tabela -->
    <table v-else class="min-w-full divide-y divide-gray-200 dark:divide-slate-700">
      <thead class="bg-gray-50 dark:bg-slate-800">
        <tr>
          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-slate-400 uppercase tracking-wider">
            Nome
          </th>
          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-slate-400 uppercase tracking-wider">
            Contato
          </th>
          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-slate-400 uppercase tracking-wider">
            Bairro
          </th>
          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-slate-400 uppercase tracking-wider">
            Tags
          </th>
          <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-slate-400 uppercase tracking-wider hidden xl:table-cell">
            Última ação
          </th>
        </tr>
      </thead>
      <tbody class="bg-white dark:bg-slate-900 divide-y divide-gray-200 dark:divide-slate-700">
        <tr 
          v-for="cidadao in cidadaos" 
          :key="cidadao.id"
          @click="verPerfil(cidadao.id)"
          class="hover:bg-gray-50 dark:hover:bg-slate-800 cursor-pointer transition-colors"
        >
          <!-- Nome -->
          <td class="px-6 py-4 whitespace-nowrap">
            <div class="flex items-center">
              <div class="flex-shrink-0 h-10 w-10">
                <div class="h-10 w-10 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center">
                  <span class="text-sm font-medium text-primary-700 dark:text-primary-400">
                    {{ cidadao.nome.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase() }}
                  </span>
                </div>
              </div>
              <div class="ml-4">
                <div class="text-sm font-medium text-gray-900 dark:text-slate-100">
                  {{ cidadao.nome }}
                </div>
                <div v-if="cidadao.cpf" class="text-xs text-gray-500 dark:text-slate-400">
                  {{ cidadao.cpf }}
                </div>
              </div>
            </div>
          </td>

          <!-- Contato -->
          <td class="px-6 py-4 whitespace-nowrap">
            <div class="space-y-1">
              <div class="flex items-center gap-2 text-sm text-gray-900 dark:text-slate-100">
                <Phone class="w-4 h-4 text-gray-400 dark:text-slate-500" />
                {{ cidadao.telefone }}
              </div>
              <div v-if="cidadao.email" class="flex items-center gap-2 text-xs text-gray-500 dark:text-slate-400">
                <Mail class="w-4 h-4 text-gray-400 dark:text-slate-500" />
                {{ cidadao.email }}
              </div>
            </div>
          </td>

          <!-- Bairro -->
          <td class="px-6 py-4 whitespace-nowrap">
            <div class="text-sm text-gray-900 dark:text-slate-100">
              {{ cidadao.bairro || cidadao.endereco?.bairro || '-' }}
            </div>
            <div v-if="cidadao.endereco?.cidade" class="text-xs text-gray-500 dark:text-slate-400">
              {{ cidadao.endereco.cidade }}/{{ cidadao.endereco.estado }}
            </div>
          </td>

          <!-- Tags / perfis -->
          <td class="px-6 py-4">
            <div class="flex flex-wrap gap-1 max-w-xs">
              <span
                v-for="tagId in cidadao.tag_ids"
                :key="'m-' + tagId"
                class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border"
                :style="{
                  backgroundColor: (tagPorId(tagId)?.cor ?? '#6b7280') + '20',
                  color: tagPorId(tagId)?.cor ?? '#6b7280',
                  borderColor: (tagPorId(tagId)?.cor ?? '#6b7280') + '40',
                }"
              >
                {{ tagPorId(tagId)?.nome ?? 'Tag' }}
              </span>
              <span
                v-for="perfil in cidadao.perfis_profissionais"
                :key="perfil.id"
                class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 dark:bg-slate-700 text-gray-700 dark:text-slate-300 border border-gray-300 dark:border-slate-600"
                :title="perfil.instituicao"
              >
                {{ perfil.cargo }}
              </span>
              <span
                v-if="(!cidadao.tag_ids || cidadao.tag_ids.length === 0) && (!cidadao.perfis_profissionais || cidadao.perfis_profissionais.length === 0)"
                class="text-xs text-gray-400 dark:text-slate-500"
              >
                —
              </span>
            </div>
          </td>

          <td class="px-6 py-4 hidden xl:table-cell max-w-[220px]" @click.stop>
            <RastreabilidadeMeta
              :rastreabilidade="cidadao.rastreabilidade"
              :alvo-auditoria="AUDITORIA_ALVO.cidadao(cidadao.id)"
              historico-titulo="Histórico do cidadão"
              compact
            />
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Estado Vazio -->
    <div v-if="!loading && cidadaos.length === 0" class="text-center py-12">
      <p class="text-gray-500 dark:text-slate-400">Nenhum cidadão encontrado</p>
    </div>
  </div>
</template>
