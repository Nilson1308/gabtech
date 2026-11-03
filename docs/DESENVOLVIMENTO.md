# Desenvolvimento local

## Pré-requisitos

- Node.js 20+ e npm
- Python 3.10+
- PostgreSQL 16 (ou Docker)

## Banco de dados

```bash
cd backend
cp .env.example .env   # ajuste POSTGRES_* se necessário
docker compose up -d
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate_schemas --shared
python manage.py migrate_schemas
```

## API Django

```bash
cd backend
./serve.sh
# ou: python manage.py runserver 0.0.0.0:8800
```

## Front Vue

```bash
cp .env.example .env.development
npm install --legacy-peer-deps
npm run dev          # http://localhost:5173 — tenant demo
npm run dev:5174     # subdomínios *.localhost (outros gabinetes)
```

## Tenant demo (conteúdo seed)

```bash
cd backend
python manage.py bootstrap_demo --reset-seed
```

| App (`localhost:5173`) | Admin tenant (`localhost:8800/admin`) |
|------------------------|----------------------------------------|
| E-mail: ver tabela abaixo | Usuário: `admin` |
| Senha: `demo123456` | Senha: `demo123456` |

E-mails demo: `admin@demo.localhost`, `chefe@teste.com`, `assessor@teste.com`, `recepcao@teste.com`, `cerimonia@teste.com`.

## Outros gabinetes (self-service)

1. Cadastro: front em `/cadastro-gabinete` (API public em `127.0.0.1:8800`).
2. Login: `http://<slug>.localhost:5174/login` com `npm run dev:5174`.
3. Não use `localhost:5173` para tenants criados via cadastro — aponta para o demo.

## Comandos úteis

| Comando | Descrição |
|---------|-----------|
| `python manage.py bootstrap_demo` | RBAC + contas + seed Mogi |
| `python manage.py seed_demo --schema=gabinete_demo --reset` | Só dados demo |
| `python manage.py criar_gabinete --schema X --nome Y --domain z.localhost` | Novo tenant manual |
| `python manage.py criar_operador_plataforma --email=... --senha=...` | Admin plataforma (public) |
| `python manage.py redefinir_senha_tenant --schema=... --email=... --senha=...` | Reset senha tenant |

## Admin plataforma

- URL: `http://127.0.0.1:8800/admin/` (schema **public**)
- Credencial: operador criado via `criar_operador_plataforma` (e-mail, não `User` de gabinete)
