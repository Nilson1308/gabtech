import 'vue-router'

declare module 'vue-router' {
  interface RouteMeta {
    /** Título exibido no header principal (substitui «GabTech»). */
    headerTitle?: string
  }
}
