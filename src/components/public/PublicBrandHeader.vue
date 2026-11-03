<script setup lang="ts">
defineProps<{
  subtitle?: string
}>()
</script>

<template>
  <div class="flex flex-col items-center gap-1">
    <img
      src="/logo_gt_tema_claro.png"
      alt="GabTech"
      class="h-10 w-auto object-contain"
    />
    <p v-if="subtitle" class="text-xs text-gray-500 dark:text-gray-400">
      {{ subtitle }}
    </p>
  </div>
</template>
