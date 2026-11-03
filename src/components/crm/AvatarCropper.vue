<script setup lang="ts">
import { ref, computed } from 'vue'
import Modal from '@/components/common/Modal.vue'
import Button from '@/components/common/Button.vue'
import { Check } from 'lucide-vue-next'

interface Props {
  modelValue: boolean
  imageUrl: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  crop: [dataUrl: string]
}>()

// Estados para zoom e posição (CSS-based cropper)
const zoom = ref(1)
const posX = ref(50)
const posY = ref(50)
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })

// Style computado para a imagem
const imageStyle = computed(() => ({
  transform: `scale(${zoom.value}) translate(${posX.value - 50}%, ${posY.value - 50}%)`,
  transformOrigin: 'center center'
}))

// Handlers de zoom
const zoomIn = () => {
  zoom.value = Math.min(zoom.value + 0.1, 3)
}

const zoomOut = () => {
  zoom.value = Math.max(zoom.value - 0.1, 0.5)
}

const reset = () => {
  zoom.value = 1
  posX.value = 50
  posY.value = 50
}

// Handlers de drag
const startDrag = (e: MouseEvent) => {
  isDragging.value = true
  dragStart.value = { x: e.clientX, y: e.clientY }
}

const onDrag = (e: MouseEvent) => {
  if (!isDragging.value) return
  
  const deltaX = (e.clientX - dragStart.value.x) / 2
  const deltaY = (e.clientY - dragStart.value.y) / 2
  
  posX.value += deltaX
  posY.value += deltaY
  
  dragStart.value = { x: e.clientX, y: e.clientY }
}

const stopDrag = () => {
  isDragging.value = false
}

// Aplicar: renderizar canvas e exportar imagem cropada real
const aplicar = () => {
  if (!props.imageUrl) return

  const img = new Image()
  img.crossOrigin = 'anonymous'
  
  img.onload = () => {
    // Criar canvas 300x300 (tamanho do avatar final)
    const canvas = document.createElement('canvas')
    const size = 300
    canvas.width = size
    canvas.height = size
    const ctx = canvas.getContext('2d')
    
    if (!ctx) {
      emit('crop', props.imageUrl)
      fechar()
      return
    }

    // Dimensões originais da imagem
    const imgWidth = img.naturalWidth || img.width
    const imgHeight = img.naturalHeight || img.height
    
    // Calcular scale para preencher o círculo (min dimension determina o tamanho base)
    const minDimension = Math.min(imgWidth, imgHeight)
    
    // Aplicar zoom: quanto maior o zoom, mais "perto" a imagem fica
    // zoom.value varia de 0.5 a 3.0
    const scaleFactor = zoom.value
    
    // Tamanho da área visível da imagem após o zoom
    // Quanto maior o zoom, menor a área visível (mais próximo)
    const visibleSize = minDimension / scaleFactor
    
    // Converter posições de percentual (0-100) para pixels
    // posX e posY indicam o centro da área visível
    // Normalizar para que 50,50 seja o centro da imagem
    const centerX = imgWidth / 2
    const centerY = imgHeight / 2
    
    // Calcular offset do centro baseado em posX e posY
    // Valores negativos de (posX - 50) movem para esquerda, positivos para direita
    const offsetX = ((posX.value - 50) / 100) * (imgWidth - visibleSize)
    const offsetY = ((posY.value - 50) / 100) * (imgHeight - visibleSize)
    
    // Calcular coordenadas de origem do crop na imagem original
    const cropX = Math.max(0, Math.min(centerX - visibleSize / 2 + offsetX, imgWidth - visibleSize))
    const cropY = Math.max(0, Math.min(centerY - visibleSize / 2 + offsetY, imgHeight - visibleSize))
    
    // Desenhar no canvas com clip circular
    ctx.save()
    
    // Criar máscara circular
    ctx.beginPath()
    ctx.arc(size / 2, size / 2, size / 2, 0, Math.PI * 2)
    ctx.closePath()
    ctx.clip()
    
    // Preencher fundo branco
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, size, size)
    
    // Desenhar a área cropada da imagem escalada para preencher o canvas
    ctx.drawImage(
      img,
      cropX,                    // sx: início X na imagem original
      cropY,                    // sy: início Y na imagem original
      visibleSize,              // sWidth: largura da área a ser cropada
      visibleSize,              // sHeight: altura da área a ser cropada
      0,                        // dx: posição X no canvas
      0,                        // dy: posição Y no canvas
      size,                     // dWidth: largura final no canvas
      size                      // dHeight: altura final no canvas
    )
    
    ctx.restore()
    
    // Exportar como JPEG base64
    const croppedDataUrl = canvas.toDataURL('image/jpeg', 0.92)
    emit('crop', croppedDataUrl)
    fechar()
  }
  
  img.onerror = () => {
    // Fallback: retornar imagem original se houver erro
    emit('crop', props.imageUrl)
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
    @update:model-value="fechar"
    titulo="Ajustar Foto"
    largura="lg"
  >
    <div class="space-y-6">
      <!-- Preview Circular com Zoom e Pan -->
      <div class="flex justify-center">
        <div 
          class="relative w-64 h-64 rounded-full overflow-hidden bg-gray-100 dark:bg-slate-800 border-4 border-gray-200 dark:border-slate-700 cursor-move"
          @mousedown="startDrag"
          @mousemove="onDrag"
          @mouseup="stopDrag"
          @mouseleave="stopDrag"
        >
          <img
            :src="imageUrl"
            alt="Preview"
            class="w-full h-full object-cover transition-transform duration-200"
            :style="imageStyle"
            draggable="false"
          />
        </div>
      </div>

      <!-- Instrução -->
      <div class="text-center">
        <p class="text-sm text-gray-600 dark:text-slate-400">
          🖱️ Arraste a imagem para posicionar | 🔍 Use os botões para ajustar o zoom
        </p>
      </div>

      <!-- Controles de Zoom -->
      <div class="flex items-center justify-center gap-4">
        <button
          @click="zoomOut"
          type="button"
          class="px-4 py-2 bg-white dark:bg-slate-700 border border-gray-300 dark:border-slate-600 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-600 transition-colors text-sm font-medium"
          :disabled="zoom <= 0.5"
        >
          Zoom -
        </button>

        <div class="text-sm font-medium text-gray-700 dark:text-slate-300 min-w-16 text-center">
          {{ Math.round(zoom * 100) }}%
        </div>

        <button
          @click="zoomIn"
          type="button"
          class="px-4 py-2 bg-white dark:bg-slate-700 border border-gray-300 dark:border-slate-600 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-600 transition-colors text-sm font-medium"
          :disabled="zoom >= 3"
        >
          Zoom +
        </button>

        <button
          @click="reset"
          type="button"
          class="px-4 py-2 text-sm text-gray-600 dark:text-slate-400 hover:text-gray-900 dark:hover:text-slate-200 transition-colors"
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
        Confirmar
      </Button>
    </template>
  </Modal>
</template>

<style scoped>
.cursor-move {
  cursor: move;
  user-select: none;
  -webkit-user-select: none;
}
</style>
