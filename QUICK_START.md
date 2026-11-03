# Quick Start — GabTech

Documentação completa: [docs/README.md](docs/README.md) · Produção: [docs/PRODUCAO.md](docs/PRODUCAO.md)

# 🚀 Quick Start - GabTech

## ⚡ Início Rápido

```bash
# 1. Entrar no diretório
cd /var/www/gabtech

# 2. Instalar dependências (se necessário)
npm install --legacy-peer-deps

# 3. Backend Django (outro terminal)
cd backend && python manage.py runserver 0.0.0.0:8800

# 4. Preparar tenant demo (contas + seed Mogi das Cruzes)
cd backend && python manage.py bootstrap_demo --reset-seed

# 5. Front (Vite — porta 5173; `npm run dev:5174` para subdomínios)
cd .. && npm run dev

# 6. Acessar
# Demo:  http://localhost:5173/login  (API http://localhost:8800)
# Outro gabinete: http://<slug>.localhost:5174/login  (use npm run dev:5174)
```

## 🔐 Login demo (dev)

Após `bootstrap_demo`:

| E-mail | Perfil |
|--------|--------|
| `admin@demo.localhost` | Administrador |
| `chefe@teste.com` | Chefe de Gabinete |
| `assessor@teste.com` | Assessor |
| `recepcao@teste.com` | Recepção |
| `cerimonia@teste.com` | Cerimonial |

**Senha (todas):** `demo123456`

**Admin Django:** http://localhost:8800/admin/ — usuário **`admin`** (não e-mail), mesma senha.

Gabinetes criados pelo cadastro: acesse **`http://<slug>.localhost:5174/login`** (`npm run dev:5174`), não `localhost:5173` — senão a API aponta para o demo.

Se o rodapé do login mostrar API errada, recarregue a página (o app corrige ao abrir `/login`) ou limpe `gabtech_api_base` no localStorage.

## 🧭 Navegação

### Desktop (≥1024px)
- Use o **menu lateral** para navegar
- Clique em **"Recolher"** para colapsar a sidebar
- Clique em **"Sair"** (vermelho) para fazer logout

### Mobile (<1024px)
- Clique no **☰** (hamburger) para abrir o menu
- Clique no **overlay** ou **X** para fechar
- Navegue normalmente - o menu fecha automaticamente

## 📦 O Que Já Funciona

✅ **Login** - Tela completa com validação  
✅ **Navegação** - Sidebar e Header funcionais  
✅ **Dashboard** - Completo com métricas, gráfico e lista de atendimentos  
✅ **CRM** - Completo com busca, filtros, perfil 360º e exportação CSV  
✅ **Logout** - Funcional com redirecionamento  
✅ **Responsivo** - Mobile e Desktop  
✅ **Permissões** - Sistema RBAC mockado  
✅ **Atendimentos** - Em desenvolvimento (Etapa 5)  

## 🎨 Componentes Reutilizáveis

```vue
<!-- Avatar -->
<Avatar nome="João Silva" tamanho="md" />

<!-- Botão -->
<Button variant="primary" :loading="loading">
  Salvar
</Button>

<!-- Loading -->
<Loading tamanho="md" texto="Carregando..." />
```

## 📂 Estrutura de Pastas

```
src/
├── components/
│   ├── common/        # Avatar, Button, Loading
│   └── layout/        # MainLayout, Sidebar, Header
├── views/             # Páginas (Login, Dashboard, CRM, etc)
├── stores/            # Pinia (auth, crm, atendimentos)
├── router/            # Vue Router com guards
├── types/             # Interfaces TypeScript
└── composables/       # useFormatters (datas, telefone, etc)
```

## 🔧 Comandos Úteis

```bash
# Desenvolvimento
npm run dev

# Build de produção
npm run build

# Preview do build
npm run preview

# Instalar nova dependência
npm install --legacy-peer-deps [package]
```

## 📚 Documentação

- **[README.md](README.md)** — visão geral
- **[docs/README.md](docs/README.md)** — índice (dev, produção, arquitetura)
- **[docs/historico-desenvolvimento/](docs/historico-desenvolvimento/README.md)** — registros de etapas/sprints (legado)

## 🐛 Troubleshooting

### Erro ao instalar dependências
```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

### Porta em uso
O Vite automaticamente tenta outra porta disponível.

### Erros TypeScript
```bash
npm run build  # Verifica erros de compilação
```

## ✅ Status Atual

**Etapas 1 & 2:** ✅ Concluídas (Login + Layout Base)  
**Etapa 3 (Dashboard):** ✅ Concluída  
**Etapa 4 (CRM):** ✅ Concluída  
**Etapa 5 (Atendimentos):** ⏳ Próxima  

## 🎯 Próximo Passo

Implementar **Módulo de Atendimentos** com:
- Quadro Kanban (4 colunas)
- Cards de atendimentos
- Modal de novo atendimento
- Tela de detalhes com despachos

---

**Pronto para validação!** 🎉
