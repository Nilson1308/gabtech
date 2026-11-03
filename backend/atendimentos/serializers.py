from django.contrib.auth import get_user_model
from rest_framework import serializers

from auditoria.mixins import RastreabilidadeModelSerializer

from crm.models import Cidadao, PerfilProfissional, Tag
from crm.serializers import TagSerializer

from .anexo_serializers import AnexoSerializer
from .models import Atendimento, ConfiguracaoSla, Despacho, Macrotema
from .visibility import aplicar_escopo_atendimento_em_serializer
from .sla import HORAS_POR_DIA_SLA, horas_sla_para_prioridade

_SLA_PRIORIDADES = ('baixa', 'media', 'alta', 'urgente')


class ConfiguracaoSlaSerializer(RastreabilidadeModelSerializer):
    """Prazos persistidos em horas; aceita `dias_*` no PATCH (conversão automática)."""

    dias_baixa = serializers.FloatField(required=False, write_only=True, min_value=0.05, max_value=365)
    dias_media = serializers.FloatField(required=False, write_only=True, min_value=0.05, max_value=365)
    dias_alta = serializers.FloatField(required=False, write_only=True, min_value=0.05, max_value=365)
    dias_urgente = serializers.FloatField(required=False, write_only=True, min_value=0.05, max_value=365)

    class Meta:
        model = ConfiguracaoSla
        fields = (
            'horas_baixa',
            'horas_media',
            'horas_alta',
            'horas_urgente',
            'dias_baixa',
            'dias_media',
            'dias_alta',
            'dias_urgente',
            'updated_at',
        )
        read_only_fields = ('updated_at',)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for suffix in _SLA_PRIORIDADES:
            horas = getattr(instance, f'horas_{suffix}')
            data[f'dias_{suffix}'] = round(horas / HORAS_POR_DIA_SLA, 4)
        return data

    def validate(self, attrs):
        attrs = super().validate(attrs)
        for suffix in _SLA_PRIORIDADES:
            dias_key = f'dias_{suffix}'
            horas_key = f'horas_{suffix}'
            if dias_key in attrs:
                dias = float(attrs.pop(dias_key))
                horas = int(round(dias * HORAS_POR_DIA_SLA))
                attrs[horas_key] = max(1, min(8760, horas))
            elif horas_key in attrs:
                attrs[horas_key] = max(1, min(8760, int(attrs[horas_key])))
        return attrs

User = get_user_model()


class MacrotemaSerializer(RastreabilidadeModelSerializer):
    class Meta:
        model = Macrotema
        rastreabilidade_habilitada = False
        fields = ('id', 'nome', 'cor', 'icone')


class UsuarioResumoSerializer(RastreabilidadeModelSerializer):
    nome = serializers.CharField(read_only=True)
    cargo = serializers.CharField(read_only=True)
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'nome', 'email', 'avatar', 'cargo', 'permissions')
        rastreabilidade_habilitada = False

    def get_permissions(self, obj: User) -> list[str]:
        return obj.get_permissao_codenames()


class PerfilProfissionalResumoSerializer(RastreabilidadeModelSerializer):
    tag_id = serializers.PrimaryKeyRelatedField(
        source='tag',
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = PerfilProfissional
        fields = ('id', 'instituicao', 'cargo', 'tag_id')
        rastreabilidade_habilitada = False

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['tag_id'] = str(instance.tag_id) if instance.tag_id else ''
        return data


class CidadaoResumoSerializer(RastreabilidadeModelSerializer):
    bairro = serializers.CharField(read_only=True)
    perfis_profissionais = PerfilProfissionalResumoSerializer(many=True, read_only=True)

    class Meta:
        model = Cidadao
        fields = (
            'id',
            'nome',
            'nome_social',
            'cpf',
            'telefone',
            'email',
            'avatar',
            'bairro',
            'perfis_profissionais',
        )
        rastreabilidade_habilitada = False


class DespachoSerializer(RastreabilidadeModelSerializer):
    autor = UsuarioResumoSerializer(read_only=True)
    anexos = AnexoSerializer(many=True, read_only=True)
    atendimento_id = serializers.PrimaryKeyRelatedField(
        source='atendimento',
        queryset=Atendimento.objects.all(),
        write_only=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        aplicar_escopo_atendimento_em_serializer(self)

    class Meta:
        model = Despacho
        fields = (
            'id',
            'atendimento_id',
            'autor',
            'autor_id',
            'tipo',
            'conteudo',
            'status_anterior',
            'status_novo',
            'responsavel_anterior_id',
            'responsavel_novo_id',
            'anexos',
            'created_at',
        )
        read_only_fields = (
            'id',
            'autor',
            'autor_id',
            'status_anterior',
            'status_novo',
            'responsavel_anterior_id',
            'responsavel_novo_id',
            'created_at',
        )

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['autor'] = request.user if request else None
        return super().create(validated_data)


class AtendimentoSerializer(RastreabilidadeModelSerializer):
    cidadao = CidadaoResumoSerializer(read_only=True)
    macrotema = MacrotemaSerializer(read_only=True)
    responsavel = UsuarioResumoSerializer(read_only=True)
    despachos = DespachoSerializer(many=True, read_only=True)
    anexos = serializers.SerializerMethodField()
    sla_horas = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        source='tags',
        required=False,
        write_only=True,
    )

    cidadao_id = serializers.PrimaryKeyRelatedField(
        source='cidadao',
        queryset=Cidadao.objects.all(),
        write_only=True,
    )
    macrotema_id = serializers.PrimaryKeyRelatedField(
        source='macrotema',
        queryset=Macrotema.objects.all(),
        write_only=True,
    )
    responsavel_id = serializers.PrimaryKeyRelatedField(
        source='responsavel',
        queryset=User.objects.filter(is_active=True),
        required=False,
        write_only=True,
    )
    perfil_ativo_id = serializers.PrimaryKeyRelatedField(
        source='perfil_ativo',
        queryset=PerfilProfissional.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Atendimento
        fields = (
            'id',
            'protocolo',
            'cidadao',
            'cidadao_id',
            'perfil_ativo_id',
            'assunto',
            'descricao',
            'macrotema',
            'macrotema_id',
            'tags',
            'tag_ids',
            'status',
            'responsavel',
            'responsavel_id',
            'prioridade',
            'sla_vencimento',
            'sla_horas',
            'anexos',
            'despachos',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'protocolo',
            'cidadao',
            'macrotema',
            'responsavel',
            'despachos',
            'anexos',
            'tags',
            'sla_horas',
            'created_at',
            'updated_at',
        )
        extra_kwargs = {
            'cidadao_id': {'write_only': True},
            'macrotema_id': {'write_only': True},
            'responsavel_id': {'write_only': True},
        }

    def validate_tag_ids(self, tags):
        for tag in tags:
            modulos = tag.modulos or []
            if 'atendimentos' not in modulos:
                raise serializers.ValidationError(
                    f'A tag «{tag.nome}» não está disponível no módulo Atendimentos.',
                )
        return tags

    def validate(self, attrs):
        instance = self.instance
        if instance is None:
            return attrs

        status_atual = instance.status
        status_novo = attrs.get('status', status_atual)

        if (
            status_novo == Atendimento.Status.ABERTO
            and status_atual != Atendimento.Status.ABERTO
        ):
            raise serializers.ValidationError(
                {'status': 'Não é permitido retornar o atendimento para o status Aberto.'},
            )

        if status_atual != Atendimento.Status.ABERTO:
            campos_bloqueados = {
                'assunto',
                'descricao',
                'cidadao',
                'macrotema',
                'prioridade',
                'perfil_ativo',
                'tags',
            }
            if campos_bloqueados.intersection(attrs.keys()):
                raise serializers.ValidationError(
                    'Os dados do atendimento só podem ser editados enquanto o status for Aberto.',
                )

        if 'responsavel' in attrs and attrs['responsavel'] is None:
            raise serializers.ValidationError(
                {'responsavel_id': 'Informe um responsável válido.'},
            )

        return attrs

    def get_anexos(self, obj: Atendimento):
        qs = obj.anexos.filter(despacho__isnull=True)
        return AnexoSerializer(qs, many=True, context=self.context).data

    def get_sla_horas(self, obj: Atendimento) -> int:
        return horas_sla_para_prioridade(obj.prioridade)

    def create(self, validated_data):
        request = self.context.get('request')
        if not validated_data.get('responsavel'):
            validated_data['responsavel'] = request.user

        atendimento = super().create(validated_data)

        Despacho.objects.create(
            atendimento=atendimento,
            autor=request.user if request else None,
            tipo=Despacho.Tipo.NOTA_INTERNA,
            conteudo='Atendimento registrado no sistema.',
        )
        return atendimento

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = request.user if request else None

        status_novo = validated_data.get('status')
        status_anterior = instance.status
        responsavel_novo = validated_data.get('responsavel')
        responsavel_anterior = instance.responsavel
        prioridade_anterior = instance.prioridade

        instance = super().update(instance, validated_data)

        if (
            'prioridade' in validated_data
            and validated_data['prioridade'] != prioridade_anterior
            and instance.status != Atendimento.Status.CONCLUIDO
        ):
            instance.recalcular_sla()
            instance.save(update_fields=['sla_vencimento'])

        if status_novo and status_novo != status_anterior:
            Despacho.objects.create(
                atendimento=instance,
                autor=user,
                tipo=Despacho.Tipo.MUDANCA_STATUS,
                conteudo=f'Status alterado de "{status_anterior}" para "{status_novo}"',
                status_anterior=status_anterior,
                status_novo=status_novo,
            )
            if status_novo == Atendimento.Status.CONCLUIDO:
                instance.sla_vencimento = None
                instance.save(update_fields=['sla_vencimento'])

        if responsavel_novo and responsavel_novo.id != responsavel_anterior.id:
            Despacho.objects.create(
                atendimento=instance,
                autor=user,
                tipo=Despacho.Tipo.REATRIBUICAO,
                conteudo=(
                    f'Ticket transferido de "{responsavel_anterior.nome}" '
                    f'para "{responsavel_novo.nome}"'
                ),
                responsavel_anterior=responsavel_anterior,
                responsavel_novo=responsavel_novo,
            )

        return instance


class AtendimentoKanbanSerializer(RastreabilidadeModelSerializer):
    """Listagem leve para o quadro Kanban / timeline CRM (sem despachos/anexos)."""

    cidadao = CidadaoResumoSerializer(read_only=True)
    macrotema = MacrotemaSerializer(read_only=True)
    responsavel = UsuarioResumoSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    sla_horas = serializers.SerializerMethodField()

    class Meta:
        model = Atendimento
        rastreabilidade_habilitada = False
        fields = (
            'id',
            'protocolo',
            'cidadao',
            'assunto',
            'macrotema',
            'tags',
            'status',
            'responsavel',
            'prioridade',
            'sla_vencimento',
            'sla_horas',
            'created_at',
            'updated_at',
        )

    def get_sla_horas(self, obj: Atendimento) -> int:
        return horas_sla_para_prioridade(obj.prioridade)
