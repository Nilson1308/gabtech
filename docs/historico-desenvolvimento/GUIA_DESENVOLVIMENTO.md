# Guia de Desenvolvimento - Próximos Passos

## 🎯 Ordem Recomendada de Implementação

### 1️⃣ Layout Base (PRÓXIMO)
**Prioridade:** ALTA  
**Arquivo:** `src/views/LayoutBase.vue`

**Componentes necessários:**
- `src/components/common/Sidebar.vue` - Sidebar lateral colapsável
- `src/components/common/Header.vue` - Header superior com perfil do usuário
- `src/components/common/UserMenu.vue` - Menu dropdown do usuário

**Features:**
- Sidebar com navegação entre módulos (CRM, Atendimentos)
- Ícones do Lucide Vue
- Botão de colapsar/expandir sidebar
- Header com nome do usuário, avatar e botão de logout
- Responsivo (mobile: sidebar como drawer)

**Dados disponíveis:**
- `authStore.usuario` - Dados do usuário logado
- `authStore.logout()` - Função de logout

---

### 2️⃣ Tela de Login
**Prioridade:** ALTA  
**Arquivo:** `src/views/LoginView.vue`

**Layout:**
- Split screen (imagem institucional + formulário)
- Campos: Email, Senha
- Botão de login
- Mensagens de erro/sucesso

**Lógica:**
```typescript
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const login = async () => {
  const result = await authStore.login({ email, senha })
  if (result.success) {
    router.push('/dashboard')
  }
}
```

---

### 3️⃣ Dashboard
**Prioridade:** ALTA  
**Arquivo:** `src/views/DashboardView.vue`

**Componentes necessários:**
- `src/components/dashboard/MetricCard.vue` - Card de métrica
- `src/components/dashboard/MacrotemaChart.vue` - Gráfico de barras
- `src/components/dashboard/UltimosAtendimentos.vue` - Lista de atendimentos

**Dados disponíveis:**
```typescript
import { useAtendimentosStore } from '@/stores/atendimentos'

const atendimentosStore = useAtendimentosStore()

// Métricas
const totalAtendimentos = atendimentosStore.totalAtendimentos
const atendimentosAtrasados = atendimentosStore.atendimentosAtrasados.length
const atendimentosPorMacrotema = atendimentosStore.atendimentosPorMacrotema

// Últimos atendimentos do usuário
const authStore = useAuthStore()
const meusAtendimentos = computed(() => 
  atendimentosStore.atendimentos
    .filter(a => a.responsavelId === authStore.usuario?.id)
    .slice(0, 5)
)
```

---

### 4️⃣ CRM - Lista
**Prioridade:** MÉDIA  
**Arquivo:** `src/views/crm/CrmListView.vue`

**Componentes necessários:**
- `src/components/crm/CidadaoTable.vue` - Tabela de cidadãos
- `src/components/crm/CidadaoModal.vue` - Modal de criação/edição
- `src/components/common/SearchBar.vue` - Barra de pesquisa
- `src/components/common/Pagination.vue` - Componente de paginação

**Dados disponíveis:**
```typescript
import { useCrmStore } from '@/stores/crm'

const crmStore = useCrmStore()

// Buscar cidadãos com paginação
const { data, meta } = await crmStore.fetchCidadaos(page, perPage)

// Busca global
crmStore.searchQuery = 'termo de busca'

// Criar novo cidadão
await crmStore.createCidadao({ nome, telefone, ... })

// Tags disponíveis
const tags = crmStore.tagsDisponiveis
```

---

### 5️⃣ CRM - Perfil 360º
**Prioridade:** MÉDIA  
**Arquivo:** `src/views/crm/CrmPerfilView.vue`

**Layout:**
- Lado esquerdo: Dados pessoais do cidadão
- Lado direito: Timeline de interações e atendimentos

**Componentes necessários:**
- `src/components/crm/PerfilDados.vue` - Dados do cidadão
- `src/components/crm/PerfilTimeline.vue` - Timeline de histórico
- `src/components/common/BackButton.vue` - Botão voltar

**Dados disponíveis:**
```typescript
import { useCrmStore } from '@/stores/crm'
import { useAtendimentosStore } from '@/stores/atendimentos'
import { useRoute } from 'vue-router'

const route = useRoute()
const crmStore = useCrmStore()
const atendimentosStore = useAtendimentosStore()

// Buscar cidadão
const cidadao = await crmStore.getCidadaoById(route.params.id)

// Atendimentos vinculados
const atendimentos = computed(() => 
  atendimentosStore.atendimentos.filter(a => a.cidadaoId === cidadao.id)
)
```

---

### 6️⃣ Atendimentos - Kanban
**Prioridade:** ALTA  
**Arquivo:** `src/views/atendimentos/AtendimentosView.vue`

**Componentes necessários:**
- `src/components/atendimentos/KanbanBoard.vue` - Quadro Kanban
- `src/components/atendimentos/KanbanColumn.vue` - Coluna do Kanban
- `src/components/atendimentos/AtendimentoCard.vue` - Card do atendimento
- `src/components/atendimentos/NovoAtendimentoModal.vue` - Modal de criação

**Layout:**
4 colunas: Aberto | Em Andamento | Aguardando Terceiros | Concluído

**Dados disponíveis:**
```typescript
import { useAtendimentosStore } from '@/stores/atendimentos'

const atendimentosStore = useAtendimentosStore()

// Atendimentos por status
const atendimentosPorStatus = atendimentosStore.atendimentosPorStatus

// Criar novo atendimento
await atendimentosStore.createAtendimento({
  cidadaoId,
  assunto,
  descricao,
  macrotema,
  responsavelId,
  prioridade
})

// Mudar status (drag and drop)
await atendimentosStore.updateStatus(atendimentoId, novoStatus)
```

**Features especiais:**
- Indicador visual de SLA atrasado (borda vermelha)
- Cores dos macrotemas nos cards
- Avatar do responsável
- Drag and drop (opcional, pode usar botões)

---

### 7️⃣ Atendimentos - Detalhes
**Prioridade:** ALTA  
**Arquivo:** `src/views/atendimentos/AtendimentoDetalhesView.vue`

**Layout:**
- Lado esquerdo: Dados do atendimento (protocolo, cidadão, macrotema, etc)
- Lado direito: Timeline de despachos

**Componentes necessários:**
- `src/components/atendimentos/AtendimentoDados.vue` - Dados do atendimento
- `src/components/atendimentos/DespachosTimeline.vue` - Timeline de despachos
- `src/components/atendimentos/NovoDespachoForm.vue` - Formulário de despacho
- `src/components/atendimentos/StatusChanger.vue` - Alterador de status

**Dados disponíveis:**
```typescript
import { useAtendimentosStore } from '@/stores/atendimentos'
import { useRoute } from 'vue-router'

const route = useRoute()
const atendimentosStore = useAtendimentosStore()

// Buscar atendimento
const atendimento = await atendimentosStore.getAtendimentoById(route.params.id)

// Adicionar despacho
await atendimentosStore.addDespacho(
  atendimentoId, 
  conteudo, 
  'nota_interna' // ou 'nota_publica'
)

// Mudar status
await atendimentosStore.updateStatus(atendimentoId, novoStatus)
```

---

## 🎨 Padrões de UI/UX

### Cores
- **Primária:** `bg-primary-600`, `text-primary-600` (azul institucional)
- **Sucesso:** `bg-green-600`
- **Perigo:** `bg-red-600`
- **Aviso:** `bg-yellow-500`
- **Info:** `bg-blue-500`

### Componentes Reutilizáveis Sugeridos
```
src/components/common/
├── Button.vue          # Botão customizado
├── Input.vue           # Input customizado
├── Select.vue          # Select customizado
├── Modal.vue           # Modal base
├── Drawer.vue          # Drawer lateral
├── Card.vue            # Card base
├── Badge.vue           # Badge/Tag
├── Avatar.vue          # Avatar do usuário
├── Loading.vue         # Spinner de loading
├── EmptyState.vue      # Estado vazio
└── ConfirmDialog.vue   # Diálogo de confirmação
```

### Ícones (Lucide Vue)
```typescript
import { 
  Home, Users, ClipboardList, Menu, X, 
  Search, Plus, Edit, Trash, Eye, 
  ChevronLeft, ChevronRight, Filter,
  Calendar, Clock, AlertCircle, CheckCircle
} from 'lucide-vue-next'
```

---

## 🔧 Utilitários Disponíveis

### Formatadores
```typescript
import { useFormatters } from '@/composables/useFormatters'

const { 
  formatDate,          // formatDate('2026-10-26', true)
  formatRelativeTime,  // 'há 2 horas'
  formatPhone,         // '(11) 98888-7777'
  formatCPF,           // '123.456.789-00'
  formatCEP,           // '01234-567'
  getInitials,         // 'JS' de 'João Silva'
  truncate             // truncate('texto longo...', 20)
} = useFormatters()
```

### Controle de Permissões
```vue
<template>
  <!-- Via diretiva -->
  <button v-permission="'create_crm'">Novo</button>
  
  <!-- Via computed -->
  <button v-if="hasPermission('create_crm')">Novo</button>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const hasPermission = (perm: string) => authStore.hasPermission(perm)
</script>
```

---

## 📱 Responsividade

### Breakpoints Tailwind
- `sm:` - 640px
- `md:` - 768px
- `lg:` - 1024px
- `xl:` - 1280px
- `2xl:` - 1536px

### Padrão Mobile-First
```vue
<!-- Mobile por padrão, desktop com prefixos -->
<div class="flex flex-col lg:flex-row">
  <!-- Em mobile: coluna | Em desktop: linha -->
</div>
```

---

## ✅ Checklist de Cada Componente

Antes de considerar um componente completo:

- [ ] Tipagem TypeScript completa
- [ ] Composition API com `<script setup>`
- [ ] Responsivo (mobile-first)
- [ ] Loading states implementados
- [ ] Empty states implementados
- [ ] Tratamento de erros
- [ ] Permissões verificadas
- [ ] Acessibilidade (aria-labels, roles)
- [ ] Formatação de dados (datas, telefones, etc)
- [ ] Feedback visual (toasts, confirmações)

---

## 🚀 Para Começar Agora

1. Execute `npm run dev`
2. Acesse `http://localhost:5173`
3. Comece pelo **Layout Base**
4. Depois implemente a **Tela de Login**
5. Em seguida o **Dashboard**

## 📚 Documentação Útil

- Vue 3: https://vuejs.org/guide/introduction.html
- Pinia: https://pinia.vuejs.org/
- Vue Router: https://router.vuejs.org/
- Tailwind CSS: https://tailwindcss.com/docs
- Lucide Icons: https://lucide.dev/icons/

---

**Pronto para começar! 🎉**
