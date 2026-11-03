<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAgendaStore } from '@/stores/agenda'
import { useAuthStore } from '@/stores/auth'
import { PERMS } from '@/constants/rbac'
import type { Evento } from '@/stores/agenda'
import Button from '@/components/common/Button.vue'
import EventoModal from '@/components/agenda/EventoModal.vue'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import listPlugin from '@fullcalendar/list'
import ptBrLocale from '@fullcalendar/core/locales/pt-br'
import type { CalendarOptions, DateSelectArg, EventClickArg } from '@fullcalendar/core'
import { 
  Plus, 
  Calendar,
  MapPin,
  X,
  Filter
} from 'lucide-vue-next'

const router = useRouter()
const agendaStore = useAgendaStore()
const authStore = useAuthStore()

// Estado
const mostrarModalEvento = ref(false)
const eventoEditando = ref<Evento | null>(null)
const mostrarFiltros = ref(true)
const isDarkMode = ref(false)

// Filtros (usando ref para garantir reatividade)
const filtrosTipos = ref<string[]>([])
const filtrosEspacos = ref<string[]>([])
const fullCalendarRef = ref<InstanceType<typeof FullCalendar> | null>(null)

const tiposAtivosIds = computed(() => agendaStore.tiposEventoAtivos.map(t => t.id))
const espacosAtivosIds = computed(() => agendaStore.espacosAtivos.map(e => e.id))

// Computed
const eventosFiltrados = computed(() => {
  const tiposIds = tiposAtivosIds.value
  const espacosIds = espacosAtivosIds.value

  return agendaStore.eventos.filter(evento => {
    if (evento.status !== 'agendado') return false

    // Nenhum tipo marcado → não exibe eventos (checkbox = inclusão)
    if (tiposIds.length > 0) {
      if (filtrosTipos.value.length === 0) return false
      if (!filtrosTipos.value.includes(evento.tipoId)) return false
    }

    // Nenhum espaço marcado → não exibe eventos com espaço; sem espaço continua visível
    if (espacosIds.length > 0) {
      if (filtrosEspacos.value.length === 0) {
        return !evento.espacoId
      }
      if (evento.espacoId && !filtrosEspacos.value.includes(evento.espacoId)) {
        return false
      }
    }

    return true
  })
})

// Mapear eventos para formato FullCalendar
const eventosFullCalendar = computed(() => {
  return eventosFiltrados.value.map(evento => {
    const tipo = agendaStore.getTipoEventoById(evento.tipoId)
    const cor = tipo?.cor || '#6b7280'
    
    // Converter data e horários para ISO string
    const horaInicio = evento.horaInicio.length === 5 ? `${evento.horaInicio}:00` : evento.horaInicio
    const horaFim = evento.horaFim.length === 5 ? `${evento.horaFim}:00` : evento.horaFim

    return {
      id: evento.id,
      title: evento.titulo,
      start: `${evento.data}T${horaInicio}`,
      end: `${evento.data}T${horaFim}`,
      backgroundColor: cor,
      borderColor: cor,
      textColor: '#ffffff',
      extendedProps: {
        descricao: evento.descricao,
        espacoId: evento.espacoId,
        tipoId: evento.tipoId,
        convidadosIds: evento.convidadosIds
      }
    }
  })
})

function sincronizarEventosCalendario() {
  const calendar = fullCalendarRef.value?.getApi()
  if (!calendar) return

  calendar.removeAllEvents()
  for (const evento of eventosFullCalendar.value) {
    calendar.addEvent(evento)
  }
}

const handleEventClick = (clickInfo: EventClickArg) => {
  const eventoOriginal = agendaStore.eventos.find(e => e.id === clickInfo.event.id)
  if (eventoOriginal) {
    const tipoEvento = agendaStore.tiposEventoAtivos.find(t => t.id === eventoOriginal.tipoId)
    const tiposEspeciais = ['cerimonial', 'audiencia', 'sessao']

    if (tipoEvento && tiposEspeciais.some(t => tipoEvento.nome.toLowerCase().includes(t))) {
      router.push(`/eventos/evento-1`)
    } else {
      abrirEdicaoEvento(eventoOriginal)
    }
  }
}

const handleDateSelect = (selectInfo: DateSelectArg) => {
  eventoEditando.value = null

  const start = selectInfo.start
  const ano = start.getFullYear()
  const mes = String(start.getMonth() + 1).padStart(2, '0')
  const dia = String(start.getDate()).padStart(2, '0')
  const hora = String(start.getHours()).padStart(2, '0')
  const minuto = String(start.getMinutes()).padStart(2, '0')

  localStorage.setItem('novoEventoData', `${ano}-${mes}-${dia}`)
  localStorage.setItem('novoEventoHora', `${hora}:${minuto}`)

  mostrarModalEvento.value = true
  selectInfo.view.calendar.unselect()
}

// FullCalendar Options (eventos sincronizados via watch — resetOptions nem sempre reflete filtros)
const calendarOptions: CalendarOptions = {
  plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin, listPlugin],
  initialView: 'dayGridMonth',
  locale: ptBrLocale,
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,timeGridWeek,timeGridDay,listWeek'
  },
  buttonText: {
    today: 'Hoje',
    month: 'Mês',
    week: 'Semana',
    day: 'Dia',
    list: 'Lista'
  },
  slotMinTime: '07:00:00',
  slotMaxTime: '20:00:00',
  expandRows: true,
  height: 'auto',
  contentHeight: 650,
  nowIndicator: true,
  weekends: true,
  editable: false,
  selectable: true,
  selectMirror: true,
  dayMaxEvents: true,
  navLinks: true,
  businessHours: {
    daysOfWeek: [1, 2, 3, 4, 5],
    startTime: '08:00',
    endTime: '18:00'
  },
  events: [],
  eventDisplay: 'block',
  displayEventTime: true,
  displayEventEnd: true,
  eventTimeFormat: {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  },
  eventClick: handleEventClick,
  select: handleDateSelect,
}

function inicializarFiltros() {
  filtrosTipos.value = [...tiposAtivosIds.value]
  filtrosEspacos.value = [...espacosAtivosIds.value]
}

watch(
  [eventosFullCalendar, () => fullCalendarRef.value],
  () => {
    sincronizarEventosCalendario()
  },
  { flush: 'post', deep: true },
)

watch([tiposAtivosIds, espacosAtivosIds], () => {
  if (filtrosTipos.value.length === 0 && tiposAtivosIds.value.length > 0) {
    filtrosTipos.value = [...tiposAtivosIds.value]
  } else {
    const novosTipos = tiposAtivosIds.value.filter(id => !filtrosTipos.value.includes(id))
    if (novosTipos.length) {
      filtrosTipos.value = [...filtrosTipos.value, ...novosTipos]
    }
    filtrosTipos.value = filtrosTipos.value.filter(id => tiposAtivosIds.value.includes(id))
  }

  if (filtrosEspacos.value.length === 0 && espacosAtivosIds.value.length > 0) {
    filtrosEspacos.value = [...espacosAtivosIds.value]
  } else {
    const novosEspacos = espacosAtivosIds.value.filter(id => !filtrosEspacos.value.includes(id))
    if (novosEspacos.length) {
      filtrosEspacos.value = [...filtrosEspacos.value, ...novosEspacos]
    }
    filtrosEspacos.value = filtrosEspacos.value.filter(id => espacosAtivosIds.value.includes(id))
  }
})

// Carregar dados
onMounted(async () => {
  await agendaStore.initialize()

  inicializarFiltros()
  await nextTick()
  sincronizarEventosCalendario()
  
  // Detectar dark mode inicial
  isDarkMode.value = document.documentElement.classList.contains('dark')
  
  // Observer para mudanças no dark mode
  const observer = new MutationObserver(() => {
    isDarkMode.value = document.documentElement.classList.contains('dark')
  })
  
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ['class']
  })
})

// Methods
const abrirNovoEvento = () => {
  eventoEditando.value = null
  localStorage.removeItem('novoEventoData')
  localStorage.removeItem('novoEventoHora')
  mostrarModalEvento.value = true
}

const abrirEdicaoEvento = (evento: Evento) => {
  eventoEditando.value = evento
  mostrarModalEvento.value = true
}

</script>

<template>
  <div class="flex gap-6 h-full">
    <!-- Sidebar de Filtros -->
    <aside
      v-if="mostrarFiltros"
      class="w-64 flex-shrink-0 space-y-6"
    >
      <!-- Resumo / Big Number -->
      <div class="card bg-gradient-to-br from-primary-500 to-primary-600 dark:from-primary-600 dark:to-primary-700 border-0 text-white">
        <div class="flex items-center justify-between mb-2">
          <h3 class="text-sm font-medium opacity-90">Eventos Filtrados</h3>
          <button
            @click="mostrarFiltros = false"
            class="lg:hidden text-white/80 hover:text-white"
          >
            <X class="w-4 h-4" />
          </button>
        </div>
        <p class="text-4xl font-bold mb-1">{{ eventosFiltrados.length }}</p>
        <p class="text-sm opacity-90">{{ eventosFiltrados.length === 1 ? 'evento' : 'eventos' }}</p>
      </div>

      <!-- Filtros por Tipo -->
      <div class="card">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-gray-900 dark:text-slate-100 flex items-center gap-2">
            <Filter class="w-4 h-4" />
            Tipo de Evento
          </h3>
        </div>
        <div class="space-y-2">
          <label
            v-for="tipo in agendaStore.tiposEventoAtivos"
            :key="tipo.id"
            class="flex items-center gap-2 cursor-pointer group"
          >
            <input
              type="checkbox"
              v-model="filtrosTipos"
              :value="tipo.id"
              class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-slate-700 dark:border-slate-600 cursor-pointer"
            />
            <div class="flex items-center gap-2 flex-1">
              <div
                class="w-3 h-3 rounded-full flex-shrink-0"
                :style="{ backgroundColor: tipo.cor }"
              ></div>
              <span class="text-sm text-gray-700 dark:text-slate-300 group-hover:text-gray-900 dark:group-hover:text-slate-100">
                {{ tipo.nome }}
              </span>
            </div>
          </label>
        </div>
      </div>

      <!-- Filtros por Espaço -->
      <div class="card">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-gray-900 dark:text-slate-100 flex items-center gap-2">
            <MapPin class="w-4 h-4" />
            Espaços
          </h3>
        </div>
        <div class="space-y-2">
          <label
            v-for="espaco in agendaStore.espacosAtivos"
            :key="espaco.id"
            class="flex items-center gap-2 cursor-pointer group"
          >
            <input
              type="checkbox"
              v-model="filtrosEspacos"
              :value="espaco.id"
              class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-slate-700 dark:border-slate-600 cursor-pointer"
            />
            <span class="text-sm text-gray-700 dark:text-slate-300 group-hover:text-gray-900 dark:group-hover:text-slate-100">
              {{ espaco.nome }}
            </span>
          </label>
        </div>
      </div>
    </aside>

    <!-- Área Principal -->
    <div class="flex-1 space-y-6 min-w-0">
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div class="flex items-center gap-3">
          <button
            v-if="!mostrarFiltros"
            @click="mostrarFiltros = true"
            class="lg:hidden p-2 hover:bg-gray-100 dark:hover:bg-slate-700 rounded-lg"
          >
            <Filter class="w-5 h-5 text-gray-600 dark:text-slate-400" />
          </button>
          <div>
            <h2 class="text-2xl font-bold text-gray-900 dark:text-slate-100 flex items-center gap-2">
              <Calendar class="w-7 h-7" />
              Agenda Oficial
            </h2>
            <p class="text-sm text-gray-600 dark:text-slate-400 mt-1">
              Visualize eventos em grade de horários
            </p>
          </div>
        </div>

        <Button
          v-if="authStore.hasPermission(PERMS.agendaCreate)"
          variant="primary"
          @click="abrirNovoEvento"
        >
          <Plus class="w-4 h-4" />
          Novo Evento
        </Button>
      </div>

      <!-- FullCalendar -->
      <div class="card p-6" :class="{ 'calendar-dark': isDarkMode }">
        <FullCalendar ref="fullCalendarRef" :options="calendarOptions as any" />
      </div>

      <!-- Empty State (só quando já há eventos na store, mas nenhum passa no filtro) -->
      <div
        v-if="agendaStore.eventos.some(e => e.status === 'agendado') && eventosFiltrados.length === 0"
        class="card text-center py-12"
      >
        <Calendar class="w-16 h-16 text-gray-300 dark:text-slate-600 mx-auto mb-4" />
        <h3 class="text-lg font-semibold text-gray-900 dark:text-slate-100 mb-2">
          Nenhum evento encontrado
        </h3>
        <p class="text-sm text-gray-600 dark:text-slate-400 mb-4">
          Não há eventos com os filtros selecionados
        </p>
        <Button
          v-if="authStore.hasPermission(PERMS.agendaCreate)"
          variant="primary"
          @click="abrirNovoEvento"
        >
          <Plus class="w-4 h-4" />
          Criar Primeiro Evento
        </Button>
      </div>
    </div>

    <!-- Modal de Evento -->
    <EventoModal
      v-model="mostrarModalEvento"
      :evento="eventoEditando"
      @saved="() => { mostrarModalEvento = false; sincronizarEventosCalendario() }"
      @deleted="() => { mostrarModalEvento = false; sincronizarEventosCalendario() }"
    />
  </div>
</template>

<style>
/* ========================================
   FULLCALENDAR PREMIUM - DARK/LIGHT MODE
   ======================================== */

/* Card container light/dark */
.card:has(.fc) {
  background: white !important;
  border: 1px solid #e2e8f0 !important;
}

.calendar-dark.card {
  background: #0f172a !important;
  border: 1px solid #1e293b !important;
}

/* ===== LIGHT MODE ===== */
:root {
  --fc-border-color: #e2e8f0;
  --fc-button-bg-color: #3b82f6;
  --fc-button-border-color: #3b82f6;
  --fc-button-hover-bg-color: #2563eb;
  --fc-button-hover-border-color: #2563eb;
  --fc-button-active-bg-color: #1d4ed8;
  --fc-button-active-border-color: #1d4ed8;
  --fc-event-bg-color: #3b82f6;
  --fc-event-border-color: #3b82f6;
  --fc-event-text-color: #ffffff;
  --fc-today-bg-color: rgba(59, 130, 246, 0.1);
}

/* Container */
.fc {
  font-family: inherit !important;
  background: white !important;
}

.fc * {
  border-color: #e2e8f0 !important;
}

/* Header Toolbar */
.fc .fc-toolbar {
  padding: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 0.75rem 0.75rem 0 0;
  margin-bottom: 0 !important;
}

.fc .fc-toolbar-title {
  font-size: 1.5rem !important;
  font-weight: 700 !important;
  color: white !important;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Buttons */
.fc .fc-button {
  background: rgba(255, 255, 255, 0.2) !important;
  border: none !important;
  color: white !important;
  font-weight: 600 !important;
  padding: 0.5rem 1rem !important;
  border-radius: 0.5rem !important;
  transition: all 0.2s !important;
  text-transform: capitalize !important;
}

.fc .fc-button:hover {
  background: rgba(255, 255, 255, 0.3) !important;
  transform: translateY(-1px);
}

.fc .fc-button:active,
.fc .fc-button-active {
  background: rgba(255, 255, 255, 0.4) !important;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1) !important;
}

.fc .fc-button:disabled {
  opacity: 0.4 !important;
  cursor: not-allowed !important;
}

/* View Container */
.fc .fc-view-harness {
  background: white !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 0 0 0.75rem 0.75rem !important;
}

.fc .fc-scrollgrid {
  background: white !important;
  border-color: #e2e8f0 !important;
}

.fc .fc-scrollgrid-section > * {
  background: white !important;
}

.fc table {
  background: white !important;
}

/* Weekday Headers */
.fc .fc-col-header-cell {
  background: #f8fafc !important;
  border-color: #e2e8f0 !important;
  padding: 0.75rem 0.5rem !important;
}

.fc .fc-col-header-cell-cushion {
  color: #475569 !important;
  font-weight: 700 !important;
  font-size: 0.875rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
  text-decoration: none !important;
}

/* Day Cells */
.fc .fc-daygrid-day {
  background: white !important;
  border-color: #e2e8f0 !important;
  transition: background-color 0.15s !important;
}

.fc .fc-daygrid-day:hover {
  background: #f8fafc !important;
  cursor: pointer !important;
}

.fc .fc-daygrid-day.fc-day-today {
  background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%) !important;
}

.fc .fc-daygrid-day-number {
  color: #1e293b !important;
  font-weight: 600 !important;
  padding: 0.5rem !important;
  text-decoration: none !important;
}

.fc .fc-day-today .fc-daygrid-day-number {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
  color: white !important;
  border-radius: 50% !important;
  width: 2rem !important;
  height: 2rem !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  font-weight: 700 !important;
  box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3) !important;
}

/* Time Grid */
.fc .fc-timegrid-slot {
  border-color: #f1f5f9 !important;
  height: 3rem !important;
}

.fc .fc-timegrid-slot-label {
  color: #64748b !important;
  font-size: 0.75rem !important;
  font-weight: 600 !important;
  border-color: #e2e8f0 !important;
}

.fc .fc-timegrid-col {
  background: white !important;
  border-color: #e2e8f0 !important;
}

.fc .fc-timegrid-col.fc-day-today {
  background: rgba(59, 130, 246, 0.05) !important;
}

.fc .fc-timegrid-now-indicator-line {
  border-color: #ef4444 !important;
  border-width: 2px !important;
}

.fc .fc-timegrid-now-indicator-arrow {
  border-color: #ef4444 !important;
}

/* Events - CORES VIBRANTES */
.fc .fc-event {
  border: none !important;
  border-radius: 0.5rem !important;
  padding: 0.25rem 0.5rem !important;
  font-weight: 600 !important;
  cursor: pointer !important;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15) !important;
  transition: all 0.2s !important;
  border-left: 4px solid rgba(255, 255, 255, 0.5) !important;
  margin: 2px !important;
}

.fc .fc-event:hover {
  transform: translateY(-2px) scale(1.02) !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25) !important;
  filter: brightness(1.1) !important;
}

.fc .fc-event-title {
  font-weight: 700 !important;
  font-size: 0.875rem !important;
  color: white !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2) !important;
}

.fc .fc-event-time {
  font-weight: 600 !important;
  font-size: 0.75rem !important;
  color: white !important;
  opacity: 0.95 !important;
}

.fc .fc-daygrid-event-dot {
  display: none !important;
}

/* List View */
.fc .fc-list-event:hover td {
  background: #f8fafc !important;
}

.fc .fc-list-event-title {
  color: #1e293b !important;
  font-weight: 600 !important;
}

.fc .fc-list-event-time {
  color: #64748b !important;
}

/* Popover */
.fc .fc-popover {
  background: white !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 0.5rem !important;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1) !important;
}

.fc .fc-popover-header {
  background: #f8fafc !important;
  padding: 0.75rem 1rem !important;
  font-weight: 600 !important;
  color: #1e293b !important;
}

/* ========================================
   DARK MODE - COMPLETO
   ======================================== */

/* Container Dark */
.calendar-dark .fc {
  background: #0f172a !important;
}

.calendar-dark .fc * {
  border-color: #1e293b !important;
}

/* Toolbar Dark */
.calendar-dark .fc .fc-toolbar {
  background: linear-gradient(135deg, #1e40af 0%, #7c3aed 100%) !important;
}

/* View Container Dark */
.calendar-dark .fc .fc-view-harness {
  background: #0f172a !important;
  border-color: #1e293b !important;
}

.calendar-dark .fc .fc-scrollgrid {
  background: #0f172a !important;
  border-color: #1e293b !important;
}

.calendar-dark .fc .fc-scrollgrid-section {
  background: #0f172a !important;
}

.calendar-dark .fc .fc-scrollgrid-section > * {
  background: #0f172a !important;
}

.calendar-dark .fc .fc-scrollgrid-section table {
  background: #0f172a !important;
}

.calendar-dark .fc table {
  background: #0f172a !important;
}

/* Headers Dark */
.calendar-dark .fc .fc-col-header {
  background: #1e293b !important;
}

.calendar-dark .fc .fc-col-header-cell {
  background: #1e293b !important;
  border-color: #334155 !important;
}

.calendar-dark .fc .fc-col-header-cell-cushion {
  color: #cbd5e1 !important;
}

/* Day Grid Dark */
.calendar-dark .fc .fc-daygrid-day {
  background: #0f172a !important;
  border-color: #1e293b !important;
}

.calendar-dark .fc .fc-daygrid-day:hover {
  background: #1e293b !important;
}

.calendar-dark .fc .fc-daygrid-day.fc-day-today {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(37, 99, 235, 0.2) 100%) !important;
  border: 1px solid #3b82f6 !important;
}

.calendar-dark .fc .fc-daygrid-day.fc-day-other {
  background: #020617 !important;
  opacity: 0.5 !important;
}

.calendar-dark .fc .fc-daygrid-day-number {
  color: #f1f5f9 !important;
}

.calendar-dark .fc .fc-daygrid-day-top {
  color: #f1f5f9 !important;
}

.calendar-dark .fc .fc-day-today .fc-daygrid-day-number {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
  color: white !important;
}

/* More Link Dark */
.calendar-dark .fc .fc-daygrid-more-link {
  color: #60a5fa !important;
  background: rgba(59, 130, 246, 0.1) !important;
}

.calendar-dark .fc .fc-daygrid-more-link:hover {
  background: rgba(59, 130, 246, 0.2) !important;
}

/* Time Grid Dark */
.calendar-dark .fc .fc-timegrid {
  background: #0f172a !important;
}

.calendar-dark .fc .fc-timegrid-slot {
  border-color: #1e293b !important;
}

.calendar-dark .fc .fc-timegrid-slot-label {
  color: #94a3b8 !important;
  border-color: #1e293b !important;
  background: #0f172a !important;
}

.calendar-dark .fc .fc-timegrid-slot-lane {
  border-color: #1e293b !important;
}

.calendar-dark .fc .fc-timegrid-col {
  background: #0f172a !important;
  border-color: #1e293b !important;
}

.calendar-dark .fc .fc-timegrid-col.fc-day-today {
  background: rgba(59, 130, 246, 0.08) !important;
}

.calendar-dark .fc .fc-timegrid-axis {
  background: #0f172a !important;
  border-color: #1e293b !important;
}

.calendar-dark .fc .fc-timegrid-divider {
  border-color: #334155 !important;
}

/* List View Dark */
.calendar-dark .fc .fc-list {
  background: #0f172a !important;
  border-color: #1e293b !important;
}

.calendar-dark .fc .fc-list-table {
  background: #0f172a !important;
}

.calendar-dark .fc .fc-list-day-cushion {
  background: #1e293b !important;
  color: #cbd5e1 !important;
}

.calendar-dark .fc .fc-list-event {
  background: #0f172a !important;
}

.calendar-dark .fc .fc-list-event:hover td {
  background: #1e293b !important;
}

.calendar-dark .fc .fc-list-event-dot {
  border-color: #cbd5e1 !important;
}

.calendar-dark .fc .fc-list-event-title {
  color: #f1f5f9 !important;
}

.calendar-dark .fc .fc-list-event-time {
  color: #94a3b8 !important;
}

.calendar-dark .fc .fc-list-empty {
  background: #0f172a !important;
  color: #64748b !important;
}

/* Popover Dark */
.calendar-dark .fc .fc-popover {
  background: #1e293b !important;
  border-color: #334155 !important;
}

.calendar-dark .fc .fc-popover-header {
  background: #0f172a !important;
  color: #f1f5f9 !important;
  border-bottom: 1px solid #334155 !important;
}

.calendar-dark .fc .fc-popover-body {
  background: #1e293b !important;
}

.calendar-dark .fc .fc-popover-close {
  color: #cbd5e1 !important;
}

/* Scrollbar Dark */
.calendar-dark .fc .fc-scroller::-webkit-scrollbar {
  width: 8px !important;
  height: 8px !important;
}

.calendar-dark .fc .fc-scroller::-webkit-scrollbar-track {
  background: #0f172a !important;
}

.calendar-dark .fc .fc-scroller::-webkit-scrollbar-thumb {
  background: #334155 !important;
  border-radius: 4px !important;
}

.calendar-dark .fc .fc-scroller::-webkit-scrollbar-thumb:hover {
  background: #475569 !important;
}

/* Day Header Dark (Week/Day views) */
.calendar-dark .fc .fc-timegrid-col-frame {
  background: #0f172a !important;
}

.calendar-dark .fc .fc-day-other .fc-daygrid-day-number {
  color: #475569 !important;
}

/* All Day Row Dark */
.calendar-dark .fc .fc-daygrid-body {
  background: #0f172a !important;
}

.calendar-dark .fc .fc-daygrid-body-balanced {
  background: #0f172a !important;
}

.calendar-dark .fc .fc-daygrid-body-unbalanced {
  background: #0f172a !important;
}

.calendar-dark .fc .fc-daygrid-body-natural {
  background: #0f172a !important;
}

/* Event Containers Dark */
.calendar-dark .fc .fc-daygrid-event-harness {
  background: transparent !important;
}

.calendar-dark .fc .fc-daygrid-day-frame {
  background: #0f172a !important;
}

.calendar-dark .fc .fc-daygrid-day-bg {
  background: #0f172a !important;
}

/* Border overrides Dark */
.calendar-dark .fc table {
  border-color: #1e293b !important;
}

.calendar-dark .fc td,
.calendar-dark .fc th {
  border-color: #1e293b !important;
}

/* Text elements Dark */
.calendar-dark .fc .fc-daygrid-day-events {
  color: #f1f5f9 !important;
}

.calendar-dark .fc .fc-h-event {
  border-color: transparent !important;
}

/* Now Indicator Dark - manter vermelho */
.calendar-dark .fc .fc-timegrid-now-indicator-line {
  border-color: #ef4444 !important;
  border-width: 2px !important;
}

.calendar-dark .fc .fc-timegrid-now-indicator-arrow {
  border-color: #ef4444 !important;
}

/* ========================================
   RESPONSIVIDADE
   ======================================== */

@media (max-width: 768px) {
  .fc .fc-toolbar {
    flex-direction: column !important;
    gap: 0.75rem !important;
  }
  
  .fc .fc-toolbar-title {
    font-size: 1.25rem !important;
  }
  
  .fc .fc-button {
    padding: 0.375rem 0.75rem !important;
    font-size: 0.875rem !important;
  }
  
  .fc .fc-event-title {
    font-size: 0.75rem !important;
  }
  
  .fc .fc-event-time {
    font-size: 0.625rem !important;
  }
}
</style>
