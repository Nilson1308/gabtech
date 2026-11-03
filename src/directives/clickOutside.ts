import type { Directive } from 'vue'

export const vClickOutside: Directive = {
  mounted(el, binding) {
    el.clickOutsideEvent = (event: MouseEvent) => {
      // Verifica se o clique foi fora do elemento
      if (!(el === event.target || el.contains(event.target as Node))) {
        // Chama a função passada como valor da diretiva
        binding.value(event)
      }
    }
    document.addEventListener('click', el.clickOutsideEvent)
  },
  unmounted(el) {
    document.removeEventListener('click', el.clickOutsideEvent)
  }
}
