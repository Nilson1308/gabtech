# Análise comercial (referência interna)

Documento de apoio para decisões futuras de produto, precificação e go-to-market. Não substitui estudo de mercado atualizado.

## Posicionamento

Plataforma SaaS multi-tenant para **gabinetes políticos e equipes de mandato**: CRM de cidadãos, atendimentos/SLA, agenda, documentos, cerimonial (eventos/convidados), serviços (talentos, cursos, assistência), governança e analytics — com **RBAC por módulo** e **auditoria/rastreabilidade** em CRUDs.

Diferenciais típicos frente a planilhas + WhatsApp:

- Dados centralizados por mandato/tenant
- Permissões granulares (ex.: cerimonial sem acesso total ao CRM)
- Rastreio de quem alterou o quê e quando
- Módulos integrados (mesmo cadastro de cidadão em atendimento, evento, etc.)

## Concorrentes e alternativas (visão geral)

| Tipo | Exemplos / padrão | Observação |
|------|-------------------|------------|
| ERP/CRM genérico | Pipedrive, HubSpot, Zoho | Pouco alinhado a mandato, cerimonial, SLA político |
| Gestão de gabinete / política (BR) | Soluções locais, consultorias + Excel | Fragmentado; poucos com multi-módulo + RBAC forte |
| Atendimento ao cidadão | Ouvidoria municipal, ferramentas de ticket | Sobrepõe só parte de “atendimentos” |
| Agenda/cerimonial avulso | Ferramentas de eventos | Não ligam ao CRM do eleitor |

Posicionamento recomendado: **nicho mandato/gabinete**, não CRM horizontal.

## Modelo de receita (hipóteses)

- **Assinatura mensal/anual por tenant** (mandato ou organização)
- Tiers por: número de usuários, módulos habilitados, volume (cidadãos/atendimentos) ou “plano completo”
- Serviços: implantação, migração de dados, treinamento, customização

Ordem de magnitude (ilustrativo, validar com pesquisa):

- Plano base mandato pequeno: faixa baixa centenas R$/mês
- Mandato médio / equipe maior: mid hundreds a low thousands R$/mês
- Enterprise / multi-unidade: negociação anual

## Custos e margem

- Infra: app + DB por tenant ou schema compartilhado; backups; monitoramento
- Suporte e onboarding humano costumam dominar em clientes políticos (curva de adoção)
- Margem bruta SaaS típica é alta **se** churn baixo e suporte controlado (documentação, autoserviço, RBAC claro)

## Riscos

- Ciclo eleitoral → churn natural entre mandatos; mitigar com multi-mandato, histórico exportável, contratos com partidos/assessorias
- Sensibilidade a dados pessoais (LGPD): auditoria, mínimo privilégio, DPA
- Dependência de champion no gabinete (troca de equipe)

## Próximos passos comerciais sugeridos

1. Definir **ICP** (tamanho de gabinete, módulos “must have”)
2. 3–5 entrevistas com cerimonialistas / chief of staff de mandato
3. Piloto pago em 1–2 gabinetes com métricas: tempo de resposta SLA, convites/eventos, adoção CRM
4. Página de pricing alinhada a módulos (`ler_crm`, cerimonial, atendimentos, etc.)
5. Material de vendas: segurança, auditoria, multi-usuário

---

*Última atualização: out/2025 — revisar anualmente ou antes de rodada comercial.*
