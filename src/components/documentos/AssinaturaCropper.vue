<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { X, Check, RotateCw, ZoomIn, ZoomOut, Crop } from 'lucide-vue-next'

interface Props {
  imageUrl: string
}

interface Emits {
  (e: 'confirm', croppedImage: string): void
  (e: 'cancel'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const canvasRef = ref<HTMLCanvasElement | null>(null)
let ctx: CanvasRenderingContext2D | null = null
let image: HTMLImageElement | null = null

const zoom = ref(1)
const rotation = ref(0)
const offsetX = ref(0)
const offsetY = ref(0)

let isDragging = false
let startX = 0
let startY = 0

onMounted(() => {
  if (canvasRef.value) {
    ctx = canvasRef.value.getContext('2d')
    image = new Image()
    image.onload = () => {
      drawImage()
    }
    image.src = props.imageUrl
  }
})

function drawImage() {
  if (!ctx || !canvasRef.value || !image) return

  const canvas = canvasRef.value
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  
  ctx.save()
  ctx.translate(canvas.width / 2 + offsetX.value, canvas.height / 2 + offsetY.value)
  ctx.rotate((rotation.value * Math.PI) / 180)
  ctx.scale(zoom.value, zoom.value)
  
  const imgWidth = image.width
  const imgHeight = image.height
  ctx.drawImage(image, -imgWidth / 2, -imgHeight / 2, imgWidth, imgHeight)
  
  ctx.restore()
}

function zoomIn() {
  zoom.value = Math.min(zoom.value + 0.1, 3)
  drawImage()
}

function zoomOut() {
  zoom.value = Math.max(zoom.value - 0.1, 0.5)
  drawImage()
}

function rotacionar() {
  rotation.value = (rotation.value + 90) % 360
  drawImage()
}

function resetar() {
  zoom.value = 1
  rotation.value = 0
  offsetX.value = 0
  offsetY.value = 0
  drawImage()
}

function handleMouseDown(e: MouseEvent) {
  isDragging = true
  startX = e.clientX - offsetX.value
  startY = e.clientY - offsetY.value
}

function handleMouseMove(e: MouseEvent) {
  if (!isDragging) return
  offsetX.value = e.clientX - startX
  offsetY.value = e.clientY - startY
  drawImage()
}

function handleMouseUp() {
  isDragging = false
}

function confirmar() {
  if (!canvasRef.value) return
  
  const croppedImage = canvasRef.value.toDataURL('image/png')
  emit('confirm', croppedImage)
}

function cancelar() {
  emit('cancel')
}
</script>

<template>
  <div class="fixed inset-0 bg-black bg-opacity-75 z-50 flex items-center justify-center p-4">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
          Editar Assinatura
        </h3>
        <button
          @click="cancelar"
          class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded transition-colors"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- Toolbar -->
      <div class="flex items-center gap-2 p-3 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
        <button
          @click="zoomIn"
          class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
          title="Aumentar zoom"
        >
          <ZoomIn class="w-4 h-4 text-gray-700 dark:text-gray-300" />
        </button>
        
        <button
          @click="zoomOut"
          class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
          title="Diminuir zoom"
        >
          <ZoomOut class="w-4 h-4 text-gray-700 dark:text-gray-300" />
        </button>

        <button
          @click="rotacionar"
          class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
          title="Rotacionar 90°"
        >
          <RotateCw class="w-4 h-4 text-gray-700 dark:text-gray-300" />
        </button>

        <button
          @click="resetar"
          class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-colors"
          title="Resetar"
        >
          <Crop class="w-4 h-4 text-gray-700 dark:text-gray-300" />
        </button>

        <div class="ml-auto text-sm text-gray-600 dark:text-gray-400">
          Arraste para reposicionar • Zoom: {{ Math.round(zoom * 100) }}%
        </div>
      </div>

      <!-- Canvas Area -->
      <div class="flex-1 overflow-auto p-4 bg-gray-100 dark:bg-slate-900 flex items-center justify-center">
        <canvas
          ref="canvasRef"
          width="800"
          height="400"
          class="max-w-full border-2 border-dashed border-gray-300 dark:border-gray-600 cursor-move bg-white"
          @mousedown="handleMouseDown"
          @mousemove="handleMouseMove"
          @mouseup="handleMouseUp"
          @mouseleave="handleMouseUp"
        />
      </div>

      <!-- Footer -->
      <div class="flex items-center justify-end gap-3 p-4 border-t border-gray-200 dark:border-gray-700">
        <button
          @click="cancelar"
          class="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
        >
          Cancelar
        </button>
        <button
          @click="confirmar"
          class="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors"
        >
          <Check class="w-4 h-4" />
          Confirmar
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
canvas {
  image-rendering: high-quality;
}
</style>
