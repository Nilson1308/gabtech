from django.contrib.auth import get_user_model
from rest_framework import serializers

from auditoria.mixins import RastreabilidadeModelSerializer

from atendimentos.serializers import CidadaoResumoSerializer, UsuarioResumoSerializer
from crm.models import Cidadao

from .models import Espaco, Evento, TipoEvento

User = get_user_model()


class TipoEventoSerializer(RastreabilidadeModelSerializer):
    class Meta:
        model = TipoEvento
        fields = ('id', 'nome', 'cor', 'icone', 'descricao', 'ativo')


class EspacoSerializer(RastreabilidadeModelSerializer):
    class Meta:
        model = Espaco
        fields = (
            'id',
            'nome',
            'descricao',
            'capacidade',
            'icone',
            'cor',
            'ativo',
            'created_at',
        )
        read_only_fields = ('id', 'created_at')


class EventoSerializer(RastreabilidadeModelSerializer):
    tipo = TipoEventoSerializer(read_only=True)
    espaco = EspacoSerializer(read_only=True)
    criado_por = UsuarioResumoSerializer(read_only=True)
    convidados = CidadaoResumoSerializer(many=True, read_only=True)

    tipo_id = serializers.PrimaryKeyRelatedField(
        source='tipo',
        queryset=TipoEvento.objects.all(),
        write_only=True,
    )
    espaco_id = serializers.PrimaryKeyRelatedField(
        source='espaco',
        queryset=Espaco.objects.filter(ativo=True),
        required=False,
        allow_null=True,
        write_only=True,
    )
    convidado_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Cidadao.objects.all(),
        source='convidados',
        required=False,
        write_only=True,
    )

    class Meta:
        model = Evento
        fields = (
            'id',
            'titulo',
            'descricao',
            'data',
            'hora_inicio',
            'hora_fim',
            'tipo',
            'tipo_id',
            'espaco',
            'espaco_id',
            'convidados',
            'convidado_ids',
            'is_synced_google',
            'is_synced_outlook',
            'status',
            'criado_por',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'criado_por', 'created_at', 'updated_at')

    def validate(self, attrs):
        instance = self.instance

        hora_inicio = attrs.get('hora_inicio', getattr(instance, 'hora_inicio', None))
        hora_fim = attrs.get('hora_fim', getattr(instance, 'hora_fim', None))
        if hora_inicio and hora_fim and hora_inicio >= hora_fim:
            raise serializers.ValidationError(
                {'hora_fim': 'A hora de término deve ser posterior à hora de início.'},
            )

        espaco = attrs.get('espaco', getattr(instance, 'espaco', None))
        if espaco is None:
            return attrs

        data = attrs.get('data', getattr(instance, 'data', None))
        status = attrs.get('status', getattr(instance, 'status', Evento.Status.AGENDADO))

        if status != Evento.Status.AGENDADO:
            return attrs

        qs = Evento.objects.filter(
            espaco=espaco,
            data=data,
            status=Evento.Status.AGENDADO,
        )
        if instance is not None:
            qs = qs.exclude(pk=instance.pk)

        for outro in qs:
            if hora_inicio < outro.hora_fim and hora_fim > outro.hora_inicio:
                raise serializers.ValidationError(
                    {
                        'espaco': (
                            f'Conflito de horário com «{outro.titulo}» '
                            f'({outro.hora_inicio.strftime("%H:%M")}–'
                            f'{outro.hora_fim.strftime("%H:%M")}).'
                        ),
                    },
                )

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['criado_por'] = request.user if request else None
        convidados = validated_data.pop('convidados', [])
        evento = super().create(validated_data)
        if convidados:
            evento.convidados.set(convidados)
        return evento

    def update(self, instance, validated_data):
        convidados = validated_data.pop('convidados', None)
        evento = super().update(instance, validated_data)
        if convidados is not None:
            evento.convidados.set(convidados)
        return evento
