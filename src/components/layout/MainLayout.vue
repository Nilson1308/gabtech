<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Sidebar from './Sidebar.vue'
import Header from './Header.vue'
import AlertDialog from '@/components/common/AlertDialog.vue'
import { useAlertDialog } from '@/composables/useAlertDialog'

const sidebarAberta = ref(false)
const alertDialogRef = ref()

const toggleSidebar = () => {
  sidebarAberta.value = !sidebarAberta.value
}

const { setRef } = useAlertDialog()

onMounted(() => {
  setRef(alertDialogRef.value)
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-slate-900 flex">
    <!-- Sidebar -->
    <Sidebar v-model="sidebarAberta" />

    <!-- Área Principal -->
    <div class="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
      <!-- Header -->
      <Header @toggle-sidebar="toggleSidebar" class="flex-shrink-0" />

      <!-- Conteúdo -->
      <main class="flex-1 p-4 lg:p-6 overflow-y-auto bg-gray-50 dark:bg-slate-900">
        <div class="max-w-7xl mx-auto">
          <RouterView />
        </div>
      </main>
    </div>

    <!-- AlertDialog Global -->
    <AlertDialog ref="alertDialogRef" />
  </div>
</template>
