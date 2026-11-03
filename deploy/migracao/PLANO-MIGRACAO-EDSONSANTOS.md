# Plano de migração — Legado Edson Santos → GabTech

**Tenant:** `gab_edsonsantos` (`edsonsantos.gabtech.app.br`)  
**Fonte:** `public/db_bkp/edsonsantos/edsons79_sys.sql` (MySQL 5.7, ~5,5 MB)  
**Config:** [`edsonsantos.yaml`](edsonsantos.yaml)  
**Inventário:** [`edsonsantos-inventario.json`](edsonsantos-inventario.json) (gerado em 2026-11-03)

---

## 1. Resultado do inventário (executado)

| Entidade | Quantidade | Observação |
|----------|------------|------------|
| Cadastros (`tbCadastro`) | **5.691** | `stts`: 0→4278, 3→905, 2→486, 1→15 |
| CPF preenchido | **577** (~10%) | Chave natural fraca; usar `legacy_id` |
| CPF duplicado | **5** | Dedup na importação |
| Atendimentos | **3.133** | `stts`: 2→2636 concl., 1→476 aberto, 3→8 |
| Órfãos (`vCad` sem cadastro) | **434** | Placeholder ou revisão manual |
| Categorias atendimento | **73** | 16 “secretarias” (`vSecr`) |
| Tags cadastro (`tbVCadTag`) | **1.778** | |
| Eventos agenda | **5.393** | Ignorar `tbEventos-bkp` |
| Legislativo | **875** | Sem módulo 1:1 no GabTech |
| Docs cadastro (meta) | **575** | Requer arquivos hash no disco antigo |
| Docs atendimento (meta) | **3.523** | Idem |
| Usuários legado | **17** | Mapear para `User` do tenant |

**Responsáveis no legado (top atendimentos):** Alex (4)=1486, Alessandra (5)=1009, Sergio (18)=323, Juan (15)=262.

Regenerar inventário:

```bash
cd /var/www/gabtech/backend && source .venv/bin/activate
python manage.py inventario_legado_edsonsantos
```

---

## 2. Objetivos e escopo

### Dentro do escopo (fases 1–4)

- CRM: cidadãos, endereços, marcadores/tags, observações.
- Atendimentos: histórico, macrotema, responsável, status, descrição HTML.
- Agenda: eventos e tipos derivados do campo `tag`.
- Metadados de anexos + cópia de arquivos **se** `media_legacy_root` for informado.

### Fora do escopo inicial (fase 5+)

- `tbCadastro-old`, `tbEventos-bkp`, `tbNews`, `tbChatAtend`, RBAC legado.
- Acervo legislativo com UX completa (avaliar módulo ou Documentos).
- Replicação de senhas `tbUsuarios`.

### Premissas a validar com o gabinete

1. **`stts` cadastro:** confirmar significado de `3` (905 registros) — provável recadastro/arquivo.
2. **`stts` cadastro `2`:** duplicados — **não** importar (486).
3. Importar apenas **`stts=0`** (4278) na fase 1, salvo orientação contrária.
4. Lista de **e-mails** dos assessores para o mapa `usuarios_legado.mapa` no YAML.

---

## 3. Arquitetura ETL

```
edsons79_sys.sql
      │
      ▼
┌─────────────────┐     ┌──────────────────────────┐
│ Parser Python   │────►│ schema gab_edsonsantos   │
│ (core/legado)   │     │ CRM / Atendimentos /     │
└─────────────────┘     │ Agenda / legado_migracao_ref │
      │                 └──────────────────────────┘
      ▼
media_legacy_root ──► backend/media/ (tenant)
```

- **Idempotência:** tabela `legado_migracao_ref` (`tipo`, `legacy_id`, `gabtech_id`).
- **Dry-run:** padrão `true` até homologação.
- **Backup:** `deploy/backup-postgres.sh` imediatamente antes da importação real.

---

## 4. Fases, entregas e critérios de aceite

### Fase 0 — Preparação (1–2 dias)

| # | Tarefa | Responsável |
|---|--------|-------------|
| 0.1 | Validar significado `stts` cadastro/atendimento | Gabinete + dev |
| 0.2 | Obter pasta de **uploads** do sistema PHP | Gabinete/infra |
| 0.3 | Preencher `usuarios_legado.mapa` no YAML | Gabinete |
| 0.4 | Criar usuários assessores no tenant (se faltarem) | Ops |
| 0.5 | Backup PG + tenant vazio ou staging `gab_edsonsantos` | Ops |

**Aceite:** YAML assinado + inventário JSON atualizado.

---

### Fase 1 — CRM (2–4 dias dev + 1 dia validação)

**Importar:** `stts=0` (~4278), endereço, tags `tbVCadTag`, `obs`/`indicado`.

| Legado | GabTech |
|--------|---------|
| `tbCadastro` | `Cidadao` + `Endereco` |
| `tbVCadTag` | `Tag` + M2M marcadores |
| `tbTags` (institucional) | `Tag` tipo contexto |

**Regras:**

- `legacy_id` em `legado_migracao_ref`; CPF só quando válido/único.
- Normalizar telefone; datas `0000-00-00` ignoradas.
- Geocode (opcional): comando pós-import existente no CRM.

**Aceite:** Amostra 30 fichas conferidas; busca por nome/telefone/bairro OK.

---

### Fase 2 — Atendimentos (3–5 dias)

**Importar:** 3133 registros (incl. órfãos conforme YAML).

| Legado | GabTech |
|--------|---------|
| `tbAtendimento` | `Atendimento` |
| `vCat` | `macrotema` + `assunto` (nome categoria) |
| `descr` | `descricao` |
| `dtIni` | `created_at` (fixo na importação) |
| `stts` | `status` (ver YAML) |
| `tipo` | tag “Canal: WhatsApp” etc. |
| `vUsu` | `responsavel` |

**Despacho inicial:** nota pública “Importado do sistema legado (ID …)”.

**Aceite:** Contagem por status/macrotema; 20 casos abertos/concluídos lidos pela equipe.

---

### Fase 3 — Agenda (2–3 dias)

**Importar:** ~5393 `tbEventos` → `Evento` + `TipoEvento`.

- `tag` → tipo; `stts`/cor → status cancelado quando aplicável.
- Convidados M2M só se houver vínculo explícito (baixa prioridade).

**Aceite:** Calendário navegável; sessões CMMC visíveis no mês de amostra.

---

### Fase 4 — Anexos (2–4 dias, depende dos arquivos)

- `tbCadastroDocs` → `DocumentoAnexo` (currículo/outros).
- `tbAtendimentoDocs` → `Anexo` do atendimento.
- Arquivos: `{media_legacy_root}/{arquivo}` → `MEDIA_ROOT` tenant.

**Aceite:** 95% dos arquivos existentes copiados; log dos ausentes.

---

### Fase 5 — Legislativo (opcional, 3–7 dias)

875 itens `tbLegislativo` — opções:

1. CSV consultivo + links CMMC (rápido).
2. `Documento` no módulo Documentos (metadados + link).
3. Modelo `Proposicao` (feature nova).

**Aceite:** Equipe encontra PL/indicação por número/ano.

---

## 5. Cronograma sugerido

| Semana | Fase | Ambiente |
|--------|------|----------|
| S1 | 0 + 1 (dry-run) | staging ou tenant com flag |
| S2 | 1 (real) + 2 (dry-run) | homologação |
| S3 | 2 (real) + 3 | homologação |
| S4 | 4 (anexos) + validação usuário | produção (janela) |

Produção: preferir **import em tenant já criado** com poucos dados de teste, ou restore de backup pós-teste.

---

## 6. Comandos (roadmap implementação)

| Comando | Status |
|---------|--------|
| `python manage.py inventario_legado_edsonsantos` | **Implementado** |
| `python manage.py migrar_legado_edsonsantos --dry-run` | **Fase 1 OK** |
| `python manage.py migrar_legado_edsonsantos --executar` | **Fase 1 OK** (use após validar dry-run) |
| `python manage.py migrar_legado_edsonsantos --fase 2 …` | **Implementado** (2026-11-03) |
| `python manage.py migrar_legado_edsonsantos --fase 3 …` | **Implementado** (2026-11-03) |
| `python manage.py migrar_legado_edsonsantos --fase 4 …` | **Implementado** — requer `media_legacy_root` para `--executar` |
| `python manage.py geocodificar_crm_lote --schema gab_edsonsantos …` | **Implementado** — pós-migração (mapa territorial) |

Exemplos:

```bash
cd backend && source .venv/bin/activate
python manage.py migrar_legado_edsonsantos --dry-run
python manage.py migrar_legado_edsonsantos --executar --limit 50   # amostra
python manage.py migrar_legado_edsonsantos --executar            # ~4512 cidadãos (stts=0)
```

---

## 7. Riscos e mitigação

| Risco | Mitigação |
|-------|-----------|
| CPF vazio/duplicado | Chave `legacy_id`; dedup parametrizado |
| 434 atendimentos órfãos | Cidadão placeholder + lista para merge manual |
| HTML/`&ccedil;` na descrição | Sanitizar ou converter entidades |
| Anexos ausentes | Modo `registrar_log`; não abortar |
| Macrotema errado | Ajustar YAML; re-run idempotente |
| Performance | Lotes 500/200; transações por batch |

---

## 8. Checklist go-live pós-migração

- [ ] Backup PG pós-import verificado (restore test)
- [ ] Login assessores + permissões RBAC
- [ ] Contagens legado vs GabTech (relatório por fase)
- [ ] Equipe treinada no fluxo novo (sem depender do legado)
- [ ] Link cadastro self-service desligado ou só por convite (já operacional)

---

## 9. Próximo passo imediato (dev)

1. Migration tenant: model `LegadoMigracaoRef`.
2. Implementar `migrar_legado_edsonsantos --fase 1 --dry-run`.
3. Homologar com ~100 cadastros reais + revisão do gabinete.

Atualizar este plano quando fases forem concluídas (data, responsável, desvios).
