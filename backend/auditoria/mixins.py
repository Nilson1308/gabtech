from rest_framework import serializers

from .models import EventoAuditoria
from .services import montar_rastreabilidade, montar_rastreabilidade_em_lote, registrar_evento_auditoria


class AuditoriaCRUDMixin:
    """Registra create/update/delete no log central (ViewSets DRF)."""

    def perform_create(self, serializer):
        super().perform_create(serializer)
        self._auditoria_registrar(serializer.instance, EventoAuditoria.Acao.CRIAR)

    def perform_update(self, serializer):
        super().perform_update(serializer)
        self._auditoria_registrar(serializer.instance, EventoAuditoria.Acao.ALTERAR)

    def perform_destroy(self, instance):
        self._auditoria_registrar(instance, EventoAuditoria.Acao.EXCLUIR)
        super().perform_destroy(instance)

    def _auditoria_registrar(self, instance, acao: str) -> None:
        request = getattr(self, 'request', None)
        user = getattr(request, 'user', None) if request else None
        registrar_evento_auditoria(user, instance, acao)


class RastreabilidadeModelSerializer(serializers.ModelSerializer):
    """
    Expõe `rastreabilidade` (última ação + criação) nos payloads da API.
    Desative em serializers resumo com Meta.rastreabilidade_habilitada = False.
    """

    rastreabilidade = serializers.SerializerMethodField(read_only=True)

    class Meta:
        rastreabilidade_habilitada = True

    def get_fields(self):
        fields = super().get_fields()
        meta = getattr(self, 'Meta', None)
        habilitada = meta is None or getattr(meta, 'rastreabilidade_habilitada', True)
        if not habilitada:
            fields.pop('rastreabilidade', None)
            return fields
        if 'rastreabilidade' not in fields:
            fields['rastreabilidade'] = serializers.SerializerMethodField(read_only=True)
        return fields

    def get_rastreabilidade(self, obj):
        meta = getattr(self, 'Meta', None)
        if meta and not getattr(meta, 'rastreabilidade_habilitada', True):
            return None
        cache = getattr(self, '_rastreabilidade_cache', None)
        if cache is not None and obj.pk in cache:
            return cache[obj.pk]
        return montar_rastreabilidade(obj)

    @classmethod
    def prefetch_rastreabilidade(cls, serializer, instances: list):
        """Chame após construir serializer em list actions N+1-safe."""
        meta = getattr(serializer, 'Meta', None)
        if meta and not getattr(meta, 'rastreabilidade_habilitada', True):
            return
        serializer._rastreabilidade_cache = montar_rastreabilidade_em_lote(instances)
