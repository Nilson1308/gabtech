"""Agregações leves para sidebar de documentos (sem listar todos os registros)."""

from __future__ import annotations

from django.db.models import Count

from .models import Documento, EtiquetaDocumento


def build_documentos_resumo() -> dict:
    por_status = {
        row['status']: row['c']
        for row in Documento.objects.values('status').annotate(c=Count('id'))
    }
    por_pasta = {
        str(row['pasta_id']): row['c']
        for row in Documento.objects.filter(pasta_id__isnull=False)
        .values('pasta_id')
        .annotate(c=Count('id'))
    }
    sem_pasta = Documento.objects.filter(pasta__isnull=True).count()
    por_etiqueta = {
        str(row['id']): row['c']
        for row in EtiquetaDocumento.objects.annotate(c=Count('documentos')).values('id', 'c')
    }
    total = Documento.objects.count()

    return {
        'total': total,
        'sem_pasta': sem_pasta,
        'por_status': {
            'rascunho': por_status.get(Documento.Status.RASCUNHO, 0),
            'aguardando_assinatura': por_status.get(Documento.Status.AGUARDANDO_ASSINATURA, 0),
            'finalizado': por_status.get(Documento.Status.FINALIZADO, 0),
        },
        'por_pasta': por_pasta,
        'por_etiqueta': por_etiqueta,
    }
