import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './style.css'

// Diretivas customizadas
import { vPermission } from './directives/permission'
import { vClickOutside } from './directives/clickOutside'

const app = createApp(App)
const pinia = createPinia()

// Registrar Pinia e Router
app.use(pinia)
app.use(router)

// Registrar diretivas globais
app.directive('permission', vPermission)
app.directive('click-outside', vClickOutside)

app.mount('#app')
