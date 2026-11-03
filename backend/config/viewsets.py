from rest_framework import viewsets

from auditoria.mixins import AuditoriaCRUDMixin


class GabineteModelViewSet(AuditoriaCRUDMixin, viewsets.ModelViewSet):
    """ModelViewSet padrão com log de auditoria em create/update/delete."""


class GabineteReadOnlyModelViewSet(AuditoriaCRUDMixin, viewsets.ReadOnlyModelViewSet):
    """Somente leitura; mixin não altera fluxo sem escrita."""
