from django.db import transaction
from rest_framework import serializers

from auditoria.mixins import RastreabilidadeModelSerializer

from agenda.models import Evento, TipoEvento
from crm.models import Cidadao, PerfilProfissional

from .credenciamento_config import normalize_credenciamento_config
from .models import (
    ComunicacaoDisparo,
    ConvidadoEvento,
    Credenciado,
    EventoCerimonial,
    ItemChecklist,
    ItemChecklistPadrao,
)


class CredenciamentoConfigSerializer(serializers.Serializer):
    mostrar_email = serializers.BooleanField(required=False, default=True)
    mostrar_data_nascimento = serializers.BooleanField(required=False, default=True)
    mostrar_orgao_instituicao = serializers.BooleanField(required=False, default=True)
    url_politica_privacidade = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        default='',
    )

    def validate_url_politica_privacidade(self, value):
        url = (value or '').strip()
        if url and not url.startswith(('http://', 'https://')):
            raise serializers.ValidationError('Informe uma URL completa (https://...).')
        return url


class CidadaoConvidadoSerializer(RastreabilidadeModelSerializer):
    class Meta:
        model = Cidadao
        fields = ('id', 'nome', 'avatar', 'email', 'telefone')
        rastreabilidade_habilitada = False


class PerfilAtivoSerializer(RastreabilidadeModelSerializer):
    class Meta:
        model = PerfilProfissional
        fields = ('id', 'cargo', 'instituicao')
        rastreabilidade_habilitada = False


class ItemChecklistSerializer(RastreabilidadeModelSerializer):
    evento_id = serializers.PrimaryKeyRelatedField(
        queryset=EventoCerimonial.objects.all(),
        source='evento',
        write_only=True,
    )

    class Meta:
        model = ItemChecklist
        fields = (
            'id',
            'evento_id',
            'categoria',
            'descricao',
            'status',
            'responsavel',
            'prazo',
            'observacoes',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class ItemChecklistPadraoSerializer(RastreabilidadeModelSerializer):
    class Meta:
        model = ItemChecklistPadrao
        fields = ('id', 'categoria', 'descricao', 'created_at')
        read_only_fields = fields


class ConvidadoEventoSerializer(RastreabilidadeModelSerializer):
    cidadao = CidadaoConvidadoSerializer(read_only=True)
    perfil_ativo = PerfilAtivoSerializer(read_only=True)

    cidadao_id = serializers.PrimaryKeyRelatedField(
        queryset=Cidadao.objects.all(),
        source='cidadao',
        write_only=True,
    )
    perfil_ativo_id = serializers.PrimaryKeyRelatedField(
        queryset=PerfilProfissional.objects.all(),
        source='perfil_ativo',
        required=False,
        allow_null=True,
        write_only=True,
    )
    evento_id = serializers.PrimaryKeyRelatedField(
        queryset=EventoCerimonial.objects.all(),
        source='evento',
        write_only=True,
    )

    class Meta:
        model = ConvidadoEvento
        validators = []
        fields = (
            'id',
            'evento_id',
            'cidadao',
            'cidadao_id',
            'perfil_ativo',
            'perfil_ativo_id',
            'status_confirmacao',
            'ordem_precedencia',
            'is_vip',
            'observacoes',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'cidadao', 'perfil_ativo', 'created_at', 'updated_at')

    def validate(self, attrs):
        evento = attrs.get('evento') or getattr(self.instance, 'evento', None)
        cidadao = attrs.get('cidadao') or getattr(self.instance, 'cidadao', None)
        perfil = attrs.get('perfil_ativo')

        if perfil and cidadao and perfil.cidadao_id != cidadao.id:
            raise serializers.ValidationError(
                {'perfil_ativo_id': 'O perfil não pertence a este cidadão.'},
            )

        if evento and cidadao:
            qs = ConvidadoEvento.objects.filter(evento=evento, cidadao=cidadao)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {'cidadao_id': 'Este cidadão já está na lista de convidados.'},
                )

        return attrs


class CredenciadoSerializer(RastreabilidadeModelSerializer):
    evento_id = serializers.PrimaryKeyRelatedField(
        queryset=EventoCerimonial.objects.all(),
        source='evento',
        write_only=True,
        required=False,
    )
    cpf = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta:
        model = Credenciado
        fields = (
            'id',
            'evento_id',
            'nome',
            'telefone',
            'email',
            'data_nascimento',
            'orgao_instituicao',
            'cpf',
            'aceitou_lgpd',
            'data_registro',
            'status_presenca',
        )
        read_only_fields = ('id', 'data_registro')

    def validate(self, attrs):
        telefone = ''.join(filter(str.isdigit, attrs.get('telefone', '') or ''))
        if len(telefone) < 10:
            raise serializers.ValidationError({'telefone': 'Informe um telefone ou WhatsApp válido.'})
        attrs['telefone'] = telefone

        cpf_raw = attrs.get('cpf') or ''
        if cpf_raw:
            cpf = ''.join(filter(str.isdigit, cpf_raw))
            if len(cpf) != 11:
                raise serializers.ValidationError({'cpf': 'CPF inválido.'})
            attrs['cpf'] = cpf
        else:
            attrs['cpf'] = ''

        email = (attrs.get('email') or '').strip()
        attrs['email'] = email

        orgao = (attrs.get('orgao_instituicao') or '').strip()
        attrs['orgao_instituicao'] = orgao

        return attrs

    def validate_aceitou_lgpd(self, value):
        if not value:
            raise serializers.ValidationError('É necessário aceitar o termo LGPD.')
        return value


class ComunicacaoDisparoSerializer(RastreabilidadeModelSerializer):
    evento_id = serializers.PrimaryKeyRelatedField(
        queryset=EventoCerimonial.objects.all(),
        source='evento',
        write_only=True,
        required=False,
    )

    class Meta:
        model = ComunicacaoDisparo
        fields = (
            'id',
            'evento_id',
            'canal',
            'mensagem',
            'publico_alvo',
            'quantidade_envios',
            'status',
            'data_hora',
        )
        read_only_fields = ('id', 'status', 'data_hora')


class EventoAgendaResumoSerializer(RastreabilidadeModelSerializer):
    tipo_nome = serializers.CharField(source='tipo.nome', read_only=True)
    local = serializers.SerializerMethodField()
    hora_inicio = serializers.TimeField(format='%H:%M', read_only=True)
    hora_fim = serializers.TimeField(format='%H:%M', read_only=True)

    class Meta:
        model = Evento
        rastreabilidade_habilitada = False
        fields = (
            'id',
            'titulo',
            'descricao',
            'data',
            'hora_inicio',
            'hora_fim',
            'local',
            'tipo_nome',
            'status',
        )

    def get_local(self, obj: Evento) -> str:
        if obj.espaco_id:
            return obj.espaco.nome
        return ''


class EventoCerimonialSerializer(RastreabilidadeModelSerializer):
    token_logistica = serializers.UUIDField(read_only=True)
    logistica_publica_ativa = serializers.BooleanField(read_only=True)
    observacao_logistica_externa = serializers.CharField(read_only=True)
    checklist = ItemChecklistSerializer(many=True, read_only=True)
    convidados = ConvidadoEventoSerializer(many=True, read_only=True)
    credenciados = CredenciadoSerializer(many=True, read_only=True)
    comunicacoes = ComunicacaoDisparoSerializer(many=True, read_only=True)
    agenda = EventoAgendaResumoSerializer(source='evento_agenda', read_only=True)

    titulo = serializers.CharField(write_only=True, required=False)
    descricao = serializers.CharField(write_only=True, required=False, allow_blank=True)
    data = serializers.DateField(write_only=True, required=False)
    hora_inicio = serializers.TimeField(write_only=True, required=False, format='%H:%M')
    hora_fim = serializers.TimeField(write_only=True, required=False, format='%H:%M')
    tipo_id = serializers.PrimaryKeyRelatedField(
        queryset=TipoEvento.objects.all(),
        write_only=True,
        required=False,
    )
    local = serializers.CharField(write_only=True, required=False, allow_blank=True)

    total_convidados = serializers.SerializerMethodField()
    credenciamento_config = serializers.JSONField(required=False)

    class Meta:
        model = EventoCerimonial
        fields = (
            'id',
            'status_logistico',
            'token_logistica',
            'logistica_publica_ativa',
            'observacao_logistica_externa',
            'credenciamento_config',
            'created_at',
            'updated_at',
            'agenda',
            'checklist',
            'convidados',
            'credenciados',
            'comunicacoes',
            'total_convidados',
            'titulo',
            'descricao',
            'data',
            'hora_inicio',
            'hora_fim',
            'tipo_id',
            'local',
        )
        read_only_fields = (
            'id',
            'created_at',
            'updated_at',
            'token_logistica',
            'logistica_publica_ativa',
            'observacao_logistica_externa',
            'agenda',
            'checklist',
            'convidados',
            'credenciados',
            'comunicacoes',
        )

    def get_total_convidados(self, obj: EventoCerimonial) -> int:
        return obj.convidados.count()

    def validate_credenciamento_config(self, value):
        if value is None:
            return normalize_credenciamento_config(None)
        instance = getattr(self, 'instance', None)
        current = normalize_credenciamento_config(
            instance.credenciamento_config if instance else None,
        )
        merged = {**current, **value}
        nested = CredenciamentoConfigSerializer(data=merged)
        nested.is_valid(raise_exception=True)
        return normalize_credenciamento_config({**merged, **nested.validated_data})

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['credenciamento_config'] = normalize_credenciamento_config(
            instance.credenciamento_config,
        )
        return data

    @transaction.atomic
    def create(self, validated_data):
        titulo = validated_data.pop('titulo')
        descricao = validated_data.pop('descricao', '')
        data = validated_data.pop('data')
        hora_inicio = validated_data.pop('hora_inicio')
        hora_fim = validated_data.pop('hora_fim')
        tipo = validated_data.pop('tipo_id')
        local = validated_data.pop('local', '')
        status_logistico = validated_data.get('status_logistico', EventoCerimonial.StatusLogistico.PLANEJAMENTO)

        request = self.context.get('request')
        criado_por = request.user if request and request.user.is_authenticated else None

        evento_agenda = Evento.objects.create(
            titulo=titulo,
            descricao=descricao,
            data=data,
            hora_inicio=hora_inicio,
            hora_fim=hora_fim,
            tipo=tipo,
            criado_por=criado_por,
        )
        if local.strip():
            from agenda.models import Espaco
            espaco, _ = Espaco.objects.get_or_create(
                nome=local.strip()[:120],
                defaults={'descricao': 'Local informado no cerimonial'},
            )
            evento_agenda.espaco = espaco
            evento_agenda.save(update_fields=['espaco'])

        cerimonial = EventoCerimonial.objects.create(
            evento_agenda=evento_agenda,
            status_logistico=status_logistico,
        )
        return cerimonial

    @transaction.atomic
    def update(self, instance, validated_data):
        agenda_fields = {}
        for key in ('titulo', 'descricao', 'data', 'hora_inicio', 'hora_fim'):
            if key in validated_data:
                agenda_fields[key] = validated_data.pop(key)
        if 'tipo_id' in validated_data:
            agenda_fields['tipo'] = validated_data.pop('tipo_id')
        if 'local' in validated_data:
            local = validated_data.pop('local', '').strip()
            if local:
                from agenda.models import Espaco
                espaco, _ = Espaco.objects.get_or_create(
                    nome=local[:120],
                    defaults={'descricao': 'Local informado no cerimonial'},
                )
                agenda_fields['espaco'] = espaco

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if agenda_fields:
            evento = instance.evento_agenda
            for attr, value in agenda_fields.items():
                setattr(evento, attr, value)
            evento.save()

        return instance


class EventoCerimonialListSerializer(RastreabilidadeModelSerializer):
    agenda = EventoAgendaResumoSerializer(source='evento_agenda', read_only=True)
    total_convidados = serializers.SerializerMethodField()

    class Meta:
        model = EventoCerimonial
        fields = (
            'id',
            'status_logistico',
            'created_at',
            'agenda',
            'total_convidados',
        )

    def get_total_convidados(self, obj: EventoCerimonial) -> int:
        return obj.convidados.count()


class EventoPublicoSerializer(RastreabilidadeModelSerializer):
    titulo = serializers.CharField(source='evento_agenda.titulo', read_only=True)
    data = serializers.DateField(source='evento_agenda.data', read_only=True)
    hora_inicio = serializers.TimeField(source='evento_agenda.hora_inicio', format='%H:%M', read_only=True)
    hora_fim = serializers.TimeField(source='evento_agenda.hora_fim', format='%H:%M', read_only=True)
    local = serializers.SerializerMethodField()
    credenciamento_config = serializers.SerializerMethodField()

    class Meta:
        model = EventoCerimonial
        rastreabilidade_habilitada = False
        fields = (
            'id',
            'titulo',
            'data',
            'hora_inicio',
            'hora_fim',
            'local',
            'status_logistico',
            'credenciamento_config',
        )

    def get_local(self, obj: EventoCerimonial) -> str:
        espaco = obj.evento_agenda.espaco
        return espaco.nome if espaco else ''

    def get_credenciamento_config(self, obj: EventoCerimonial) -> dict:
        return normalize_credenciamento_config(obj.credenciamento_config)


class ItemChecklistPublicSerializer(RastreabilidadeModelSerializer):
    """Campos editáveis por colaboradores externos (token)."""

    class Meta:
        model = ItemChecklist
        rastreabilidade_habilitada = False
        fields = (
            'id',
            'categoria',
            'descricao',
            'status',
            'responsavel',
            'prazo',
            'observacoes',
        )
        read_only_fields = ('id', 'categoria', 'descricao', 'status')


class LogisticaPublicaItemPayloadSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    responsavel = serializers.CharField(required=False, allow_blank=True, default='')
    prazo = serializers.DateField(required=False, allow_null=True)
    observacoes = serializers.CharField(required=False, allow_blank=True, default='')
    status = serializers.ChoiceField(
        choices=ItemChecklist.Status.choices,
        required=False,
    )
    descartar = serializers.BooleanField(required=False, default=False)


class LogisticaPublicaEnviarSerializer(serializers.Serializer):
    itens = LogisticaPublicaItemPayloadSerializer(many=True, allow_empty=False)
    observacao_envio = serializers.CharField(required=False, allow_blank=True, default='')


class LogisticaPublicaEventoSerializer(RastreabilidadeModelSerializer):
    titulo = serializers.CharField(source='evento_agenda.titulo', read_only=True)
    data = serializers.DateField(source='evento_agenda.data', read_only=True)
    local = serializers.SerializerMethodField()
    checklist = ItemChecklistPublicSerializer(many=True, read_only=True)

    class Meta:
        model = EventoCerimonial
        rastreabilidade_habilitada = False
        fields = ('titulo', 'data', 'local', 'status_logistico', 'checklist')

    def get_local(self, obj: EventoCerimonial) -> str:
        espaco = obj.evento_agenda.espaco
        return espaco.nome if espaco else ''


class ReordenarConvidadosSerializer(serializers.Serializer):
    ordens = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False,
    )

    def validate_ordens(self, value):
        for item in value:
            if 'id' not in item or 'ordem_precedencia' not in item:
                raise serializers.ValidationError(
                    'Cada item deve conter id e ordem_precedencia.',
                )
        return value
