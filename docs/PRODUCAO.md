# Checklist para produção

Estado do repositório: **MVP funcional em dev**; itens abaixo são necessários ou fortemente recomendados antes do go-live.

## Crítico (bloqueia go-live seguro)

| Item | Situação atual | Ação |
|------|----------------|------|
| `DJANGO_DEBUG=false` | Default dev `true` | `.env` produção + fail se SECRET_KEY fraca |
| `DJANGO_SECRET_KEY` | Placeholder em dev | Segredo forte, rotação planejada |
| `SHOW_PUBLIC_IF_NO_TENANT_FOUND` | `true` em dev | **`false` em prod** — evita cair no public em host errado |
| Servidor WSGI | Só `runserver` / `serve.sh` | **Gunicorn/uWSGI** + reverse proxy (nginx/Caddy) |
| HTTPS | HTTP local | TLS, `SECURE_SSL_REDIRECT`, cookies seguros |
| `ALLOWED_HOSTS` / domínios | `.localhost` | Domínios reais por tenant + API public |
| CORS | Regex `*.localhost` | Origens explícitas do front (`https://app...`, `https://*.seudominio.com`) |
| Secrets no git | `.env` no `.gitignore` | Validar CI/CD e secrets manager |
| Provisionamento | **Thread** in-process | **Fila** (Celery + Redis), idempotência, alertas em falha |
| Cache rate-limit signup | Sem `CACHES` (memória local) | **Redis** para `GABTECH_SIGNUP_RATE_LIMIT` entre workers |
| Backups PostgreSQL | Não automatizado no repo | Backup diário + restore testado (schemas multi-tenant) |
| Media/uploads | `MEDIA_ROOT` local | S3-compatible ou volume replicado |
| JWT | 8h access, sem blacklist | Revisar TTL, refresh rotation, blacklist se logout obrigatório |

## Importante (qualidade operacional)

| Item | Notas |
|------|--------|
| `collectstatic` + CDN/nginx | Servir `/static/` do admin e DRF |
| Health checks | `/health/` tenant e public para load balancer |
| Logs estruturados | Request ID, tenant schema, erros 5xx |
| Monitoramento | Sentry/Datadog, métricas DB e fila |
| E-mail transacional | Confirmação cadastro, reset senha, falha provisionamento |
| `GABTECH_SIGNUP_CODIGO_CONVITE` | Convite em prod se não quiser signup aberto |
| Política de senha | Já usa validadores Django; comunicar ao usuário |
| Logo/identidade | Data URL em DB — considerar limite tamanho e storage object |
| Testes automatizados | Poucos no repo — smoke tests API auth + provisionamento |

## Front (SPA)

| Item | Ação |
|------|------|
| Build | `npm run build` → servir `dist/` via nginx ou object storage |
| Variáveis | `VITE_API_BASE_URL` **não** fixar demo; resolver por hostname em prod |
| `VITE_PLATFORM_API_BASE_URL` | URL da API public (cadastro) |
| Rotas SPA | Fallback `index.html` para Vue Router |

## Deploy sugerido (referência)

```
                    ┌─────────────┐
   Browser ────────►│ nginx/TLS   │
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
      SPA (dist)    Gunicorn (API)    PostgreSQL
                    + Celery workers
                    + Redis (cache/fila)
```

## Comandos pós-deploy (primeira vez)

```bash
python manage.py migrate_schemas --shared
python manage.py migrate_schemas
python manage.py criar_operador_plataforma --email=ops@... --senha=...
# Tenant demo opcional em staging:
python manage.py bootstrap_demo
```

## O que já está pronto para produção (base)

- Multi-tenant por schema PostgreSQL
- RBAC por permissões no backend
- JWT + API REST modular
- Self-service cadastro gabinete (schema public)
- CORS configurável por env
- Docker Compose só para Postgres (dev) — estender para prod conforme infra
