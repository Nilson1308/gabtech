declare module 'vue' {
  interface HTMLElementWithClickOutside extends HTMLElement {
    clickOutsideEvent?: (event: MouseEvent) => void
  }
}

export {}
