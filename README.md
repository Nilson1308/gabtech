# GabTech

SaaS multi-tenant para **gestão de gabinetes políticos** (executivo e legislativo): CRM de cidadãos, atendimentos/SLA, agenda, documentos, cerimonial, serviços, analytics e governança (RBAC + auditoria).

## Stack

| Camada | Tecnologia |
|--------|------------|
| Front | Vue 3, TypeScript, Vite, Pinia, Vue Router, Tailwind |
| API | Django 5.2, Django REST Framework, Simple JWT |
| Dados | PostgreSQL, **django-tenants** (schema por gabinete) |
| Plataforma | App `plataforma` (cadastro self-service, admin public) |

## Início rápido

Ver [QUICK_START.md](QUICK_START.md) e [docs/DESENVOLVIMENTO.md](docs/DESENVOLVIMENTO.md).

```bash
# Postgres
cd backend && docker compose up -d && cp .env.example .env
source .venv/bin/activate && pip install -r requirements.txt
python manage.py migrate_schemas --shared && python manage.py migrate_schemas
python manage.py bootstrap_demo --reset-seed
./serve.sh

# Front (outro terminal)
npm install --legacy-peer-deps && npm run dev
# Login demo: http://localhost:5173/login — admin@demo.localhost / demo123456
```

## Documentação

Índice completo: **[docs/README.md](docs/README.md)**

- [Arquitetura](docs/ARQUITETURA.md)
- [Produção — checklist](docs/PRODUCAO.md)
- [Análise comercial](docs/ANALISE_COMERCIAL.md)

## Estrutura do repositório

```
backend/          # Django (config, apps, manage.py)
src/              # Vue SPA
docs/             # Documentação atual
public/           # Assets estáticos do Vite
```

## Produção

Antes do go-live, leia **[docs/PRODUCAO.md](docs/PRODUCAO.md)** (HTTPS, Gunicorn, fila de provisionamento, Redis, backups, CORS de produção).

## Licença

Proprietary — GabTech © 2026
