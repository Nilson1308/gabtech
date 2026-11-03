# Arquitetura

## Multi-tenant (django-tenants)

- **Schema `public`:** gabinetes (`core.Gabinete`), domínios HTTP (`core.Dominio`), cadastro self-service (`plataforma`), operadores da plataforma.
- **Schema por gabinete:** usuários, CRM, atendimentos, agenda, documentos, cerimonial, serviços, auditoria, RBAC.

## Resolução de host

| Host (exemplo) | URLconf | Uso |
|----------------|---------|-----|
| `api.seudominio.com` (tenant) | `config.urls` | API + admin do gabinete |
| `app.seudominio.com` | SPA (Vite/nginx) | Front por subdomínio ou path |
| Domínio public / sem tenant | `config.urls_public` | `/api/platform/`, admin plataforma |

Em dev, `localhost` costuma apontar para o tenant **demo**; `127.0.0.1` cai no **public** (admin plataforma).

## Autenticação

- **App (Vue):** JWT (`/api/auth/login/`), e-mail + senha, usuário `usuarios.User` no schema do tenant.
- **Admin Django (tenant):** `username` + senha, `is_staff`.
- **Admin plataforma:** `OperadorPlataforma` (e-mail), schema public — site admin separado.

## Provisionamento de gabinetes

1. `POST /api/platform/cadastro-gabinete/` (public)
2. Thread em background → `provisionar_gabinete_completo` (schema, migrations, RBAC, admin inicial)

**Produção:** substituir thread por fila (Celery/RQ) e persistência de falhas com retry.

## Front (Vue)

- API tenant: `resolveTenantApiBaseUrl()` — subdomínio `*.localhost` ou host de produção.
- API plataforma: `VITE_PLATFORM_API_BASE_URL` — host public (cadastro de gabinetes).
