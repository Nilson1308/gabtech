from decimal import Decimal, ROUND_HALF_UP

from rest_framework import serializers

from auditoria.mixins import RastreabilidadeModelSerializer

from .documento_validators import validar_arquivo_cidadao
from .models import Cidadao, DocumentoAnexo, Endereco, PerfilProfissional, Tag


class TagResumoSerializer(RastreabilidadeModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'nome', 'cor')
        rastreabilidade_habilitada = False


class DocumentoAnexoSerializer(RastreabilidadeModelSerializer):
    arquivo = serializers.FileField(write_only=True)
    url_download = serializers.SerializerMethodField()
    etiquetas = TagResumoSerializer(many=True, read_only=True)
    etiqueta_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        source='etiquetas',
        required=False,
        allow_empty=True,
        write_only=True,
    )

    class Meta:
        model = DocumentoAnexo
        fields = (
            'id',
            'cidadao',
            'categoria',
            'nome_original',
            'content_type',
            'tamanho',
            'created_at',
            'arquivo',
            'url_download',
            'etiquetas',
            'etiqueta_ids',
        )
        read_only_fields = (
            'id',
            'nome_original',
            'content_type',
            'tamanho',
            'created_at',
            'url_download',
            'etiquetas',
        )

    def get_url_download(self, obj: DocumentoAnexo) -> str | None:
        request = self.context.get('request')
        if not request:
            return None
        path = f'/api/crm/documentos/{obj.pk}/download/'
        return request.build_absolute_uri(path)

    def validate_arquivo(self, arquivo):
        validar_arquivo_cidadao(arquivo)
        return arquivo

    def validate_categoria(self, value):
        valid = {c.value for c in DocumentoAnexo.Categoria}
        if value not in valid:
            raise serializers.ValidationError('Categoria de documento inválida.')
        return value

    def _validar_etiquetas_curriculo(self, categoria, etiquetas):
        if not etiquetas:
            return
        if categoria != DocumentoAnexo.Categoria.CURRICULO:
            raise serializers.ValidationError(
                {'etiqueta_ids': 'Etiquetas de contexto profissional só se aplicam a currículos.'},
            )
        for tag in etiquetas:
            if tag.tipo != Tag.Tipo.CONTEXTO_PROFISSIONAL:
                raise serializers.ValidationError(
                    {
                        'etiqueta_ids': (
                            f'A etiqueta «{tag.nome}» deve ser do tipo Contexto profissional.'
                        ),
                    },
                )

    def validate(self, attrs):
        categoria = attrs.get(
            'categoria',
            self.instance.categoria if self.instance else DocumentoAnexo.Categoria.OUTROS,
        )
        etiquetas = attrs.get('etiquetas')
        if etiquetas is not None:
            self._validar_etiquetas_curriculo(categoria, etiquetas)
        return attrs

    def update(self, instance, validated_data):
        validated_data.pop('arquivo', None)
        validated_data.pop('cidadao', None)
        etiquetas = validated_data.pop('etiquetas', None)
        instance = super().update(instance, validated_data)
        if etiquetas is not None:
            if instance.categoria == DocumentoAnexo.Categoria.CURRICULO:
                instance.etiquetas.set(etiquetas)
            else:
                instance.etiquetas.clear()
        return instance

    def create(self, validated_data):
        arquivo = validated_data.pop('arquivo')
        cidadao = validated_data['cidadao']
        etiquetas = validated_data.pop('etiquetas', [])
        request = self.context.get('request')
        categoria = validated_data.get('categoria', DocumentoAnexo.Categoria.OUTROS)
        doc = DocumentoAnexo(
            cidadao=cidadao,
            categoria=categoria,
            nome_original=arquivo.name,
            content_type=getattr(arquivo, 'content_type', '') or '',
            tamanho=arquivo.size,
            enviado_por=request.user if request and request.user.is_authenticated else None,
        )
        doc.arquivo = arquivo
        doc.save()
        if categoria == DocumentoAnexo.Categoria.CURRICULO:
            doc.etiquetas.set(etiquetas)
        return doc


class GeocodeEntradaSerializer(serializers.Serializer):
    logradouro = serializers.CharField(required=False, allow_blank=True, default='')
    numero = serializers.CharField(required=False, allow_blank=True, default='')
    bairro = serializers.CharField(required=False, allow_blank=True, default='')
    cidade = serializers.CharField(required=False, allow_blank=True, default='')
    estado = serializers.CharField(required=False, allow_blank=True, default='')
    cep = serializers.CharField(required=False, allow_blank=True, default='')


class TagSerializer(RastreabilidadeModelSerializer):
    modulos = serializers.ListField(
        child=serializers.ChoiceField(choices=['crm', 'atendimentos']),
        allow_empty=False,
    )

    class Meta:
        model = Tag
        fields = ('id', 'nome', 'cor', 'tipo', 'modulos')

    def validate_modulos(self, value):
        if not value:
            raise serializers.ValidationError('Selecione ao menos um módulo.')
        seen: set[str] = set()
        ordered: list[str] = []
        for item in value:
            if item not in seen:
                seen.add(item)
                ordered.append(item)
        return ordered


def _coordenada_decimal(value) -> Decimal | None:
    """Alinha ao DecimalField(decimal_places=6) — geocoders enviam mais casas."""
    if value is None or value == '':
        return None
    return Decimal(str(value)).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)


class EnderecoSerializer(RastreabilidadeModelSerializer):
    class Meta:
        model = Endereco
        rastreabilidade_habilitada = False
        fields = (
            'logradouro',
            'numero',
            'complemento',
            'bairro',
            'cidade',
            'estado',
            'cep',
            'latitude',
            'longitude',
        )

    def validate_latitude(self, value):
        return _coordenada_decimal(value)

    def validate_longitude(self, value):
        return _coordenada_decimal(value)


class PerfilProfissionalSerializer(RastreabilidadeModelSerializer):
    tag_id = serializers.PrimaryKeyRelatedField(
        source='tag',
        queryset=Tag.objects.all(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = PerfilProfissional
        fields = ('id', 'instituicao', 'cargo', 'tag_id')
        read_only_fields = ('id',)
        rastreabilidade_habilitada = False


class EnderecoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = ('bairro', 'cidade', 'estado')


class CidadaoListSerializer(RastreabilidadeModelSerializer):
    """Listagem paginada — sem rastreabilidade nem observações (performance)."""

    endereco = EnderecoListSerializer(read_only=True)
    perfis_profissionais = PerfilProfissionalSerializer(many=True, read_only=True)
    bairro = serializers.CharField(read_only=True)
    tag_ids = serializers.SerializerMethodField()

    class Meta:
        model = Cidadao
        rastreabilidade_habilitada = False
        fields = (
            'id',
            'nome',
            'nome_social',
            'cpf',
            'telefone',
            'email',
            'bairro',
            'endereco',
            'tag_ids',
            'perfis_profissionais',
        )

    def get_tag_ids(self, instance: Cidadao) -> list[int]:
        return [tag.id for tag in instance.marcadores.all()]


class CidadaoBuscaSerializer(RastreabilidadeModelSerializer):
    """Payload enxuto para autocomplete (sem endereço completo nem avatar base64)."""

    bairro = serializers.CharField(read_only=True)

    class Meta:
        model = Cidadao
        rastreabilidade_habilitada = False
        fields = (
            'id',
            'nome',
            'nome_social',
            'cpf',
            'telefone',
            'email',
            'avatar',
            'bairro',
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        avatar = data.get('avatar') or ''
        if isinstance(avatar, str) and avatar.startswith('data:'):
            data['avatar'] = None
        return data


class CidadaoSerializer(RastreabilidadeModelSerializer):
    endereco = EnderecoSerializer(required=False, allow_null=True)
    perfis_profissionais = PerfilProfissionalSerializer(many=True, required=False)
    bairro = serializers.CharField(required=False, allow_blank=True, write_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        source='marcadores',
        required=False,
    )

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
            'observacoes',
            'bairro',
            'endereco',
            'tag_ids',
            'perfis_profissionais',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['bairro'] = instance.bairro
        data['tag_ids'] = [tag.id for tag in instance.marcadores.all()]
        return data

    def _sync_endereco(self, cidadao: Cidadao, endereco_data: dict | None, bairro_extra: str = ''):
        if endereco_data is None and not bairro_extra:
            return
        payload = endereco_data.copy() if endereco_data else {}
        if bairro_extra and not payload.get('bairro'):
            payload['bairro'] = bairro_extra
        if not payload:
            return
        Endereco.objects.update_or_create(cidadao=cidadao, defaults=payload)

    def _sync_perfis(self, cidadao: Cidadao, perfis_data: list[dict] | None):
        if perfis_data is None:
            return
        cidadao.perfis_profissionais.all().delete()
        for perfil in perfis_data:
            perfil.pop('id', None)
            tag = perfil.pop('tag', None)
            PerfilProfissional.objects.create(cidadao=cidadao, tag=tag, **perfil)

    def create(self, validated_data):
        endereco_data = validated_data.pop('endereco', None)
        perfis_data = validated_data.pop('perfis_profissionais', None)
        bairro = validated_data.pop('bairro', '')
        marcadores = validated_data.pop('marcadores', None)

        cidadao = Cidadao.objects.create(**validated_data)
        if marcadores is not None:
            cidadao.marcadores.set(marcadores)
        self._sync_endereco(cidadao, endereco_data, bairro)
        self._sync_perfis(cidadao, perfis_data)
        return cidadao

    def update(self, instance, validated_data):
        endereco_data = validated_data.pop('endereco', None)
        perfis_data = validated_data.pop('perfis_profissionais', None)
        bairro = validated_data.pop('bairro', None)
        marcadores = validated_data.pop('marcadores', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if marcadores is not None:
            instance.marcadores.set(marcadores)

        if endereco_data is not None or bairro:
            self._sync_endereco(
                instance,
                endereco_data,
                bairro or '',
            )
        if perfis_data is not None:
            self._sync_perfis(instance, perfis_data)

        return instance
