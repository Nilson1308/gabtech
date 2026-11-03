"""Agregações para dashboards executivo e mapa territorial."""

from __future__ import annotations

from collections import Counter, defaultdict
from decimal import Decimal
from typing import Any

from django.utils import timezone

from agenda.models import Evento
from atendimentos.models import Atendimento, Despacho, Macrotema
from atendimentos.visibility import filtrar_atendimentos_visiveis
from auditoria.models import EventoAuditoria
from auditoria.services import montar_rastreabilidade
from crm.models import Cidadao
from documentos.models import Documento

MOGI_CENTRO = {'lat': -23.5227, 'lng': -46.1879, 'zoom': 12}

AGRUPAMENTO_MACROTEMA = 'macrotema'
AGRUPAMENTO_MACROTEMA_BAIRRO = 'macrotema_bairro'
AGRUPAMENTOS_VALIDOS = frozenset({AGRUPAMENTO_MACROTEMA, AGRUPAMENTO_MACROTEMA_BAIRRO})

STATUS_LABEL = {
    'aberto': 'Aberto',
    'em_andamento': 'Em andamento',
    'aguardando_terceiros': 'Aguardando terceiros',
    'concluido': 'Concluído',
}


def _atendimentos_visiveis(user):
    base = Atendimento.objects.select_related(
        'macrotema',
        'responsavel',
        'cidadao',
        'cidadao__endereco',
    )
    return filtrar_atendimentos_visiveis(base, user)


def _is_atrasado(atendimento: Atendimento, agora) -> bool:
    if atendimento.status == Atendimento.Status.CONCLUIDO:
        return False
    if not atendimento.sla_vencimento:
        return False
    return atendimento.sla_vencimento < agora


def build_executivo(user) -> dict[str, Any]:
    agora = timezone.now()
    qs = _atendimentos_visiveis(user)
    lista = list(qs)

    por_responsavel: dict[int, dict[str, Any]] = defaultdict(
        lambda: {
            'concluidos': 0,
            'em_andamento': 0,
            'atrasados': 0,
            'total': 0,
            'nome': '',
        }
    )

    gargalo_contagem: Counter[int] = Counter()
    macrotema_map: dict[int, Macrotema] = {}

    for att in lista:
        rid = att.responsavel_id
        bucket = por_responsavel[rid]
        bucket['nome'] = att.responsavel.nome if att.responsavel else '—'
        bucket['total'] += 1
        if att.status == Atendimento.Status.CONCLUIDO:
            bucket['concluidos'] += 1
        else:
            bucket['em_andamento'] += 1
            if _is_atrasado(att, agora):
                bucket['atrasados'] += 1
                gargalo_contagem[att.macrotema_id] += 1
                macrotema_map[att.macrotema_id] = att.macrotema

    produtividade = []
    for uid, dados in por_responsavel.items():
        total = dados['total']
        concluidos = dados['concluidos']
        taxa = round((concluidos / total) * 100, 1) if total else 0.0
        produtividade.append(
            {
                'user_id': str(uid),
                'nome_usuario': dados['nome'],
                'concluidos': concluidos,
                'atrasados': dados['atrasados'],
                'em_andamento': dados['em_andamento'],
                'total': total,
                'taxa_sucesso': taxa,
            }
        )
    produtividade.sort(key=lambda x: (-x['taxa_sucesso'], -x['concluidos']))

    gargalos = []
    for mid, qtd in gargalo_contagem.most_common():
        macro = macrotema_map[mid]
        gargalos.append(
            {
                'macrotema': macro.nome,
                'atrasados': qtd,
                'cor': macro.cor,
            }
        )

    atendimento_ids = qs.values_list('pk', flat=True)
    atividades = _montar_atividades(user, atendimento_ids)

    return {
        'produtividade': produtividade,
        'atividades_recentes': atividades,
        'gargalos': gargalos,
    }


def _descricao_evento_auditoria(ev: EventoAuditoria) -> str:
    rotulo = {
        EventoAuditoria.Acao.CRIAR: 'Criou',
        EventoAuditoria.Acao.ALTERAR: 'Alterou',
        EventoAuditoria.Acao.EXCLUIR: 'Excluiu',
    }.get(ev.acao, 'Alterou')
    modelo = ev.content_type.model.replace('_', ' ')
    alvo = ev.object_repr or ev.object_id
    return f'{rotulo} {modelo}: «{alvo}»'


def _montar_atividades(user, atendimento_ids) -> list[dict[str, Any]]:
    itens: list[dict[str, Any]] = []
    visiveis = list(atendimento_ids)

    for ev in EventoAuditoria.objects.select_related('usuario', 'content_type').order_by('-ocorrido_em')[:35]:
        autor_nome = ev.usuario.nome if ev.usuario else 'Sistema'
        autor_id = str(ev.usuario_id) if ev.usuario_id else ''
        itens.append(
            {
                'id': f'aud-{ev.pk}',
                'tipo': 'auditoria_crud',
                'usuario': autor_nome,
                'usuario_id': autor_id,
                'descricao': _descricao_evento_auditoria(ev),
                'timestamp': ev.ocorrido_em.isoformat(),
                'icone': 'history',
                'cor': '#64748b',
            }
        )

    despachos = (
        Despacho.objects.filter(atendimento_id__in=visiveis)
        .select_related('autor', 'atendimento', 'responsavel_novo')
        .order_by('-created_at')[:40]
    )
    for d in despachos:
        autor_nome = d.autor.nome if d.autor else 'Sistema'
        autor_id = str(d.autor_id) if d.autor_id else ''
        proto = d.atendimento.protocolo
        if d.tipo == Despacho.Tipo.REATRIBUICAO:
            dest = d.responsavel_novo.nome if d.responsavel_novo else 'outro assessor'
            itens.append(
                {
                    'id': f'desp-{d.pk}',
                    'tipo': 'ticket_transferido',
                    'usuario': autor_nome,
                    'usuario_id': autor_id,
                    'descricao': f'Transferiu o Atendimento #{proto} para {dest}',
                    'timestamp': d.created_at.isoformat(),
                    'icone': 'arrow-right',
                    'cor': '#3b82f6',
                }
            )
        elif d.tipo == Despacho.Tipo.MUDANCA_STATUS:
            novo = STATUS_LABEL.get(d.status_novo, d.status_novo or 'atualizado')
            itens.append(
                {
                    'id': f'desp-{d.pk}',
                    'tipo': 'status_alterado',
                    'usuario': autor_nome,
                    'usuario_id': autor_id,
                    'descricao': f'Marcou Atendimento #{proto} como {novo}',
                    'timestamp': d.created_at.isoformat(),
                    'icone': 'check-circle' if d.status_novo == 'concluido' else 'play-circle',
                    'cor': '#10b981' if d.status_novo == 'concluido' else '#f59e0b',
                }
            )

    cidadaos = Cidadao.objects.order_by('-created_at')[:8]
    for c in cidadaos:
        rast = montar_rastreabilidade(c)
        autor_nome = rast.get('criado_por_nome') or rast.get('ultima_acao_por_nome') or '—'
        autor_id = rast.get('criado_por_id') or rast.get('ultima_acao_por_id') or ''
        ts = rast.get('criado_em') or c.created_at.isoformat()
        itens.append(
            {
                'id': f'crm-{c.pk}',
                'tipo': 'cidadao_criado',
                'usuario': autor_nome,
                'usuario_id': str(autor_id) if autor_id else '',
                'descricao': f'Cadastrou cidadão "{c.nome}" no CRM',
                'timestamp': ts,
                'icone': 'user-plus',
                'cor': '#10b981',
            }
        )

    eventos = Evento.objects.select_related('criado_por').order_by('-created_at')[:10]
    for ev in eventos:
        criador = ev.criado_por.nome if ev.criado_por else user.nome
        criador_id = str(ev.criado_por_id) if ev.criado_por_id else str(user.pk)
        itens.append(
            {
                'id': f'ev-{ev.pk}',
                'tipo': 'evento_criado',
                'usuario': criador,
                'usuario_id': criador_id,
                'descricao': f'Criou evento "{ev.titulo}"',
                'timestamp': ev.created_at.isoformat(),
                'icone': 'calendar',
                'cor': '#ec4899',
            }
        )

    docs = (
        Documento.objects.filter(status=Documento.Status.FINALIZADO)
        .select_related('autor')
        .order_by('-updated_at')[:10]
    )
    for doc in docs:
        autor = doc.autor.nome if doc.autor else user.nome
        itens.append(
            {
                'id': f'doc-{doc.pk}',
                'tipo': 'documento_assinado',
                'usuario': autor,
                'usuario_id': str(doc.autor_id),
                'descricao': f'Documento finalizado: "{doc.titulo[:80]}"',
                'timestamp': doc.updated_at.isoformat(),
                'icone': 'file-check',
                'cor': '#f97316',
            }
        )

    itens.sort(key=lambda x: x['timestamp'], reverse=True)
    return itens[:30]


def _aplicar_filtros_territorial(
    queryset,
    *,
    macrotema_id: int | None,
    bairro: str | None,
):
    if macrotema_id:
        queryset = queryset.filter(macrotema_id=macrotema_id)
    if bairro:
        queryset = queryset.filter(cidadao__endereco__bairro=bairro)
    return queryset


def _filtros_disponiveis(pendentes) -> dict[str, Any]:
    macro_ids = pendentes.values_list('macrotema_id', flat=True).distinct()
    macrotemas = [
        {'id': m.pk, 'nome': m.nome, 'cor': m.cor}
        for m in Macrotema.objects.filter(pk__in=macro_ids).order_by('nome')
    ]
    bairros = sorted(
        {
            b
            for b in pendentes.filter(cidadao__endereco__bairro__gt='').values_list(
                'cidadao__endereco__bairro',
                flat=True,
            )
            if b
        }
    )
    return {'macrotemas': macrotemas, 'bairros': bairros}


def _radius_zona(pendentes_count: int, *, por_bairro: bool) -> int:
    if por_bairro:
        return min(2200, 500 + pendentes_count * 100)
    return min(3200, 900 + pendentes_count * 150)


def _montar_zonas(
    pendentes,
    agrupamento: str,
) -> list[dict[str, Any]]:
    por_bairro = agrupamento == AGRUPAMENTO_MACROTEMA_BAIRRO

    if por_bairro:
        buckets: dict[tuple[int, str], dict[str, Any]] = defaultdict(
            lambda: {
                'lat_sum': Decimal('0'),
                'lng_sum': Decimal('0'),
                'count_geo': 0,
                'pendentes': 0,
                'macro': None,
                'bairro': '',
            }
        )
        for att in pendentes.select_related('cidadao__endereco', 'macrotema'):
            end = getattr(att.cidadao, 'endereco', None)
            if not end or not end.bairro:
                continue
            if end.latitude is None or end.longitude is None:
                continue
            chave = (att.macrotema_id, end.bairro)
            bucket = buckets[chave]
            bucket['macro'] = att.macrotema
            bucket['bairro'] = end.bairro
            bucket['pendentes'] += 1
            bucket['lat_sum'] += end.latitude
            bucket['lng_sum'] += end.longitude
            bucket['count_geo'] += 1

        zonas = []
        for (mid, bairro_nome), dados in sorted(
            buckets.items(),
            key=lambda x: (-x[1]['pendentes'], x[1]['bairro']),
        ):
            if dados['count_geo'] == 0 or not dados['macro']:
                continue
            macro = dados['macro']
            lat = float(dados['lat_sum'] / dados['count_geo'])
            lng = float(dados['lng_sum'] / dados['count_geo'])
            pendentes_count = dados['pendentes']
            zonas.append(
                {
                    'id': f'macro-{mid}-bairro-{bairro_nome}',
                    'nome': f'{macro.nome} — {bairro_nome}',
                    'bairro': bairro_nome,
                    'macrotema_id': mid,
                    'lat': lat,
                    'lng': lng,
                    'radius': _radius_zona(pendentes_count, por_bairro=True),
                    'atendimentos_pendentes': pendentes_count,
                    'macrotema': macro.nome,
                    'cor': macro.cor,
                }
            )
        return zonas

    por_macrotema: dict[int, dict[str, Any]] = defaultdict(
        lambda: {
            'lat_sum': Decimal('0'),
            'lng_sum': Decimal('0'),
            'count_geo': 0,
            'pendentes': 0,
            'macro': None,
        }
    )

    for att in pendentes.select_related('cidadao__endereco', 'macrotema'):
        end = getattr(att.cidadao, 'endereco', None)
        if not end or end.latitude is None or end.longitude is None:
            continue
        mid = att.macrotema_id
        bucket = por_macrotema[mid]
        bucket['macro'] = att.macrotema
        bucket['pendentes'] += 1
        bucket['lat_sum'] += end.latitude
        bucket['lng_sum'] += end.longitude
        bucket['count_geo'] += 1

    zonas = []
    for mid, dados in sorted(
        por_macrotema.items(),
        key=lambda x: -x[1]['pendentes'],
    ):
        if dados['count_geo'] == 0 or not dados['macro']:
            continue
        macro = dados['macro']
        lat = float(dados['lat_sum'] / dados['count_geo'])
        lng = float(dados['lng_sum'] / dados['count_geo'])
        pendentes_count = dados['pendentes']
        zonas.append(
            {
                'id': f'macro-{mid}',
                'nome': macro.nome,
                'bairro': '',
                'macrotema_id': mid,
                'lat': lat,
                'lng': lng,
                'radius': _radius_zona(pendentes_count, por_bairro=False),
                'atendimentos_pendentes': pendentes_count,
                'macrotema': macro.nome,
                'cor': macro.cor,
            }
        )
    return zonas


def build_territorial(
    user,
    *,
    agrupamento: str = AGRUPAMENTO_MACROTEMA,
    macrotema_id: int | None = None,
    bairro: str | None = None,
) -> dict[str, Any]:
    if agrupamento not in AGRUPAMENTOS_VALIDOS:
        agrupamento = AGRUPAMENTO_MACROTEMA

    qs = _atendimentos_visiveis(user)
    pendentes_base = qs.exclude(status=Atendimento.Status.CONCLUIDO)
    filtros_disp = _filtros_disponiveis(pendentes_base)

    pendentes = _aplicar_filtros_territorial(
        pendentes_base,
        macrotema_id=macrotema_id,
        bairro=bairro,
    )
    qs_pins = _aplicar_filtros_territorial(
        qs,
        macrotema_id=macrotema_id,
        bairro=bairro,
    )

    cidadao_ids = qs_pins.values_list('cidadao_id', flat=True).distinct()
    pins_qs = (
        Cidadao.objects.filter(pk__in=cidadao_ids, endereco__latitude__isnull=False)
        .select_related('endereco')
        .prefetch_related('marcadores')
    )

    pins = []
    for c in pins_qs:
        end = c.endereco
        pins.append(
            {
                'id': str(c.pk),
                'nome': c.nome,
                'lat': float(end.latitude),
                'lng': float(end.longitude),
                'endereco': _format_endereco(end),
                'tags': list(c.marcadores.values_list('nome', flat=True)),
            }
        )

    zonas = _montar_zonas(pendentes, agrupamento)

    return {
        'pins_cidadaos': pins,
        'zonas_calor': zonas,
        'centro': MOGI_CENTRO,
        'meta': {
            'agrupamento': agrupamento,
            'macrotema_id': macrotema_id,
            'bairro': bairro or '',
        },
        'filtros_disponiveis': filtros_disp,
    }


def _format_endereco(end) -> str:
    partes = []
    if end.logradouro:
        partes.append(end.logradouro)
    if end.bairro:
        partes.append(end.bairro)
    cidade = end.cidade or 'Mogi das Cruzes'
    uf = end.estado or 'SP'
    partes.append(f'{cidade}/{uf}')
    return ', '.join(partes)
