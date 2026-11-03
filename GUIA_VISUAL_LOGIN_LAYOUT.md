# 🎨 Guia Visual - Login e Layout Base

## 📱 Tela de Login

### Layout Desktop (≥1024px)

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  ┌──────────────────┬─────────────────────────────────────┐   │
│  │                  │                                     │   │
│  │   🟦 AZUL       │         [FORMULÁRIO]               │   │
│  │   INSTITUCIONAL │                                     │   │
│  │   GRADIENTE     │    Bem-vindo de volta              │   │
│  │                  │    Entre com suas credenciais      │   │
│  │   GT            │                                     │   │
│  │   GabTech       │    📧 E-mail                       │   │
│  │                  │    ┌──────────────────────────┐   │   │
│  │   Gestão de     │    │ seu.email@exemplo.com    │   │   │
│  │   Mandatos      │    └──────────────────────────┘   │   │
│  │   Políticos     │                                     │   │
│  │                  │    🔒 Senha                        │   │
│  │   Plataforma    │    ┌──────────────────────────┐   │   │
│  │   completa...   │    │ ••••••••                 │   │   │
│  │                  │    └──────────────────────────┘   │   │
│  │                  │                                     │   │
│  │                  │    ┌──────────────────────────┐   │   │
│  │                  │    │   🔐 Entrar              │   │   │
│  │   © 2026        │    └──────────────────────────┘   │   │
│  │   GabTech       │                                     │   │
│  │                  │    ℹ️  Ambiente de Demonstração   │   │
│  └──────────────────┴─────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Layout Mobile (<1024px)

```
┌──────────────────────┐
│                      │
│      GT  GabTech     │
│                      │
│  Bem-vindo de volta  │
│  Entre com suas...   │
│                      │
│  📧 E-mail           │
│  ┌────────────────┐  │
│  │                │  │
│  └────────────────┘  │
│                      │
│  🔒 Senha            │
│  ┌────────────────┐  │
│  │                │  │
│  └────────────────┘  │
│                      │
│  ┌────────────────┐  │
│  │   🔐 Entrar    │  │
│  └────────────────┘  │
│                      │
│  ℹ️  Demonstração   │
│                      │
└──────────────────────┘
```

### Estados do Botão

**Normal:**
```
┌──────────────────────────┐
│   🔐 Entrar              │  ← Azul primário
└──────────────────────────┘
```

**Loading:**
```
┌──────────────────────────┐
│   ⏳ Entrando...         │  ← Spinner animado
└──────────────────────────┘
```

**Erro:**
```
┌────────────────────────────────────┐
│  ⚠️  Credenciais inválidas        │  ← Vermelho, animado
└────────────────────────────────────┘
```

---

## 🏗️ Layout Base (Desktop)

### Vista Completa (≥1024px)

```
┌─────────────────────────────────────────────────────────────────────┐
│  ┌──────────┬─────────────────────────────────────────────────┐   │
│  │          │  📋 Dashboard              👤 João Silva  [JS]   │   │
│  │  GT      ├─────────────────────────────────────────────────┤   │
│  │ GabTech  │                                                  │   │
│  │          │                                                  │   │
│  ├──────────┤     [CONTEÚDO DA PÁGINA]                        │   │
│  │          │                                                  │   │
│  │ 📊 Dash  │     Olá, João Silva! 👋                         │   │
│  │          │     Bem-vindo ao seu painel...                  │   │
│  │ 👥 CRM   │                                                  │   │
│  │          │     ┌──────┐  ┌──────┐  ┌──────┐               │   │
│  │ 📥 Atend │     │ Card │  │ Card │  │ Card │               │   │
│  │          │     └──────┘  └──────┘  └──────┘               │   │
│  ├──────────┤                                                  │   │
│  │          │                                                  │   │
│  │ ◀ Recol. │                                                  │   │
│  │          │                                                  │   │
│  │ 🚪 Sair  │                                                  │   │
│  └──────────┴──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
     256px          Conteúdo Fluido (max-w-7xl centralizado)
```

### Sidebar Colapsada (Desktop)

```
┌──────────────────────────────────────────────────────────────┐
│  ┌───┬──────────────────────────────────────────────────┐   │
│  │   │  📋 Dashboard              👤 João Silva  [JS]   │   │
│  │GT ├──────────────────────────────────────────────────┤   │
│  │   │                                                   │   │
│  ├───┤     [CONTEÚDO MAIS AMPLO]                        │   │
│  │   │                                                   │   │
│  │📊 │                                                   │   │
│  │   │                                                   │   │
│  │👥 │                                                   │   │
│  │   │                                                   │   │
│  │📥 │                                                   │   │
│  │   │                                                   │   │
│  ├───┤                                                   │   │
│  │▶  │                                                   │   │
│  │🚪 │                                                   │   │
│  └───┴───────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
   80px      Conteúdo expandido (mais espaço horizontal)
```

### Layout Mobile (<1024px)

**Sidebar Fechada:**
```
┌────────────────────────┐
│ ☰  Dashboard   [JS]    │ ← Header com botão hamburger
├────────────────────────┤
│                        │
│   [CONTEÚDO]           │
│                        │
│   Olá, João! 👋        │
│                        │
│   ┌──────────────┐     │
│   │ Card Métrica │     │
│   └──────────────┘     │
│                        │
└────────────────────────┘
```

**Sidebar Aberta (Drawer):**
```
┌────────────────────────┐
│ ⬛⬛⬛⬛⬛⬛⬛⬛⬛     │ ← Overlay escuro
│ ⬛┌──────────┐⬛     │
│ ⬛│ GT   ✖   │⬛     │
│ ⬛│ GabTech  │⬛     │
│ ⬛├──────────┤⬛     │
│ ⬛│          │⬛     │
│ ⬛│ 📊 Dash  │⬛     │
│ ⬛│ 👥 CRM   │⬛     │
│ ⬛│ 📥 Atend │⬛     │
│ ⬛│          │⬛     │
│ ⬛├──────────┤⬛     │
│ ⬛│ 🚪 Sair  │⬛     │
│ ⬛└──────────┘⬛     │
└────────────────────────┘
  Drawer    Overlay
  (256px)   (clicável)
```

---

## 🎨 Componentes Visuais

### Avatar

**Com Imagem:**
```
┌────┐
│ 📷 │  ← Imagem do usuário
└────┘
```

**Com Iniciais:**
```
┌────┐
│ JS │  ← Iniciais em fundo azul
└────┘
```

**Tamanhos:**
```
┌──┐     ┌───┐     ┌────┐     ┌─────┐
│sm│     │ md│     │ lg │     │  xl │
└──┘     └───┘     └────┘     └─────┘
32px     40px      48px       64px
```

### Botões (Component)

```
Primary:    ┌──────────────┐
            │   Primário   │  Azul
            └──────────────┘

Secondary:  ┌──────────────┐
            │  Secundário  │  Cinza
            └──────────────┘

Danger:     ┌──────────────┐
            │    Perigo    │  Vermelho
            └──────────────┘

Ghost:      ┌──────────────┐
            │    Ghost     │  Transparente
            └──────────────┘

Loading:    ┌──────────────┐
            │ ⏳ Loading.. │  Com spinner
            └──────────────┘
```

### Estados do Menu

**Item Normal:**
```
┌────────────────┐
│ 📊 Dashboard   │  ← Cinza, hover: fundo cinza claro
└────────────────┘
```

**Item Ativo:**
```
┌────────────────┐
│ 📊 Dashboard   │  ← Fundo azul claro, texto azul
└────────────────┘
```

**Logout:**
```
┌────────────────┐
│ 🚪 Sair        │  ← Vermelho, hover: fundo vermelho claro
└────────────────┘
```

---

## 🎭 Animações

### Sidebar Mobile (Drawer)

**Entrando:**
```
Frame 1:  ┌────┐              Frame 2:  ┌────────┐         Frame 3:  ┌────────────┐
          │    │ (oculto)              │        │                   │            │
          └────┘ -100%                 └────────┘ -50%               └────────────┘ 0%
```

**Overlay:**
```
Frame 1:  Transparente         Frame 2:  Semi-opaco         Frame 3:  Opaco
          (opacity: 0)                  (opacity: 0.3)              (opacity: 0.5)
```

### Collapse Sidebar Desktop

**Expandir → Colapsar:**
```
┌──────────────┐  →  ┌─────┐
│   256px      │      │ 80px│
│              │      │     │
│  Dashboard   │      │ 📊  │
│              │      │     │
└──────────────┘      └─────┘

Duração: 300ms
Easing: ease-in-out
```

### Loading Button

**Spinner:**
```
   ⏳        ⏰        ⌛        ⏲️
 (0°)      (90°)     (180°)    (270°)
   
   Rotação contínua: 360° em 1s
```

---

## 📐 Medidas e Especificações

### Sidebar
- **Largura Expandida:** 256px (w-64)
- **Largura Colapsada:** 80px (w-20)
- **Altura:** 100vh (full screen)
- **Z-index:** 50 (mobile), auto (desktop)
- **Transição:** 300ms

### Header
- **Altura:** 64px (h-16)
- **Z-index:** 30
- **Position:** Sticky top-0
- **Padding Horizontal:** 16px mobile, 24px desktop

### Conteúdo
- **Padding:** 16px mobile (p-4), 24px desktop (p-6)
- **Max Width:** 1280px (max-w-7xl)
- **Margin:** Centralizado (mx-auto)

### Breakpoints
- **Mobile:** < 1024px
- **Desktop:** ≥ 1024px

---

## 🎯 Interações do Usuário

### Desktop
1. **Navegar:** Clicar nos itens do menu lateral
2. **Colapsar Sidebar:** Clicar no botão "Recolher" (◀)
3. **Expandir Sidebar:** Clicar no botão de expansão (▶)
4. **Logout:** Clicar no botão "Sair" (vermelho)

### Mobile
1. **Abrir Menu:** Clicar no botão hamburger (☰) no header
2. **Navegar:** Clicar nos itens do menu (fecha automaticamente)
3. **Fechar Menu:** 
   - Clicar no botão X no header da sidebar
   - Clicar no overlay escuro
   - Navegar para outra página
4. **Logout:** Clicar no botão "Sair"

---

## 🔍 Detalhes de UX

### Feedback Visual
- ✅ **Hover:** Todos os botões/links mudam de cor
- ✅ **Active:** Item do menu atual destacado em azul
- ✅ **Loading:** Spinner animado durante operações
- ✅ **Disabled:** Botões desabilitados com opacity reduzida
- ✅ **Focus:** Ring azul ao focar com teclado

### Acessibilidade
- ✅ **Tooltips:** Ícones tem title quando sidebar colapsada
- ✅ **Alt Text:** Avatar tem texto alternativo
- ✅ **Keyboard:** Tab navigation funciona
- ✅ **Screen Readers:** Estrutura semântica (nav, aside, main)

### Performance
- ✅ **Transições suaves:** GPU-accelerated (transform)
- ✅ **Lazy Loading:** Views carregadas sob demanda
- ✅ **HMR:** Hot reload durante desenvolvimento

---

**🎉 Interface completa e pronta para uso!**
