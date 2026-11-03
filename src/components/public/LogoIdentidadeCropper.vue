<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import Modal from '@/components/common/Modal.vue'
import Button from '@/components/common/Button.vue'
import { Check } from 'lucide-vue-next'
import {
  LOGO_FORMATOS,
  logoAspectRatio,
  logoOutputSize,
  type LogoFormato,
} from '@/constants/logoIdentidade'

interface Props {
  modelValue: boolean
  imageUrl: string
  formatoInicial?: LogoFormato
}

const props = withDefaults(defineProps<Props>(), {
  formatoInicial: '1:1',
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  crop: [payload: { dataUrl: string; formato: LogoFormato }]
}>()

const formato = ref<LogoFormato>(props.formatoInicial)
const naturalW = ref(0)
const naturalH = ref(0)

watch(
  () => props.modelValue,
  (aberto) => {
    if (aberto) {
      formato.value = props.formatoInicial
      resetTransform()
    }
  },
)

watch(
  () => props.imageUrl,
  () => {
    naturalW.value = 0
    naturalH.value = 0
  },
)

const aspectRatio = computed(() => logoAspectRatio(formato.value))

const viewport = computed(() => {
  const ar = aspectRatio.value
  const maxPx = 288
  if (ar >= 1) {
    return { w: maxPx, h: Math.round(maxPx / ar) }
  }
  return { w: Math.round(maxPx * ar), h: maxPx }
})

const previewBoxStyle = computed(() => ({
  width: `${viewport.value.w}px`,
  height: `${viewport.value.h}px`,
}))

const zoom = ref(1)
/** Deslocamento em px (arraste); 0 = centralizado. */
const panX = ref(0)
const panY = ref(0)

const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0, panX: 0, panY: 0 })

function onMetaLoad(event: Event) {
  const img = event.target as HTMLImageElement
  naturalW.value = img.naturalWidth
  naturalH.value = img.naturalHeight
}

/** Escala base: imagem cobre a moldura (cover) com zoom = 1. */
const imgLayout = computed(() => {
  const iw = naturalW.value
  const ih = naturalH.value
  if (!iw || !ih) return null

  const { w: vw, h: vh } = viewport.value
  const coverScale = Math.max(vw / iw, vh / ih)
  const displayScale = coverScale * zoom.value
  const imgW = iw * displayScale
  const imgH = ih * displayScale
  const maxPanX = Math.max(0, (imgW - vw) / 2)
  const maxPanY = Math.max(0, (imgH - vh) / 2)
  const px = Math.max(-maxPanX, Math.min(maxPanX, panX.value))
  const py = Math.max(-maxPanY, Math.min(maxPanY, panY.value))

  return {
    iw,
    ih,
    vw,
    vh,
    displayScale,
    imgW,
    imgH,
    left: (vw - imgW) / 2 + px,
    top: (vh - imgH) / 2 + py,
  }
})

const imageStyle = computed(() => {
  const L = imgLayout.value
  if (!L) {
    return { visibility: 'hidden' as const }
  }
  return {
    width: `${L.imgW}px`,
    height: `${L.imgH}px`,
    left: `${L.left}px`,
    top: `${L.top}px`,
  }
})

function resetTransform() {
  zoom.value = 1
  panX.value = 0
  panY.value = 0
}

const ZOOM_MIN = 0.25
const ZOOM_MAX = 3

const zoomIn = () => {
  zoom.value = Math.min(zoom.value + 0.1, ZOOM_MAX)
}

const zoomOut = () => {
  zoom.value = Math.max(zoom.value - 0.1, ZOOM_MIN)
}

const reset = () => {
  resetTransform()
}

watch(formato, () => {
  resetTransform()
})

const startDrag = (e: MouseEvent) => {
  isDragging.value = true
  dragStart.value = { x: e.clientX, y: e.clientY, panX: panX.value, panY: panY.value }
}

const onDrag = (e: MouseEvent) => {
  if (!isDragging.value) return
  panX.value = dragStart.value.panX + (e.clientX - dragStart.value.x)
  panY.value = dragStart.value.panY + (e.clientY - dragStart.value.y)
}

const stopDrag = () => {
  isDragging.value = false
}

function cropFromLayout(L: NonNullable<typeof imgLayout.value>) {
  const cropW = L.vw / L.displayScale
  const cropH = L.vh / L.displayScale
  let cropX = -L.left / L.displayScale
  let cropY = -L.top / L.displayScale
  return { cropX, cropY, cropW, cropH }
}

function desenharRecorte(
  ctx: CanvasRenderingContext2D,
  img: HTMLImageElement,
  L: NonNullable<typeof imgLayout.value>,
  outW: number,
  outH: number,
) {
  const { cropX, cropY, cropW, cropH } = cropFromLayout(L)
  const { iw, ih } = L

  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, outW, outH)

  const srcX = Math.max(0, cropX)
  const srcY = Math.max(0, cropY)
  const srcX2 = Math.min(iw, cropX + cropW)
  const srcY2 = Math.min(ih, cropY + cropH)
  if (srcX2 <= srcX || srcY2 <= srcY) return

  const destX = ((srcX - cropX) / cropW) * outW
  const destY = ((srcY - cropY) / cropH) * outH
  const destW = ((srcX2 - srcX) / cropW) * outW
  const destH = ((srcY2 - srcY) / cropH) * outH

  ctx.drawImage(img, srcX, srcY, srcX2 - srcX, srcY2 - srcY, destX, destY, destW, destH)
}

const aplicar = () => {
  if (!props.imageUrl) return

  const formatoAtual = formato.value
  const L = imgLayout.value
  const img = new Image()
  img.onload = () => {
    const { width: outW, height: outH } = logoOutputSize(formatoAtual)
    const canvas = document.createElement('canvas')
    canvas.width = outW
    canvas.height = outH
    const ctx = canvas.getContext('2d')
    if (!ctx || !L) {
      emit('crop', { dataUrl: props.imageUrl, formato: formatoAtual })
      fechar()
      return
    }

    desenharRecorte(ctx, img, L, outW, outH)
    emit('crop', { dataUrl: canvas.toDataURL('image/png', 0.92), formato: formatoAtual })
    fechar()
  }
  img.onerror = () => {
    emit('crop', { dataUrl: props.imageUrl, formato: formatoAtual })
    fechar()
  }
  img.src = props.imageUrl
}

const fechar = () => {
  reset()
  emit('update:modelValue', false)
}
</script>

<template>
  <Modal
    :model-value="modelValue"
    titulo="Ajustar logo ou brasão"
    largura="lg"
    @update:model-value="fechar"
  >
    <img
      :src="imageUrl"
      alt=""
      class="hidden"
      @load="onMetaLoad"
    >

    <div class="space-y-6">
      <div>
        <p class="text-sm font-medium text-gray-700 dark:text-slate-300 mb-2">
          Formato da imagem
        </p>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
          <button
            v-for="opt in LOGO_FORMATOS"
            :key="opt.id"
            type="button"
            class="rounded-lg border px-3 py-2 text-left text-sm transition-colors"
            :class="
              formato === opt.id
                ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/30 ring-1 ring-primary-500'
                : 'border-gray-300 dark:border-slate-600 hover:bg-gray-50 dark:hover:bg-slate-800'
            "
            @click="formato = opt.id"
          >
            <span class="font-medium text-gray-900 dark:text-slate-100">{{ opt.label }}</span>
            <span class="block text-xs text-gray-500 dark:text-slate-400 mt-0.5">{{ opt.descricao }}</span>
          </button>
        </div>
      </div>

      <div class="flex justify-center">
        <div
          class="viewport relative rounded-xl overflow-hidden bg-white dark:bg-slate-900 border-2 border-dashed border-gray-300 dark:border-slate-600 cursor-move shadow-inner"
          :style="previewBoxStyle"
          @mousedown="startDrag"
          @mousemove="onDrag"
          @mouseup="stopDrag"
          @mouseleave="stopDrag"
        >
          <img
            :src="imageUrl"
            alt="Preview"
            class="absolute max-w-none select-none pointer-events-none"
            :style="imageStyle"
            draggable="false"
          >
        </div>
      </div>

      <p class="text-sm text-center text-gray-600 dark:text-slate-400">
        Arraste para centralizar e use o zoom. Diminua o zoom para enquadrar a arte inteira; a moldura é o recorte (
        <strong>{{ formato }}</strong>).
      </p>

      <div class="flex items-center justify-center gap-4 flex-wrap">
        <button
          type="button"
          class="px-4 py-2 bg-white dark:bg-slate-700 border border-gray-300 dark:border-slate-600 rounded-lg text-sm font-medium"
          :disabled="zoom <= ZOOM_MIN"
          @click="zoomOut"
        >
          Zoom −
        </button>
        <span class="text-sm font-medium text-gray-700 dark:text-slate-300 min-w-16 text-center">
          {{ Math.round(zoom * 100) }}%
        </span>
        <button
          type="button"
          class="px-4 py-2 bg-white dark:bg-slate-700 border border-gray-300 dark:border-slate-600 rounded-lg text-sm font-medium"
          :disabled="zoom >= ZOOM_MAX"
          @click="zoomIn"
        >
          Zoom +
        </button>
        <button
          type="button"
          class="px-4 py-2 text-sm text-gray-600 dark:text-slate-400"
          @click="reset"
        >
          Resetar
        </button>
      </div>
    </div>

    <template #footer>
      <Button variant="secondary" @click="fechar">
        Cancelar
      </Button>
      <Button variant="primary" @click="aplicar">
        <Check class="w-4 h-4" />
        Usar esta imagem
      </Button>
    </template>
  </Modal>
</template>

<style scoped>
.viewport {
  cursor: move;
  user-select: none;
}
</style>
