from rest_framework import serializers

from auditoria.mixins import RastreabilidadeModelSerializer

from crm.documento_validators import validar_arquivo_cidadao

from .models import Anexo, Atendimento, Despacho
from .visibility import aplicar_escopo_atendimento_em_serializer


class AnexoSerializer(RastreabilidadeModelSerializer):
    arquivo = serializers.FileField(write_only=True)
    url_download = serializers.SerializerMethodField()
    atendimento = serializers.PrimaryKeyRelatedField(
        queryset=Atendimento.objects.all(),
        write_only=True,
    )
    despacho = serializers.PrimaryKeyRelatedField(
        queryset=Despacho.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    atendimento_id = serializers.IntegerField(read_only=True)
    despacho_id = serializers.IntegerField(read_only=True, allow_null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        aplicar_escopo_atendimento_em_serializer(self)

    class Meta:
        model = Anexo
        fields = (
            'id',
            'atendimento',
            'despacho',
            'atendimento_id',
            'despacho_id',
            'nome_original',
            'content_type',
            'tamanho',
            'created_at',
            'arquivo',
            'url_download',
        )
        read_only_fields = (
            'id',
            'nome_original',
            'content_type',
            'tamanho',
            'created_at',
            'url_download',
        )

    def get_url_download(self, obj: Anexo) -> str | None:
        request = self.context.get('request')
        if not request:
            return None
        return request.build_absolute_uri(f'/api/atendimentos/anexos/{obj.pk}/download/')

    def validate_arquivo(self, arquivo):
        validar_arquivo_cidadao(arquivo)
        return arquivo

    def validate(self, attrs):
        despacho = attrs.get('despacho')
        atendimento = attrs['atendimento']
        if despacho and despacho.atendimento_id != atendimento.id:
            raise serializers.ValidationError(
                {'despacho': 'O despacho não pertence a este atendimento.'},
            )
        return attrs

    def create(self, validated_data):
        arquivo = validated_data.pop('arquivo')
        request = self.context.get('request')
        anexo = Anexo(
            atendimento=validated_data['atendimento'],
            despacho=validated_data.get('despacho'),
            nome_original=arquivo.name,
            content_type=getattr(arquivo, 'content_type', '') or '',
            tamanho=arquivo.size,
            enviado_por=request.user if request and request.user.is_authenticated else None,
        )
        anexo.arquivo = arquivo
        anexo.save()
        return anexo
