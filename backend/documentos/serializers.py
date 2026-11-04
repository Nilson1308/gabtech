from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from rest_framework import serializers

from auditoria.mixins import RastreabilidadeModelSerializer

from atendimentos.serializers import UsuarioResumoSerializer

from .models import (
    Documento,
    EtiquetaDocumento,
    PastaDocumento,
    TemplateDocumento,
    TipoDocumento,
    VersaoDocumento,
)

User = get_user_model()


class TipoDocumentoSerializer(RastreabilidadeModelSerializer):
    is_system = serializers.BooleanField(source='is_sistema', read_only=True)

    class Meta:
        model = TipoDocumento
        fields = (
            'id',
            'nome',
            'slug',
            'descricao',
            'icone',
            'cor',
            'is_system',
        )
        read_only_fields = ('id', 'is_system')


class TipoDocumentoWriteSerializer(RastreabilidadeModelSerializer):
    slug = serializers.SlugField(required=False, allow_blank=True)

    class Meta:
        model = TipoDocumento
        fields = ('id', 'nome', 'slug', 'descricao', 'icone', 'cor')
        read_only_fields = ('id',)

    def validate(self, attrs):
        instance = self.instance
        if instance and instance.is_sistema:
            if 'slug' in attrs and attrs['slug'] != instance.slug:
                raise serializers.ValidationError({'slug': 'Slug de tipo do sistema não pode ser alterado.'})
        return attrs

    def create(self, validated_data):
        validated_data['is_sistema'] = False
        if not validated_data.get('slug'):
            validated_data['slug'] = slugify(validated_data['nome']).replace('-', '_') or 'tipo'
        return super().create(validated_data)


class PastaDocumentoSerializer(RastreabilidadeModelSerializer):
    parent_id = serializers.PrimaryKeyRelatedField(
        source='parent',
        queryset=PastaDocumento.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    parentId = serializers.SerializerMethodField()

    class Meta:
        model = PastaDocumento
        fields = (
            'id',
            'nome',
            'icone',
            'cor',
            'parent',
            'parent_id',
            'parentId',
            'created_at',
        )
        read_only_fields = ('id', 'parent', 'created_at')

    def get_parentId(self, obj: PastaDocumento):
        return str(obj.parent_id) if obj.parent_id else None


class TemplateDocumentoSerializer(RastreabilidadeModelSerializer):
    tipo = serializers.SlugRelatedField(
        source='tipo_documento',
        slug_field='slug',
        queryset=TipoDocumento.objects.all(),
        write_only=True,
    )
    tipo_documento = TipoDocumentoSerializer(read_only=True)
    isDefault = serializers.BooleanField(source='is_default')
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)

    class Meta:
        model = TemplateDocumento
        fields = (
            'id',
            'nome',
            'tipo',
            'tipo_documento',
            'descricao',
            'conteudo',
            'isDefault',
            'createdAt',
            'updatedAt',
        )
        read_only_fields = ('id', 'tipo_documento', 'createdAt', 'updatedAt')

    def _sync_default(self, tipo: TipoDocumento, template: TemplateDocumento, is_default: bool):
        if is_default:
            TemplateDocumento.objects.filter(tipo_documento=tipo).exclude(pk=template.pk).update(
                is_default=False,
            )

    def create(self, validated_data):
        is_default = validated_data.get('is_default', False)
        template = super().create(validated_data)
        if is_default:
            self._sync_default(template.tipo_documento, template, True)
        return template

    def update(self, instance, validated_data):
        is_default = validated_data.get('is_default', instance.is_default)
        template = super().update(instance, validated_data)
        if is_default:
            self._sync_default(template.tipo_documento, template, True)
        return template


class EtiquetaDocumentoSerializer(RastreabilidadeModelSerializer):
    class Meta:
        model = EtiquetaDocumento
        fields = ('id', 'nome', 'cor', 'created_at')
        read_only_fields = ('id', 'created_at')


class VersaoDocumentoSerializer(RastreabilidadeModelSerializer):
    documento_id = serializers.IntegerField(source='documento.id', read_only=True)
    numero_versao = serializers.IntegerField()
    autor = UsuarioResumoSerializer(read_only=True)

    class Meta:
        model = VersaoDocumento
        fields = (
            'id',
            'documento_id',
            'numero_versao',
            'autor',
            'conteudo',
            'mudancas',
            'created_at',
        )
        read_only_fields = fields
        rastreabilidade_habilitada = False


class DocumentoListSerializer(RastreabilidadeModelSerializer):
    """Listagem — sem conteúdo HTML nem versões (payload leve)."""

    tipo_documento = TipoDocumentoSerializer(read_only=True)
    pasta = PastaDocumentoSerializer(read_only=True)
    autor = UsuarioResumoSerializer(read_only=True)
    etiquetas = EtiquetaDocumentoSerializer(many=True, read_only=True)
    finalizado_at = serializers.DateTimeField(source='finalizado_em', read_only=True, allow_null=True)

    class Meta:
        model = Documento
        fields = (
            'id',
            'titulo',
            'tipo_documento',
            'pasta',
            'autor',
            'status',
            'versao_atual',
            'etiquetas',
            'created_at',
            'updated_at',
            'finalizado_at',
        )
        read_only_fields = fields


class DocumentoSerializer(RastreabilidadeModelSerializer):
    tipo_documento = TipoDocumentoSerializer(read_only=True)
    pasta = PastaDocumentoSerializer(read_only=True)
    autor = UsuarioResumoSerializer(read_only=True)
    assinantes = UsuarioResumoSerializer(many=True, read_only=True)
    etiquetas = EtiquetaDocumentoSerializer(many=True, read_only=True)
    versoes = VersaoDocumentoSerializer(many=True, read_only=True)

    tipo_documento_id = serializers.PrimaryKeyRelatedField(
        source='tipo_documento',
        queryset=TipoDocumento.objects.all(),
        write_only=True,
    )
    pasta_id = serializers.PrimaryKeyRelatedField(
        source='pasta',
        queryset=PastaDocumento.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    assinante_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        source='assinantes',
        required=False,
        write_only=True,
    )
    etiqueta_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=EtiquetaDocumento.objects.all(),
        source='etiquetas',
        required=False,
        write_only=True,
    )

    versao_atual = serializers.IntegerField(read_only=True)
    finalizado_at = serializers.DateTimeField(source='finalizado_em', read_only=True, allow_null=True)

    class Meta:
        model = Documento
        fields = (
            'id',
            'titulo',
            'tipo_documento',
            'tipo_documento_id',
            'pasta',
            'pasta_id',
            'conteudo',
            'autor',
            'status',
            'versao_atual',
            'assinantes',
            'assinante_ids',
            'etiquetas',
            'etiqueta_ids',
            'versoes',
            'created_at',
            'updated_at',
            'finalizado_at',
        )
        read_only_fields = (
            'id',
            'autor',
            'versao_atual',
            'versoes',
            'created_at',
            'updated_at',
            'finalizado_at',
        )

    def validate(self, attrs):
        instance = self.instance
        if instance and instance.status == Documento.Status.FINALIZADO:
            # Finalizado: permite reorganizar pasta; bloqueia alteração de conteúdo/metadados.
            bloqueados = {
                'conteudo',
                'titulo',
                'tipo_documento',
                'etiquetas',
                'status',
                'assinantes',
            }
            if bloqueados.intersection(attrs.keys()):
                raise serializers.ValidationError(
                    'Documento finalizado não pode ter conteúdo ou metadados alterados.',
                )
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        assinantes = validated_data.pop('assinantes', [])
        etiquetas = validated_data.pop('etiquetas', [])
        validated_data['autor'] = request.user if request else None
        documento = super().create(validated_data)
        if assinantes:
            documento.assinantes.set(assinantes)
        if etiquetas:
            documento.etiquetas.set(etiquetas)
        return documento

    def update(self, instance, validated_data):
        request = self.context.get('request')
        assinantes = validated_data.pop('assinantes', None)
        etiquetas = validated_data.pop('etiquetas', None)
        novo_conteudo = validated_data.get('conteudo')
        novo_status = validated_data.get('status')

        if novo_conteudo is not None and novo_conteudo != instance.conteudo:
            VersaoDocumento.objects.create(
                documento=instance,
                numero_versao=instance.versao_atual,
                autor=request.user if request else None,
                conteudo=instance.conteudo,
                mudancas='Alteração de conteúdo',
            )
            instance.versao_atual = instance.versao_atual + 1
            validated_data['versao_atual'] = instance.versao_atual

        if novo_status == Documento.Status.FINALIZADO and instance.status != Documento.Status.FINALIZADO:
            validated_data['finalizado_em'] = timezone.now()
            if request and request.user:
                instance.assinantes.add(request.user)

        documento = super().update(instance, validated_data)

        if assinantes is not None:
            documento.assinantes.set(assinantes)
        if etiquetas is not None:
            documento.etiquetas.set(etiquetas)

        return documento
