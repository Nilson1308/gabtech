import type { Directive } from 'vue'
import { useAuthStore } from '@/stores/auth'

/**
 * Controle de visibilidade por permissão RBAC (codenames do backend, ex.: criar_crm).
 * Uso: v-permission="PERMS.crmCreate" ou v-permission="['criar_crm', 'editar_crm']"
 */
export const vPermission: Directive = {
  mounted(el, binding) {
    const authStore = useAuthStore()
    const required = Array.isArray(binding.value) ? binding.value : [binding.value]

    const allowed = required.some((permission: string) => authStore.hasPermission(permission))

    if (!allowed) {
      el.remove()
    }
  },
}
