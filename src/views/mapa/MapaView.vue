<script setup lang="ts">
import { computed, onMounted, ref, watch, nextTick } from 'vue'
import { useAnalyticsStore, type TerritorialAgrupamento, type MapBbox } from '@/stores/analytics'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { Layers, MapPin, Flame, X } from 'lucide-vue-next'

// Fix dos ícones do Leaflet no Vite
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png'
import iconUrl from 'leaflet/dist/images/marker-icon.png'
import shadowUrl from 'leaflet/dist/images/marker-shadow.png'

delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl,
  iconUrl,
  shadowUrl,
})

const analyticsStore = useAnalyticsStore()

const mapaContainer = ref<HTMLElement | null>(null)
let mapa: L.Map | null = null

// Controle de camadas
const camadasAtivas = ref({
  cidadaos: true,
  demandas: true
})

// Painel de camadas aberto/fechado
const painelAberto = ref(true)

// Markers e círculos
const markersLayer = ref<L.LayerGroup | null>(null)
const heatLayer = ref<L.LayerGroup | null>(null)

const agrupamentoDemandas = ref<TerritorialAgrupamento>('macrotema')
const filtroMacrotemaId = ref('')
const filtroBairro = ref('')

const demandasResumo = computed(() => {
  const n = analyticsStore.zonasCalor.length
  if (analyticsStore.territorialAgrupamento === 'macrotema_bairro') {
    return `${n} combinações macrotema + bairro`
  }
  return `${n} macrotemas com demandas pendentes`
})

const demandasLegendaTitulo = computed(() =>
  analyticsStore.territorialAgrupamento === 'macrotema_bairro'
    ? 'Pendentes por macrotema e bairro:'
    : 'Pendentes por macrotema:',
)

const demandasLegendaRotulo = (zona: { nome: string; macrotema: string }) =>
  analyticsStore.territorialAgrupamento === 'macrotema_bairro' ? zona.nome : zona.macrotema

const queryTerritorial = () => ({
  agrupamento: agrupamentoDemandas.value as TerritorialAgrupamento,
  macrotemaId: filtroMacrotemaId.value ? Number(filtroMacrotemaId.value) : null,
  bairro: filtroBairro.value || null,
})

const pinsResumoTexto = computed(() => {
  const visiveis = analyticsStore.pinsCidadaos.length
  const total =
    analyticsStore.territorialTotais?.cidadaosGeolocalizados ??
    analyticsStore.pinsMeta?.totalGeolocalizados ??
    visiveis
  if (!camadasAtivas.value.cidadaos) {
    return `${total} cidadãos geolocalizados (camada desligada)`
  }
  if (analyticsStore.pinsMeta?.limitAplicado) {
    return `${visiveis} pins na área visível (limite; ${total} no filtro)`
  }
  if (visiveis < total) {
    return `${visiveis} na área visível · ${total} no filtro`
  }
  return `${visiveis} cidadãos mapeados`
})

let debounceMapaFiltros: ReturnType<typeof setTimeout> | null = null
let debouncePinsViewport: ReturnType<typeof setTimeout> | null = null

function bboxDoMapa(): MapBbox | null {
  if (!mapa) return null
  const b = mapa.getBounds()
  return {
    swLat: b.getSouth(),
    swLng: b.getWest(),
    neLat: b.getNorth(),
    neLng: b.getEast(),
  }
}

async function carregarPinsNaViewport() {
  if (!camadasAtivas.value.cidadaos) {
    return
  }
  const bbox = bboxDoMapa()
  if (!bbox) return
  await analyticsStore.carregarTerritorialPins({
    ...queryTerritorial(),
    bbox,
  })
}

async function recarregarMapaBase() {
  await analyticsStore.carregarMapaBase(queryTerritorial())
  await carregarPinsNaViewport()
  if (mapa) atualizarCamadas()
}

function agendarPinsViewport() {
  if (debouncePinsViewport) clearTimeout(debouncePinsViewport)
  debouncePinsViewport = setTimeout(async () => {
    await carregarPinsNaViewport()
    atualizarCamadas()
  }, 350)
}

// Carregar dados
onMounted(async () => {
  await analyticsStore.carregarMapaBase(queryTerritorial())

  await nextTick()

  if (mapaContainer.value) {
    inicializarMapa()
    await carregarPinsNaViewport()
    atualizarCamadas()
  }
})

function inicializarMapa() {
  if (!mapaContainer.value) return

  const centro = analyticsStore.mapaCentro
  mapa = L.map(mapaContainer.value, {
    zoomControl: true
  }).setView([centro.lat, centro.lng], centro.zoom)

  // Adicionar camada de tiles do OpenStreetMap
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 18
  }).addTo(mapa)

  // Criar layers group para markers e heat
  markersLayer.value = L.layerGroup().addTo(mapa)
  heatLayer.value = L.layerGroup().addTo(mapa)

  mapa.on('moveend', () => {
    if (camadasAtivas.value.cidadaos) {
      agendarPinsViewport()
    }
  })

  // Renderizar camadas iniciais
  atualizarCamadas()
}

function atualizarCamadas() {
  if (!mapa || !markersLayer.value || !heatLayer.value) return

  // Limpar layers
  markersLayer.value.clearLayers()
  heatLayer.value.clearLayers()

  // Camada de Cidadãos (Pins Azuis)
  if (camadasAtivas.value.cidadaos) {
    analyticsStore.pinsCidadaos.forEach(pin => {
      const marker = L.marker([pin.lat, pin.lng], {
        icon: L.divIcon({
          className: 'custom-marker',
          html: `
            <div class="relative">
              <div class="w-8 h-8 bg-blue-500 rounded-full border-2 border-white shadow-lg flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div class="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-blue-500"></div>
            </div>
          `,
          iconSize: [32, 40],
          iconAnchor: [16, 40]
        })
      })

      marker.bindPopup(`
        <div class="p-2">
          <h4 class="font-bold text-gray-900">${pin.nome}</h4>
          <p class="text-sm text-gray-600 mt-1">${pin.endereco}</p>
          <div class="flex flex-wrap gap-1 mt-2">
            ${pin.tags.map(tag => `
              <span class="inline-block px-2 py-0.5 text-xs rounded-full bg-blue-100 text-blue-800">
                ${tag}
              </span>
            `).join('')}
          </div>
        </div>
      `)

      markersLayer.value?.addLayer(marker)
    })
  }

  // Camada de Demandas (Zonas de Calor)
  if (camadasAtivas.value.demandas) {
    analyticsStore.zonasCalor.forEach(zona => {
      const circle = L.circle([zona.lat, zona.lng], {
        color: zona.cor,
        fillColor: zona.cor,
        fillOpacity: 0.3,
        radius: zona.radius,
        weight: 2
      })

      circle.bindPopup(`
        <div class="p-2">
          <h4 class="font-bold text-gray-900">${zona.nome}</h4>
          <div class="mt-2 space-y-1">
            <p class="text-sm text-gray-600">
              <span class="font-semibold">${zona.atendimentosPendentes}</span> atendimentos pendentes
            </p>
            ${zona.bairro ? `<p class="text-sm text-gray-600">Bairro: <span class="font-semibold">${zona.bairro}</span></p>` : ''}
            <p class="text-sm text-gray-600">
              Macrotema: <span class="font-semibold" style="color: ${zona.cor}">${zona.macrotema}</span>
            </p>
          </div>
        </div>
      `)

      heatLayer.value?.addLayer(circle)
    })
  }
}

// Observar mudanças nas camadas ativas
watch(camadasAtivas, async () => {
  if (camadasAtivas.value.cidadaos && mapa) {
    await carregarPinsNaViewport()
  }
  atualizarCamadas()
}, { deep: true })

watch(
  () =>
    [
      analyticsStore.pinsCidadaos.length,
      analyticsStore.zonasCalor.length,
      analyticsStore.loading,
      analyticsStore.loadingPins,
      analyticsStore.loadingZonas,
    ] as const,
  ([, , loading, loadingPins, loadingZonas]) => {
    if (!loading && !loadingPins && !loadingZonas && mapa) {
      atualizarCamadas()
    }
  },
)

watch([agrupamentoDemandas, filtroMacrotemaId, filtroBairro], () => {
  if (debounceMapaFiltros) clearTimeout(debounceMapaFiltros)
  debounceMapaFiltros = setTimeout(() => {
    recarregarMapaBase()
  }, 300)
})

function toggleCamada(camada: 'cidadaos' | 'demandas') {
  camadasAtivas.value[camada] = !camadasAtivas.value[camada]
}
</script>

<template>
  <div class="relative h-[calc(100vh-8rem)] min-h-[280px] isolate">
    <!-- Container do Mapa -->
    <div
      ref="mapaContainer"
      class="relative z-0 w-full h-full rounded-lg overflow-hidden"
      :class="[
        'leaflet-map',
        'dark:leaflet-dark-mode'
      ]"
    ></div>

    <!-- Painel de Camadas (Flutuante) -->
    <Transition
      enter-active-class="transition-all duration-300"
      leave-active-class="transition-all duration-300"
      enter-from-class="translate-x-full opacity-0"
      leave-to-class="translate-x-full opacity-0"
    >
      <div
        v-if="painelAberto"
        class="absolute z-[1200] max-md:inset-x-0 max-md:bottom-0 max-md:top-auto max-md:rounded-b-none max-md:max-h-[55vh] max-md:overflow-y-auto md:top-4 md:right-4 md:w-80 w-full bg-white dark:bg-slate-800 rounded-lg shadow-xl border border-gray-200 dark:border-slate-700"
      >
        <!-- Cabeçalho do Painel -->
        <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-slate-700">
          <div class="flex items-center gap-2">
            <Layers class="w-5 h-5 text-primary-600 dark:text-primary-400" />
            <h3 class="font-semibold text-gray-900 dark:text-slate-100">Camadas do Mapa</h3>
          </div>
          <button
            @click="painelAberto = false"
            class="p-1 hover:bg-gray-100 dark:hover:bg-slate-700 rounded-lg transition-colors"
          >
            <X class="w-5 h-5 text-gray-500 dark:text-slate-400" />
          </button>
        </div>

        <!-- Conteúdo do Painel -->
        <div class="p-4 space-y-4">
          <!-- Filtros territoriais -->
          <div class="space-y-3 pb-3 border-b border-gray-200 dark:border-slate-700">
            <p class="text-xs font-semibold text-gray-700 dark:text-slate-300 uppercase tracking-wide">
              Filtros de demanda
            </p>

            <label class="block">
              <span class="text-xs text-gray-600 dark:text-slate-400">Agrupamento</span>
              <select
                v-model="agrupamentoDemandas"
                class="mt-1 w-full text-sm rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-gray-900 dark:text-slate-100 px-2 py-1.5"
                @click.stop
              >
                <option value="macrotema">Por macrotema (visão geral)</option>
                <option value="macrotema_bairro">Macrotema + bairro</option>
              </select>
            </label>

            <label class="block">
              <span class="text-xs text-gray-600 dark:text-slate-400">Macrotema</span>
              <select
                v-model="filtroMacrotemaId"
                class="mt-1 w-full text-sm rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-gray-900 dark:text-slate-100 px-2 py-1.5"
                @click.stop
              >
                <option value="">Todos</option>
                <option
                  v-for="m in analyticsStore.territorialFiltrosMacrotemas"
                  :key="m.id"
                  :value="String(m.id)"
                >
                  {{ m.nome }}
                </option>
              </select>
            </label>

            <label class="block">
              <span class="text-xs text-gray-600 dark:text-slate-400">Bairro</span>
              <select
                v-model="filtroBairro"
                class="mt-1 w-full text-sm rounded-lg border border-gray-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-gray-900 dark:text-slate-100 px-2 py-1.5"
                @click.stop
              >
                <option value="">Todos</option>
                <option
                  v-for="b in analyticsStore.territorialFiltrosBairros"
                  :key="b"
                  :value="b"
                >
                  {{ b }}
                </option>
              </select>
            </label>

            <p
              v-if="analyticsStore.loading || analyticsStore.loadingZonas || analyticsStore.loadingPins"
              class="text-xs text-primary-600 dark:text-primary-400"
            >
              Atualizando mapa…
            </p>
          </div>

          <!-- Camada 1: Cidadãos -->
          <div
            @click="toggleCamada('cidadaos')"
            class="flex items-start gap-3 p-3 rounded-lg border-2 cursor-pointer transition-all"
            :class="[
              camadasAtivas.cidadaos
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                : 'border-gray-200 dark:border-slate-700 hover:border-blue-300 dark:hover:border-blue-700'
            ]"
          >
            <div class="flex-shrink-0 mt-0.5">
              <div
                class="w-5 h-5 rounded border-2 flex items-center justify-center transition-all"
                :class="[
                  camadasAtivas.cidadaos
                    ? 'bg-blue-500 border-blue-500'
                    : 'bg-white dark:bg-slate-700 border-gray-300 dark:border-slate-600'
                ]"
              >
                <svg
                  v-if="camadasAtivas.cidadaos"
                  class="w-3 h-3 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </div>

            <div class="flex-1">
              <div class="flex items-center gap-2">
                <MapPin class="w-4 h-4 text-blue-600 dark:text-blue-400" />
                <h4 class="font-semibold text-gray-900 dark:text-slate-100">Base de Cidadãos</h4>
              </div>
              <p class="text-sm text-gray-600 dark:text-slate-400 mt-1">
                {{ pinsResumoTexto }}
              </p>
              <p class="text-xs text-gray-500 dark:text-slate-500 mt-1">
                Pins azuis representam cidadãos cadastrados no CRM
              </p>
            </div>
          </div>

          <!-- Camada 2: Demandas -->
          <div
            @click="toggleCamada('demandas')"
            class="flex items-start gap-3 p-3 rounded-lg border-2 cursor-pointer transition-all"
            :class="[
              camadasAtivas.demandas
                ? 'border-red-500 bg-red-50 dark:bg-red-900/20'
                : 'border-gray-200 dark:border-slate-700 hover:border-red-300 dark:hover:border-red-700'
            ]"
          >
            <div class="flex-shrink-0 mt-0.5">
              <div
                class="w-5 h-5 rounded border-2 flex items-center justify-center transition-all"
                :class="[
                  camadasAtivas.demandas
                    ? 'bg-red-500 border-red-500'
                    : 'bg-white dark:bg-slate-700 border-gray-300 dark:border-slate-600'
                ]"
              >
                <svg
                  v-if="camadasAtivas.demandas"
                  class="w-3 h-3 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </div>

            <div class="flex-1">
              <div class="flex items-center gap-2">
                <Flame class="w-4 h-4 text-red-600 dark:text-red-400" />
                <h4 class="font-semibold text-gray-900 dark:text-slate-100">Zonas de Demanda</h4>
              </div>
              <p class="text-sm text-gray-600 dark:text-slate-400 mt-1">
                {{ demandasResumo }}
              </p>
              <p class="text-xs text-gray-500 dark:text-slate-500 mt-1">
                {{
                  agrupamentoDemandas === 'macrotema_bairro'
                    ? 'Um círculo por macrotema em cada bairro'
                    : 'Um círculo por macrotema (centróide no mapa)'
                }}
              </p>
            </div>
          </div>

          <!-- Legenda de Zonas de Calor -->
          <div v-if="camadasAtivas.demandas" class="pt-3 border-t border-gray-200 dark:border-slate-700">
            <p class="text-xs font-semibold text-gray-700 dark:text-slate-300 mb-2">{{ demandasLegendaTitulo }}</p>
            <div class="space-y-2 max-h-40 overflow-y-auto">
              <div
                v-for="zona in analyticsStore.zonasCalor"
                :key="zona.id"
                class="flex items-center justify-between text-xs"
              >
                <div class="flex items-center gap-2 min-w-0">
                  <div
                    class="w-3 h-3 rounded-full flex-shrink-0"
                    :style="{ backgroundColor: zona.cor }"
                  ></div>
                  <span class="text-gray-700 dark:text-slate-300 truncate">{{ demandasLegendaRotulo(zona) }}</span>
                </div>
                <span class="font-semibold text-gray-900 dark:text-slate-100 flex-shrink-0 ml-2">{{ zona.atendimentosPendentes }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Botão para Reabrir Painel -->
    <button
      v-if="!painelAberto"
      @click="painelAberto = true"
      class="absolute top-4 right-4 p-3 bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-gray-200 dark:border-slate-700 hover:bg-gray-50 dark:hover:bg-slate-700 transition-colors z-[1200]"
      title="Abrir Painel de Camadas"
    >
      <Layers class="w-5 h-5 text-primary-600 dark:text-primary-400" />
    </button>

    <!-- Legenda Flutuante Inferior -->
    <div class="absolute bottom-4 left-4 right-4 md:right-auto max-md:bottom-20 bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-gray-200 dark:border-slate-700 p-3 z-[1200]">
      <p class="text-xs font-semibold text-gray-700 dark:text-slate-300 mb-2">Inteligência Territorial</p>
      <div class="flex items-center gap-4 text-xs">
        <div class="flex items-center gap-1.5">
          <div class="w-3 h-3 bg-blue-500 rounded-full"></div>
          <span class="text-gray-600 dark:text-slate-400">Cidadãos</span>
        </div>
        <div class="flex items-center gap-1.5">
          <div class="w-3 h-3 bg-red-500 rounded-full opacity-50"></div>
          <span class="text-gray-600 dark:text-slate-400">Demandas</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Dark mode para o Leaflet */
:deep(.dark .leaflet-tile-pane) {
  filter: invert(90%) hue-rotate(180deg) brightness(95%);
}

:deep(.dark .leaflet-control-zoom) {
  filter: invert(100%) hue-rotate(180deg);
}

:deep(.leaflet-popup-content-wrapper) {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

:deep(.dark .leaflet-popup-content-wrapper) {
  background-color: rgb(30, 41, 59);
  color: rgb(248, 250, 252);
}

:deep(.leaflet-popup-tip) {
  background-color: white;
}

:deep(.dark .leaflet-popup-tip) {
  background-color: rgb(30, 41, 59);
}

/* Customização dos controles do Leaflet */
:deep(.leaflet-control-zoom a) {
  color: rgb(55, 65, 81);
}

:deep(.dark .leaflet-control-zoom a) {
  color: rgb(226, 232, 240);
}

/* Marcador customizado */
:deep(.custom-marker) {
  background: none;
  border: none;
}
</style>
