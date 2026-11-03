<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

onMounted(() => {
  // Carregar usuário do localStorage ao iniciar a aplicação
  authStore.loadUserFromStorage()
})
</script>

<template>
  <RouterView />
</template>
