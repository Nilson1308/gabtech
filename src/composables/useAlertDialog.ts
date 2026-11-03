import { ref } from 'vue'
import type { AlertDialogOptions } from '@/components/common/AlertDialog.vue'

const alertDialogRef = ref<any>(null)

export function useAlertDialog() {
  function setRef(ref: any) {
    alertDialogRef.value = ref
  }

  async function showAlert(message: string, title?: string, type: AlertDialogOptions['type'] = 'info') {
    if (!alertDialogRef.value) {
      console.warn('AlertDialog não está montado. Usando alert() padrão.')
      alert(message)
      return
    }

    return alertDialogRef.value.show({
      title,
      message,
      type,
      confirmText: 'OK'
    })
  }

  async function showConfirm(message: string, title?: string) {
    if (!alertDialogRef.value) {
      console.warn('AlertDialog não está montado. Usando confirm() padrão.')
      return confirm(message)
    }

    return alertDialogRef.value.show({
      title: title || 'Confirmar',
      message,
      type: 'confirm',
      confirmText: 'Confirmar',
      cancelText: 'Cancelar'
    })
  }

  async function showSuccess(message: string, title?: string) {
    return showAlert(message, title || 'Sucesso', 'success')
  }

  async function showError(message: string, title?: string) {
    return showAlert(message, title || 'Erro', 'error')
  }

  async function showWarning(message: string, title?: string) {
    return showAlert(message, title || 'Atenção', 'warning')
  }

  async function showInfo(message: string, title?: string) {
    return showAlert(message, title || 'Informação', 'info')
  }

  return {
    setRef,
    showAlert,
    showConfirm,
    showSuccess,
    showError,
    showWarning,
    showInfo
  }
}
