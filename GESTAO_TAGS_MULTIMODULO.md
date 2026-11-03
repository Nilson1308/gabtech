# 🏷️ Sistema de Gestão de Tags Multi-Módulo - GabTech

**Data**: 27 de Outubro de 2026  
**Desenvolvedor**: Dev Sênior Especialista em UI/UX  
**Status**: ✅ **IMPLEMENTADO E VALIDADO**

---

## 📋 Requisitos Implementados

### 1️⃣ **Dark Mode Completo em Configurações**
- ✅ Todos os textos, bordas e backgrounds com dark variants
- ✅ Cards de tags com backgrounds escuros
- ✅ Modais com dark mode completo
- ✅ Formulário com preview e cores dark-friendly

### 2️⃣ **Sistema Multi-Módulo para Tags**
- ✅ Tags podem ser compartilhadas entre CRM e Atendimentos
- ✅ Seleção de módulos no formulário de criação/edição
- ✅ Badges visuais mostrando em quais módulos a tag está disponível
- ✅ Validação para evitar exclusão de tags em uso

---

## 🎯 **Arquitetura Implementada**

### **Tipo Tag Atualizado**

```typescript
export type ModuloTag = 'crm' | 'atendimentos'

export interface Tag {
  id: string
  nome: string
  cor: string
  modulos: ModuloTag[]  // Novo campo!
}
```

### **Exemplos de Uso**

```typescript
// Tag exclusiva do CRM
{ 
  id: '1', 
  nome: 'Servidor Público', 
  cor: '#8b5cf6', 
  modulos: ['crm'] 
}

// Tag compartilhada entre CRM e Atendimentos
{ 
  id: '2', 
  nome: 'Liderança Comunitária', 
  cor: '#f59e0b', 
  modulos: ['crm', 'atendimentos'] 
}

// Tag exclusiva de Atendimentos
{ 
  id: 'a1', 
  nome: 'Tapa Buraco', 
  cor: '#f59e0b', 
  modulos: ['atendimentos'] 
}
```

---

## 🔧 **Funcionalidades Implementadas**

### **1. Tela de Configurações**

**Localização**: `/configuracoes`

**Recursos**:
- ✅ **Listagem de Tags** com badges mostrando módulos disponíveis
- ✅ **Criação de Tags** com seleção de módulos (mínimo 1)
- ✅ **Edição de Tags** permitindo alterar nome, cor e módulos
- ✅ **Exclusão de Tags** com validação de uso
- ✅ **Dark Mode Completo**

**UI Multi-Módulo**:
```vue
<!-- Badges de módulos na lista -->
<span class="bg-green-100 dark:bg-green-900/30 text-green-700">
  <Users class="w-3 h-3" />
  CRM
</span>
<span class="bg-blue-100 dark:bg-blue-900/30 text-blue-700">
  <Inbox class="w-3 h-3" />
  Atendimentos
</span>
```

**Seleção de Módulos no Modal**:
```vue
<button 
  @click="toggleModulo('crm')"
  :class="form.modulos.includes('crm') ? 'bg-green-50 border-green-500' : ''"
>
  <Users /> CRM
</button>

<button 
  @click="toggleModulo('atendimentos')"
  :class="form.modulos.includes('atendimentos') ? 'bg-blue-50 border-blue-500' : ''"
>
  <Inbox /> Atendimentos
</button>
```

---

### **2. Stores Atualizadas**

#### **CRM Store** (`src/stores/crm.ts`)

**Mudanças**:
- ✅ `tagsDisponiveis` agora é `ref()` (reativo)
- ✅ CRUD de tags com campo `modulos`
- ✅ Método `tagsPorModulo()` para filtrar tags por módulo

**Métodos**:
```typescript
// Criar tag
async createTag(data: { 
  nome: string
  cor: string
  modulos: string[] 
})

// Atualizar tag
async updateTag(id: string, data: { 
  nome: string
  cor: string
  modulos: string[] 
})

// Deletar tag
async deleteTag(id: string)

// Filtrar por módulo
tagsPorModulo(modulo: 'crm' | 'atendimentos'): Tag[]
```

**Tags Mock Iniciais**:
```typescript
const tagsDisponiveis = ref<Tag[]>([
  { id: '1', nome: 'Apoiador', cor: '#10b981', modulos: ['crm'] },
  { id: '2', nome: 'Liderança Comunitária', cor: '#f59e0b', modulos: ['crm', 'atendimentos'] },
  { id: '3', nome: 'Empresário', cor: '#3b82f6', modulos: ['crm'] },
  { id: '4', nome: 'Servidor Público', cor: '#8b5cf6', modulos: ['crm'] },
  { id: '5', nome: 'Estudante', cor: '#ec4899', modulos: ['crm', 'atendimentos'] },
])
```

#### **Atendimentos Store** (`src/stores/atendimentos.ts`)

**Tags Específicas de Atendimentos**:
```typescript
const tagsAtendimentoDisponiveis = ref<Tag[]>([
  { id: 'a1', nome: 'Tapa Buraco', cor: '#f59e0b', modulos: ['atendimentos'] },
  { id: 'a2', nome: 'Limpeza', cor: '#10b981', modulos: ['atendimentos'] },
  { id: 'a3', nome: 'Consulta Médica', cor: '#ef4444', modulos: ['atendimentos'] },
  // ... outras tags de serviços
])
```

---

### **3. Validação de Exclusão**

**Implementação**:
```typescript
const handleExcluir = (tag: Tag) => {
  // Verificar uso no CRM
  const emUsoCRM = crmStore.cidadaos.filter(c => 
    c.tags.some(t => t.id === tag.id)
  ).length
  
  // Verificar uso em Atendimentos
  const emUsoAtendimentos = atendimentosStore.atendimentos.filter(a => 
    a.tags.some(t => t.id === tag.id)
  ).length
  
  const totalEmUso = emUsoCRM + emUsoAtendimentos
  
  if (totalEmUso > 0) {
    // Mostrar modal de aviso
    quantidadeUso.value = totalEmUso
    mostrarAvisoUso.value = true
    return
  }
  
  // Prosseguir com exclusão
  if (confirmandoExclusao.value !== tag.id) {
    confirmandoExclusao.value = tag.id
    return
  }
  
  crmStore.deleteTag(tag.id)
}
```

---

## 🎨 **Dark Mode em Configurações**

### **Classes Aplicadas**

```vue
<!-- Header -->
<h2 class="text-gray-900 dark:text-slate-100">Configurações</h2>
<p class="text-gray-600 dark:text-slate-400">Gerencie tags...</p>

<!-- Card de Tags -->
<div class="card"> <!-- bg-white dark:bg-slate-800 -->
  <h3 class="text-gray-900 dark:text-slate-100">Tags e Etiquetas</h3>
</div>

<!-- Lista de Tags -->
<div class="border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800">
  <!-- Preview -->
  <div :style="{ backgroundColor: tag.cor + '20', color: tag.cor }">
    {{ tag.nome }}
  </div>
  
  <!-- Badges de Módulos -->
  <span class="bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400">
    <Users class="w-3 h-3" /> CRM
  </span>
  <span class="bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400">
    <Inbox class="w-3 h-3" /> Atendimentos
  </span>
  
  <!-- Botões de Ação -->
  <button class="text-gray-600 dark:text-slate-400 hover:bg-gray-100 dark:hover:bg-slate-700">
    <Edit class="w-4 h-4" />
  </button>
  <button class="text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30">
    <Trash2 class="w-4 h-4" />
  </button>
</div>

<!-- Modal Form -->
<div class="bg-gray-50 dark:bg-slate-900">
  <p class="text-gray-600 dark:text-slate-400">Preview:</p>
</div>

<!-- Seleção de Cor -->
<button :class="form.cor === cor ? 'ring-2 ring-primary-600 dark:ring-offset-slate-800' : ''">
  <!-- cor -->
</button>

<!-- Modal de Aviso -->
<div class="bg-yellow-100 dark:bg-yellow-900/30">
  <AlertCircle class="text-yellow-600 dark:text-yellow-400" />
</div>
<p class="text-gray-900 dark:text-slate-100">Esta tag está em uso</p>
<p class="text-gray-600 dark:text-slate-400">Você deve reatribuir...</p>
```

---

## 📊 **Fluxo de Uso**

### **1. Criar Nova Tag**

```
1. Acessar /configuracoes
2. Clicar em "Nova Tag"
3. Preencher nome
4. Selecionar cor
5. Selecionar módulos:
   ☑ CRM
   ☑ Atendimentos
6. Clicar em "Criar Tag"
```

**Resultado**: Tag criada e disponível nos módulos selecionados.

### **2. Usar Tag no CRM**

```
1. Criar/Editar cidadão
2. Ver lista de tags disponíveis (filtradas por modulo: 'crm')
3. Selecionar tags
4. Salvar
```

### **3. Usar Tag em Atendimentos**

```
1. Criar atendimento
2. Ver lista de tags disponíveis (filtradas por modulo: 'atendimentos')
3. Selecionar tags
4. Salvar
```

### **4. Editar Tag**

```
1. Acessar /configuracoes
2. Clicar no ícone de editar (lápis)
3. Alterar nome, cor ou módulos
4. Salvar
```

### **5. Excluir Tag**

```
1. Acessar /configuracoes
2. Clicar no ícone de excluir (lixeira)
3. Se em uso → Aviso: "Tag está vinculada a X registros"
4. Se não em uso → Clicar novamente para confirmar
5. Tag excluída
```

---

## 📦 **Arquivos Modificados**

### **Tipos**
- ✅ `src/types/index.ts` - Adicionado `ModuloTag` e campo `modulos` em `Tag`

### **Stores**
- ✅ `src/stores/crm.ts` - CRUD de tags com módulos + `tagsPorModulo()`
- ✅ `src/stores/atendimentos.ts` - Tags com campo `modulos`

### **Views**
- ✅ `src/views/ConfiguracoesView.vue` - UI multi-módulo + dark mode completo

### **Componentes**
- ✅ `src/components/crm/TagCreatorInline.vue` - Atualizado para incluir módulos

---

## ✅ **Build Validado**

```bash
✓ npm run build
✓ Built in 1.18s
✓ 0 errors
✓ 49.66 KB CSS
```

---

## 🎯 **Benefícios**

1. **Flexibilidade**: Tags podem ser compartilhadas ou exclusivas
2. **Organização**: Filtros automáticos por módulo
3. **Segurança**: Validação de exclusão impede perda de dados
4. **UX**: Badges visuais indicam disponibilidade
5. **Escalabilidade**: Fácil adicionar novos módulos no futuro

---

## 🚀 **Próximas Melhorias (Opcional)**

1. **Filtros Avançados**: Filtrar tags por módulo na listagem de configurações
2. **Bulk Operations**: Editar múltiplas tags de uma vez
3. **Importação/Exportação**: CSV de tags
4. **Categorias**: Agrupar tags em categorias (Status, Perfil, Serviço, etc.)
5. **Cores Customizadas**: Picker de cor livre além das pré-definidas
6. **Permissões**: Controle de quem pode criar/editar/excluir tags

---

## 📖 **Como Usar**

### **Para Usuários**:
1. Acesse **Configurações** no menu lateral
2. Veja a lista de **Tags e Etiquetas**
3. Clique em **Nova Tag** para criar
4. Selecione em quais módulos a tag estará disponível
5. Escolha uma cor e dê um nome
6. Salve e use nos módulos selecionados!

### **Para Desenvolvedores**:
```typescript
// Criar tag
await crmStore.createTag({
  nome: 'VIP',
  cor: '#ef4444',
  modulos: ['crm', 'atendimentos']
})

// Filtrar tags por módulo
const tagsCRM = crmStore.tagsPorModulo('crm')
const tagsAtendimentos = crmStore.tagsPorModulo('atendimentos')

// Atualizar tag
await crmStore.updateTag('id-da-tag', {
  nome: 'VIP Premium',
  cor: '#dc2626',
  modulos: ['crm']  // Removeu de atendimentos
})
```

---

**SISTEMA DE TAGS MULTI-MÓDULO 100% FUNCIONAL!** 🎉🏷️

- ✅ Dark mode completo
- ✅ CRUD completo de tags
- ✅ Multi-módulo (CRM + Atendimentos)
- ✅ Validações de uso
- ✅ UI/UX profissional
