# Checklist e operação em produção

Referência para o ambiente **gabtech.app.br** (VPS + nginx + Gunicorn + Celery + PostgreSQL + Redis).

## Estado atual (base implementada)

| Área | Situação |
|------|----------|
| API | Gunicorn (`gabtech-api`), schema public em `api.gabtech.app.br` |
| Front | `dist/` servido pelo nginx (`app`, subdomínios tenant, `gabtech`, `www`) |
| Tenants | Um schema PostgreSQL por gabinete (`django-tenants`) |
| Cadastro | `POST /api/platform/cadastro-gabinete/` + fila Celery `plataforma.provisionar_cadastro` |
| Admin plataforma | `https://api.gabtech.app.br/admin/` — `OperadorPlataforma` (não superuser Django) |
| Signup | `GABTECH_SIGNUP_ENABLED` + opcional `GABTECH_SIGNUP_CODIGO_CONVITE` |
| Cache / rate-limit signup | Redis (`REDIS_URL`, db separado do broker Celery) |
| Backup | Cron diário — ver [Backups](#backups) |
| Mídia | Disco local `backend/media/` — ver [Mídia e uploads](#mídia-e-uploads) |

## Crítico (já tratado no deploy; revisar em novos ambientes)

| Item | Notas |
|------|--------|
| `DJANGO_DEBUG=false` | Obrigatório; `SECRET_KEY` forte (≥ 40 chars, não placeholder) |
| `SHOW_PUBLIC_IF_NO_TENANT_FOUND=false` | Evita cair no schema public com host errado |
| HTTPS | Certbot; `SECURE_*` no Django com proxy nginx |
| `ALLOWED_HOSTS` | IP da VPS + `api`, `app`, `.gabtech.app.br` |
| CORS | Origens HTTPS explícitas + regex subdomínios tenant |
| Celery | Worker deve escutar a fila **`celery`** (`deploy/gabtech-celery.service`) |
| Secrets | `backend/.env` fora do git |

## Novo gabinete — DNS e TLS (rotina operacional, não “dívida”)

Não usamos wildcard **A** `*.gabtech.app.br` no Registro.br. Para **cada** slug novo:

1. Criar registro **A** `{slug}` → IP da VPS (ex.: `edsonsantos` → `168.231.91.74`).
2. Aguardar propagação DNS.
3. Cadastro (Vue ou API) dispara provisionamento; com `GABTECH_SSL_EXPAND_ON_PROVISION=true`, o worker chama `deploy/certbot-expand-domain.sh` para incluir `{slug}.gabtech.app.br` no certificado.

Alternativa futura: cert wildcard via **TXT** (`deploy/certbot-wildcard-dns.sh`), sem A por slug.

**Cadastro self-service:** a rota `/cadastro-gabinete` permanece no SPA, mas o link não aparece na tela de login — o operador envia o URL (`https://app.gabtech.app.br/cadastro-gabinete`) quando quiser abrir novas contas.

**Admin plataforma → Adicionar gabinete:** cria tenant/schema, mas **não** executa provisionamento completo (admin RBAC, etc.). Preferir cadastro pela fila ou `manage.py criar_gabinete`.

## Backups

- Script: `deploy/backup-postgres.sh` → `/var/backups/gabtech/`.
- Cron: `/etc/cron.d/gabtech-backup` — `0 3 * * * root ...`.
- Validação: `deploy/restore-postgres-test.sh` (DB isolado `gabtech_restore_test`).

## Mídia e uploads

**Decisão atual:** arquivos em `MEDIA_ROOT` local na VPS (`backend/media/`), servidos via nginx em `/media/`.

**Evolução planejada (não bloqueia operação):**

- Storage object (S3-compatible) + `django-storages` ou equivalente.
- Backup de mídia junto com política de retenção.
- Limites de tamanho para logo em data URL no cadastro (hoje já validado no backend).

Documentar aqui quando a migração for priorizada.

## Melhorias desejáveis (nice to have)

| Item | Objetivo |
|------|----------|
| Monitoramento | Sentry/Datadog, alertas 5xx e falha de provisionamento |
| E-mail transacional | Confirmação de cadastro, reset de senha, aviso ops em `CadastroGabinete.FALHOU` |
| JWT | Revisar TTL, refresh rotation, blacklist se logout obrigatório |
| Testes | Smoke tests: auth tenant, cadastro + mock Celery, health public/tenant |
| Logs | Request ID, schema tenant em logs estruturados |

## Front (SPA)

| Item | Ação |
|------|------|
| Build | `npm run build` com `.env.production` |
| API tenant | Resolver por hostname (`VITE_TENANT_DOMAIN_SUFFIX`); não fixar demo em prod |
| Cadastro | `VITE_PLATFORM_API_BASE_URL=https://api.gabtech.app.br` |
| Rotas | Fallback `index.html` no nginx para Vue Router |

## Comandos úteis

```bash
# Hosts da plataforma no schema public
python manage.py garantir_hosts_plataforma

# Operador admin plataforma
python manage.py criar_operador_plataforma --email=... --senha=...

# Cadastros presos (alternativa manual à fila)
python manage.py processar_cadastros_pendentes

# SSL manual para um subdomínio
sudo /var/www/gabtech/deploy/certbot-expand-domain.sh slug.gabtech.app.br

sudo systemctl restart gabtech-api gabtech-celery
```

## Arquitetura (referência)

```
                    ┌─────────────┐
   Browser ────────►│ nginx/TLS   │
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
      SPA (dist)    Gunicorn (API)    PostgreSQL
                    + Celery (fila celery)
                    + Redis (cache + broker)
```

## Health checks

- Tenant: `https://{tenant}/health/` → `{"status":"ok"}`
- Public: `https://api.gabtech.app.br/health/` → inclui `"schema":"public"`
