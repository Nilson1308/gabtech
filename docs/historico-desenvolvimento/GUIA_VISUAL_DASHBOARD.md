# 🎨 Guia Visual - Dashboard

## 📊 Layout Completo (Desktop)

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │  ✨  Olá, João Silva! 👋                                       │ │
│  │      Bem-vindo ao seu painel de gestão...                     │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │ Atendimentos    │  │  SLA em Atraso  │  │ Base de         │   │
│  │ Abertos         │  │                 │  │ Cidadãos        │   │
│  │                 │  │                 │  │                 │   │
│  │      12    📥   │  │      3     ⚠️  │  │      20    👥   │   │
│  │                 │  │                 │  │                 │   │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘   │
│     Azul                  Vermelho              Verde              │
│                                                                     │
│  ┌──────────────────────────────────────┐  ┌──────────────────┐  │
│  │ Atendimentos por Macrotema           │  │ Ações Rápidas    │  │
│  │ Distribuição dos 15 atendimentos     │  │                  │  │
│  │                                      │  │ ┌──────────────┐ │  │
│  │ Saúde       ██████████████████  5    │  │ │🔵 Novo       │ │  │
│  │ Zeladoria   ██████████████      4    │  │ │  Atendimento │ │  │
│  │ Educação    ██████████          3    │  │ └──────────────┘ │  │
│  │ Transporte  ████████            2    │  │ ┌──────────────┐ │  │
│  │ Segurança   ████                1    │  │ │⚪ Novo       │ │  │
│  │                                      │  │ │  Cidadão     │ │  │
│  └──────────────────────────────────────┘  │ └──────────────┘ │  │
│                                             │                  │  │
│                                             │ Atalhos          │  │
│                                             │ [📥][👥]        │  │
│                                             └──────────────────┘  │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ Últimos Atendimentos                           Ver todos →    │ │
│  ├───────────────────────────────────────────────────────────────┤ │
│  │ [🟥] Solicitação de consulta médica                    →     │ │
│  │      Maria Santos • há 2 horas                               │ │
│  │      [Aberto] [Saúde]                                        │ │
│  ├───────────────────────────────────────────────────────────────┤ │
│  │ [🟧] Reparo de iluminação pública                      →     │ │
│  │      José Oliveira • há 5 horas                              │ │
│  │      [Em Andamento] [Zeladoria] [⚠️ SLA Atrasado]           │ │
│  ├───────────────────────────────────────────────────────────────┤ │
│  │ [🟦] Vaga em creche municipal                          →     │ │
│  │      Ana Paula Costa • há 1 dia                              │ │
│  │      [Aberto] [Educação]                                     │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📱 Layout Mobile

```
┌──────────────────────┐
│  ✨ Olá, João! 👋   │
│  Bem-vindo...        │
├──────────────────────┤
│ Atendimentos Abertos │
│                      │
│       12        📥   │
│                      │
├──────────────────────┤
│   SLA em Atraso      │
│                      │
│        3        ⚠️   │
│                      │
├──────────────────────┤
│  Base de Cidadãos    │
│                      │
│       20        👥   │
│                      │
├──────────────────────┤
│ Atendimentos por     │
│ Macrotema            │
│                      │
│ Saúde    ███████  5  │
│ Zelad.   █████    4  │
│ Educação ████     3  │
│                      │
├──────────────────────┤
│  Ações Rápidas       │
│                      │
│ ┌──────────────────┐ │
│ │🔵 Novo Atendim. │ │
│ └──────────────────┘ │
│ ┌──────────────────┐ │
│ │⚪ Novo Cidadão  │ │
│ └──────────────────┘ │
│                      │
│ Atalhos              │
│  [📥]  [👥]         │
│                      │
├──────────────────────┤
│ Últimos Atendimentos │
│                      │
│ [🟥] Consulta...    │
│ Maria • 2h          │
│ [Aberto] [Saúde]    │
│                      │
│ [🟧] Iluminação...  │
│ José • 5h           │
│ [Em And.] [⚠️ SLA]  │
│                      │
└──────────────────────┘
```

---

## 🎴 Detalhes dos Componentes

### Card de Métrica

**Normal:**
```
┌─────────────────────┐
│ Atendimentos Abertos│
│                     │
│       12       📥   │
│                     │
└─────────────────────┘
```

**Com Variação:**
```
┌─────────────────────┐
│ Base de Cidadãos    │
│                     │
│       20       👥   │
│                     │
│  +15% vs. semana    │
└─────────────────────┘
```

**Hover:**
```
┌─────────────────────┐
│ ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ │ ← Sombra mais forte
│ ▒ SLA em Atraso   ▒ │
│ ▒                 ▒ │
│ ▒      3     ⚠️  ▒ │
│ ▒                 ▒ │
│ ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ │
└─────────────────────┘
```

---

### Gráfico de Barras

**Estrutura:**
```
┌────────────────────────────────────────┐
│ Atendimentos por Macrotema             │
│ Distribuição dos 15 atendimentos       │
├────────────────────────────────────────┤
│                                        │
│ Label       Barra              Nº   %  │
│ ─────       ─────              ──   ── │
│                                        │
│ Saúde       ████████████████   5   33% │
│             ▲                  ▲   ▲   │
│             └─ Cor do          │   └─ % │
│                macrotema       └─ Total │
│                                        │
└────────────────────────────────────────┘
```

**Animação de Entrada:**
```
Frame 1:    Saúde       █
Frame 2:    Saúde       ████████
Frame 3:    Saúde       ████████████████  5

Duração: 700ms
Easing: ease-out
```

**Cores:**
```
Saúde          █████  #ef4444 (Vermelho)
Educação       █████  #3b82f6 (Azul)
Zeladoria      █████  #f59e0b (Laranja)
Transporte     █████  #8b5cf6 (Roxo)
Ass. Social    █████  #10b981 (Verde)
Segurança      █████  #dc2626 (Vermelho escuro)
```

---

### Quick Actions

**Layout Completo:**
```
┌──────────────────┐
│ Ações Rápidas    │
│ Acesso direto... │
├──────────────────┤
│                  │
│ ┌──────────────┐ │
│ │ + Novo       │ │ ← Azul primário
│ │   Atendimento│ │
│ │   Registrar..│ │
│ └──────────────┘ │
│                  │
│ ┌──────────────┐ │
│ │👤+ Novo      │ │ ← Cinza
│ │   Cidadão    │ │
│ │   Adicionar..│ │
│ └──────────────┘ │
│                  │
│ ──────────────── │ ← Border separador
│                  │
│ ATALHOS          │
│                  │
│ ┌─────┐ ┌─────┐  │
│ │ 📥  │ │ 👥  │  │
│ │Atend│ │ CRM │  │
│ └─────┘ └─────┘  │
│                  │
└──────────────────┘
```

**Hover nos Botões:**
```
Normal:     [🔵 Novo Atendimento]
Hover:      [🔵 Novo Atendimento]  ← Fundo mais escuro
```

---

### Item de Atendimento

**Estrutura Completa:**
```
┌─────────────────────────────────────────────────┐
│ ┌─────┐                                      ┌─┐│
│ │ [•] │  Solicitação de consulta médica     │→││ ← Chevron
│ │     │  Maria Santos • há 2 horas          └─┘│
│ │🟥   │  [Aberto] [Saúde]                      │
│ └─────┘                                         │
│   ▲                                             │
│   └─ Ícone do macrotema (caixa colorida)       │
└─────────────────────────────────────────────────┘
```

**Ícone do Macrotema:**
```
┌────────┐
│        │  ← Fundo: cor + 20% opacity
│   •    │  ← Ponto: cor sólida
│        │  ← Border: cor + 40% opacity
└────────┘
  10x10px
  rounded-lg
```

**Badges:**
```
Status:
  [Aberto]              Azul claro
  [Em Andamento]        Amarelo
  [Aguardando]          Roxo
  [Concluído]           Verde

Macrotema:
  [Saúde]               Vermelho claro com borda

SLA:
  [⚠️ SLA Atrasado]     Vermelho com ícone
```

**Hover:**
```
Normal:   [             Item do atendimento            ]
Hover:    [░░░░░░░░░░░░ Item do atendimento ░░░░░░░░░] ← Fundo cinza
```

**Estados:**
```
Clickable:    cursor-pointer
Hover:        bg-gray-50
Active:       (navega para detalhes)
```

---

## 📐 Medidas e Especificações

### Cards de Métricas
- **Tamanho do Ícone:** 48x48px (w-12 h-12)
- **Tamanho do Valor:** text-3xl (30px)
- **Label:** text-sm (14px)
- **Padding:** p-6 (24px)
- **Border Radius:** rounded-lg (8px)
- **Shadow:** shadow-sm (normal), shadow-md (hover)

### Gráfico
- **Altura da Barra:** 40px (h-10)
- **Border Radius:** rounded-full
- **Label Width:** 128px (w-32)
- **Percentage Width:** 48px (w-12)
- **Animação:** 700ms ease-out

### Quick Actions
- **Botão Principal:** px-4 py-3 (padding)
- **Ícone:** w-5 h-5 (20px)
- **Atalho:** w-16 h-16 (64x64px)
- **Gap:** gap-3 (12px)

### Lista de Atendimentos
- **Ícone Macrotema:** 40x40px (w-10 h-10)
- **Ponto Central:** 8px (w-2 h-2)
- **Padding Vertical:** py-4 (16px)
- **Gap:** gap-4 (16px)

---

## 🎨 Paleta de Cores

### Cores dos Cards
```
Azul (blue):
  - Background: #dbeafe (bg-blue-100)
  - Text: #2563eb (text-blue-600)
  - Border: #bfdbfe (border-blue-200)

Verde (green):
  - Background: #dcfce7 (bg-green-100)
  - Text: #16a34a (text-green-600)
  - Border: #bbf7d0 (border-green-200)

Vermelho (red):
  - Background: #fee2e2 (bg-red-100)
  - Text: #dc2626 (text-red-600)
  - Border: #fecaca (border-red-200)

Amarelo (yellow):
  - Background: #fef3c7 (bg-yellow-100)
  - Text: #ca8a04 (text-yellow-600)
  - Border: #fde68a (border-yellow-200)

Roxo (purple):
  - Background: #f3e8ff (bg-purple-100)
  - Text: #9333ea (text-purple-600)
  - Border: #e9d5ff (border-purple-200)
```

### Cores dos Status
```
Aberto:              #dbeafe bg / #1d4ed8 text
Em Andamento:        #fef3c7 bg / #a16207 text
Aguardando:          #f3e8ff bg / #7e22ce text
Concluído:           #dcfce7 bg / #15803d text
```

### Cores dos Macrotemas
```
Saúde:               #ef4444
Educação:            #3b82f6
Zeladoria:           #f59e0b
Transporte:          #8b5cf6
Assistência Social:  #10b981
Segurança:           #dc2626
```

---

## 🔄 Interações

### Cards de Métricas
1. **Hover:** Sombra aumenta (shadow-sm → shadow-md)
2. **Sem click:** Cards são informativos apenas

### Gráfico
1. **Entrada:** Animação de expansão (0% → 100% width)
2. **Sem interação:** Puramente visual

### Quick Actions
1. **Hover:** Fundo escurece ligeiramente
2. **Click:** Navega para rota correspondente
3. **Feedback:** Transição suave (transition-colors)

### Lista de Atendimentos
1. **Hover:** Fundo cinza claro (bg-gray-50)
2. **Cursor:** Pointer (indica clicável)
3. **Click:** Navega para `/atendimentos/:id`
4. **Chevron:** Gira no hover? (opcional)

### Loading
1. **Skeleton:** Animação pulse nos cards
2. **Duração:** ~500-800ms (latência mockada)
3. **Transição:** Fade in quando carregado

---

## 📊 Exemplos de Dados Reais

### Cenário 1: Dia Calmo
```
Atendimentos Abertos: 5
SLA em Atraso: 0
Base de Cidadãos: 15

Gráfico:
  Saúde: 2
  Educação: 2
  Zeladoria: 1
```

### Cenário 2: Dia Movimentado
```
Atendimentos Abertos: 25
SLA em Atraso: 8  ⚠️
Base de Cidadãos: 50

Gráfico:
  Zeladoria: 10
  Saúde: 8
  Transporte: 4
  Educação: 3
```

### Cenário 3: Sistema Novo
```
Atendimentos Abertos: 0
SLA em Atraso: 0
Base de Cidadãos: 0

Estado Vazio:
  "Nenhum dado disponível"
  "Nenhum atendimento encontrado"
```

---

## ✅ Estados Visuais

### Loading
```
┌─────────────────┐
│░░░░░░░░░░░░░░░░░│ ← Skeleton com pulse
│░░░░░░░░░░░░░░░░░│
│░░░░░░░░░░░░░░░░░│
└─────────────────┘
```

### Vazio (Gráfico)
```
┌─────────────────┐
│                 │
│  📊            │
│  Nenhum dado    │
│  disponível     │
│                 │
└─────────────────┘
```

### Vazio (Lista)
```
┌─────────────────┐
│                 │
│  📭            │
│  Nenhum         │
│  atendimento    │
│  encontrado     │
│                 │
└─────────────────┘
```

### Erro (Caso ocorra)
```
┌─────────────────┐
│  ⚠️ Erro ao    │
│  carregar dados │
│                 │
│  [Tentar        │
│   novamente]    │
└─────────────────┘
```

---

**🎨 Interface completa e polida, pronta para uso!**
