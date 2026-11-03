"""Garante leitura/escrita no schema public (cadastros e tenants)."""

from django_tenants.utils import get_public_schema_name, schema_context


class PublicSchemaMixin:
    def dispatch(self, request, *args, **kwargs):
        with schema_context(get_public_schema_name()):
            return super().dispatch(request, *args, **kwargs)
