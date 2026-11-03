from rest_framework import serializers

from .models import EventoAuditoria


class EventoAuditoriaSerializer(serializers.ModelSerializer):
    acao_label = serializers.CharField(source='get_acao_display', read_only=True)
    usuario_nome = serializers.SerializerMethodField()

    class Meta:
        model = EventoAuditoria
        fields = (
            'id',
            'acao',
            'acao_label',
            'object_repr',
            'usuario_id',
            'usuario_nome',
            'ocorrido_em',
        )
        read_only_fields = fields

    def get_usuario_nome(self, obj: EventoAuditoria) -> str | None:
        if not obj.usuario_id:
            return None
        user = obj.usuario
        nome = getattr(user, 'nome', None)
        if nome:
            return str(nome)
        completo = user.get_full_name().strip() if hasattr(user, 'get_full_name') else ''
        return completo or getattr(user, 'username', None)
