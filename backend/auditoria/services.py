from __future__ import annotations

from typing import Any

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model

from .models import EventoAuditoria


def _nome_usuario(user) -> str | None:
    if not user:
        return None
    nome = getattr(user, 'nome', None)
    if nome:
        return str(nome)
    completo = user.get_full_name().strip() if hasattr(user, 'get_full_name') else ''
    return completo or getattr(user, 'username', None)


def registrar_evento_auditoria(usuario, instance: Model, acao: str) -> EventoAuditoria | None:
    if not instance or not instance.pk:
        return None
    if acao not in EventoAuditoria.Acao.values:
        acao_map = {
            'create': EventoAuditoria.Acao.CRIAR,
            'update': EventoAuditoria.Acao.ALTERAR,
            'delete': EventoAuditoria.Acao.EXCLUIR,
        }
        acao = acao_map.get(acao, acao)
    ct = ContentType.objects.get_for_model(instance.__class__)
    return EventoAuditoria.objects.create(
        acao=acao,
        content_type=ct,
        object_id=str(instance.pk),
        object_repr=str(instance)[:255],
        usuario=usuario if getattr(usuario, 'is_authenticated', False) else None,
    )


def montar_rastreabilidade(instance: Model) -> dict[str, Any]:
    """Payload unificado para o frontend (última ação + criação)."""
    if not instance or not getattr(instance, 'pk', None):
        return {}

    ct = ContentType.objects.get_for_model(instance.__class__)
    base_qs = EventoAuditoria.objects.filter(content_type=ct, object_id=str(instance.pk))
    ultimo = base_qs.select_related('usuario').first()
    criacao = base_qs.filter(acao=EventoAuditoria.Acao.CRIAR).order_by('ocorrido_em').last()

    criado_em = None
    if criacao:
        criado_em = criacao.ocorrido_em.isoformat()
    elif hasattr(instance, 'created_at') and instance.created_at:
        criado_em = instance.created_at.isoformat()

    ultima_em = None
    if ultimo:
        ultima_em = ultimo.ocorrido_em.isoformat()
    elif hasattr(instance, 'updated_at') and instance.updated_at:
        ultima_em = instance.updated_at.isoformat()
    elif criado_em:
        ultima_em = criado_em

    ultima_tipo = ultimo.acao if ultimo else (EventoAuditoria.Acao.CRIAR if criacao else None)

    return {
        'criado_em': criado_em,
        'criado_por_id': criacao.usuario_id if criacao and criacao.usuario_id else None,
        'criado_por_nome': _nome_usuario(criacao.usuario) if criacao else None,
        'ultima_acao_em': ultima_em,
        'ultima_acao_por_id': ultimo.usuario_id if ultimo and ultimo.usuario_id else None,
        'ultima_acao_por_nome': _nome_usuario(ultimo.usuario) if ultimo else None,
        'ultima_acao_tipo': ultima_tipo,
    }


def montar_rastreabilidade_em_lote(instances: list[Model]) -> dict[int | str, dict[str, Any]]:
    """Pré-carrega eventos para listas (agrupa por content type)."""
    if not instances:
        return {}

    por_classe: dict[type, list[Model]] = {}
    for obj in instances:
        por_classe.setdefault(obj.__class__, []).append(obj)

    resultado: dict[int | str, dict[str, Any]] = {}
    for model_cls, objs in por_classe.items():
        ct = ContentType.objects.get_for_model(model_cls)
        ids = [str(o.pk) for o in objs if o.pk]
        if not ids:
            continue
        eventos = (
            EventoAuditoria.objects.filter(content_type=ct, object_id__in=ids)
            .select_related('usuario')
            .order_by('-ocorrido_em')
        )
        ultimo_por_id: dict[str, EventoAuditoria] = {}
        criacao_por_id: dict[str, EventoAuditoria] = {}
        for ev in eventos:
            oid = ev.object_id
            if oid not in ultimo_por_id:
                ultimo_por_id[oid] = ev
            if ev.acao == EventoAuditoria.Acao.CRIAR:
                criacao_por_id[oid] = ev

        for obj in objs:
            oid = str(obj.pk)
            ultimo = ultimo_por_id.get(oid)
            criacao = criacao_por_id.get(oid)

            criado_em = None
            if criacao:
                criado_em = criacao.ocorrido_em.isoformat()
            elif hasattr(obj, 'created_at') and obj.created_at:
                criado_em = obj.created_at.isoformat()

            ultima_em = None
            if ultimo:
                ultima_em = ultimo.ocorrido_em.isoformat()
            elif hasattr(obj, 'updated_at') and obj.updated_at:
                ultima_em = obj.updated_at.isoformat()
            elif criado_em:
                ultima_em = criado_em

            ultima_tipo = ultimo.acao if ultimo else (EventoAuditoria.Acao.CRIAR if criacao else None)

            resultado[obj.pk] = {
                'criado_em': criado_em,
                'criado_por_id': criacao.usuario_id if criacao and criacao.usuario_id else None,
                'criado_por_nome': _nome_usuario(criacao.usuario) if criacao else None,
                'ultima_acao_em': ultima_em,
                'ultima_acao_por_id': ultimo.usuario_id if ultimo and ultimo.usuario_id else None,
                'ultima_acao_por_nome': _nome_usuario(ultimo.usuario) if ultimo else None,
                'ultima_acao_tipo': ultima_tipo,
            }

    return resultado
