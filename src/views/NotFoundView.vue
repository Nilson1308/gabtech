<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="text-center">
      <h1 class="text-9xl font-bold text-primary-600">404</h1>
      <p class="text-2xl font-semibold text-gray-900 mt-4">Página não encontrada</p>
      <p class="text-gray-600 mt-2">A página que você está procurando não existe.</p>
      <button 
        @click="goHome"
        class="btn btn-primary mt-6"
      >
        Voltar para o início
      </button>
    </div>
  </div>
</template>
