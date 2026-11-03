from datetime import timedelta

from rest_framework import serializers

from auditoria.mixins import RastreabilidadeModelSerializer

from crm.models import Cidadao, DocumentoAnexo, Tag
from crm.serializers import CidadaoBuscaSerializer, TagResumoSerializer

from .matchmaking import SugestaoMatch
from .models import (
    AgendamentoAssessoria,
    CandidaturaTalento,
    EntregaBeneficio,
    EixoServico,
    InscricaoCurso,
    ItemBeneficio,
    TurmaCurso,
    VagaEmprego,
)


from .tag_rules import validar_tags_contexto_profissional, validar_tags_segmentacao


def _curriculo_payload(cidadao: Cidadao, request, vaga: VagaEmprego | None = None) -> dict | None:
    qs = DocumentoAnexo.objects.filter(
        cidadao=cidadao,
        categoria=DocumentoAnexo.Categoria.CURRICULO,
    ).prefetch_related('etiquetas')
    if vaga is not None and vaga.pk:
        vaga_tag_ids = list(vaga.tags_alvo.values_list('id', flat=True))
        if vaga_tag_ids:
            qs = qs.filter(etiquetas__id__in=vaga_tag_ids).distinct()
    doc = qs.order_by('-created_at').first()
    if not doc:
        return None
    path = f'/api/crm/documentos/{doc.pk}/download/'
    url = request.build_absolute_uri(path) if request else path
    return {
        'id': doc.pk,
        'nome_original': doc.nome_original,
        'url_download': url,
        'created_at': doc.created_at.isoformat() if doc.created_at else None,
        'etiquetas': TagResumoSerializer(doc.etiquetas.all(), many=True).data,
    }


class CidadaoSugestaoSerializer(serializers.Serializer):
    score = serializers.IntegerField()
    tags_coincidentes = TagResumoSerializer(many=True)
    cidadao = CidadaoBuscaSerializer()

    @classmethod
    def from_match(cls, match: SugestaoMatch, context=None):
        return cls(
            {
                'score': match.score,
                'tags_coincidentes': match.tags,
                'cidadao': match.cidadao,
            },
            context=context,
        )


class EixoServicoSerializer(RastreabilidadeModelSerializer):
    class Meta:
        model = EixoServico
        fields = ('id', 'nome', 'icone', 'cor', 'ativo', 'created_at')
        read_only_fields = ('id', 'created_at')


class VagaEmpregoSerializer(RastreabilidadeModelSerializer):
    eixo_nome = serializers.CharField(source='eixo.nome', read_only=True)
    tags_alvo = TagResumoSerializer(many=True, read_only=True)
    tags_alvo_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        source='tags_alvo',
        required=False,
        allow_empty=True,
        write_only=True,
    )
    # Alias legado (frontend em transição)
    etiquetas = TagResumoSerializer(source='tags_alvo', many=True, read_only=True)
    etiqueta_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        source='tags_alvo',
        required=False,
        allow_empty=True,
        write_only=True,
    )

    class Meta:
        model = VagaEmprego
        fields = (
            'id',
            'eixo',
            'eixo_nome',
            'titulo',
            'empresa_parceira',
            'descricao',
            'requisitos',
            'status',
            'tags_alvo',
            'tags_alvo_ids',
            'etiquetas',
            'etiqueta_ids',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'eixo_nome', 'tags_alvo', 'etiquetas')

    def validate_tags_alvo_ids(self, tags):
        return validar_tags_contexto_profissional(tags)

    def create(self, validated_data):
        tags = validated_data.pop('tags_alvo', [])
        vaga = super().create(validated_data)
        if tags:
            vaga.tags_alvo.set(tags)
        return vaga

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags_alvo', None)
        instance = super().update(instance, validated_data)
        if tags is not None:
            instance.tags_alvo.set(tags)
        return instance


class CandidaturaTalentoSerializer(RastreabilidadeModelSerializer):
    candidato = CidadaoBuscaSerializer(read_only=True)
    candidato_id = serializers.PrimaryKeyRelatedField(
        source='candidato',
        queryset=Cidadao.objects.all(),
        write_only=True,
    )
    vaga_titulo = serializers.CharField(source='vaga.titulo', read_only=True)
    curriculo = serializers.SerializerMethodField()

    class Meta:
        model = CandidaturaTalento
        fields = (
            'id',
            'vaga',
            'vaga_titulo',
            'candidato',
            'candidato_id',
            'status_processo',
            'observacoes',
            'curriculo',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'candidato', 'vaga_titulo', 'curriculo')

    def get_curriculo(self, obj: CandidaturaTalento):
        request = self.context.get('request')
        return _curriculo_payload(obj.candidato, request, vaga=obj.vaga)

    def validate(self, attrs):
        vaga = attrs.get('vaga')
        candidato = attrs.get('candidato')
        if vaga and candidato:
            qs = CandidaturaTalento.objects.filter(vaga=vaga, candidato=candidato)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    'Este cidadão já está inscrito nesta vaga.',
                )
        return attrs


class ItemBeneficioSerializer(RastreabilidadeModelSerializer):
    tags_alvo = TagResumoSerializer(many=True, read_only=True)
    tags_alvo_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        source='tags_alvo',
        required=False,
        allow_empty=True,
        write_only=True,
    )

    class Meta:
        model = ItemBeneficio
        fields = (
            'id',
            'nome',
            'descricao',
            'exige_laudo',
            'tags_alvo',
            'tags_alvo_ids',
            'created_at',
        )
        read_only_fields = ('id', 'created_at', 'tags_alvo')

    def validate_tags_alvo_ids(self, tags):
        return validar_tags_segmentacao(tags)

    def create(self, validated_data):
        tags = validated_data.pop('tags_alvo', [])
        item = super().create(validated_data)
        if tags:
            item.tags_alvo.set(tags)
        return item

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags_alvo', None)
        instance = super().update(instance, validated_data)
        if tags is not None:
            instance.tags_alvo.set(tags)
        return instance


class EntregaBeneficioSerializer(RastreabilidadeModelSerializer):
    cidadao_nome = serializers.CharField(source='cidadao.nome', read_only=True)
    item_nome = serializers.CharField(source='item.nome', read_only=True)

    class Meta:
        model = EntregaBeneficio
        fields = (
            'id',
            'cidadao',
            'cidadao_nome',
            'item',
            'item_nome',
            'data_entrega',
            'quantidade',
            'entregue_por',
            'created_at',
        )
        read_only_fields = ('id', 'created_at', 'cidadao_nome', 'item_nome')

    def validate(self, attrs):
        cidadao = attrs.get('cidadao') or (self.instance and self.instance.cidadao)
        item = attrs.get('item') or (self.instance and self.instance.item)
        data_entrega = attrs.get('data_entrega') or (self.instance and self.instance.data_entrega)

        if cidadao and item and data_entrega:
            limite = data_entrega - timedelta(days=30)
            recente = EntregaBeneficio.objects.filter(
                cidadao=cidadao,
                item=item,
                data_entrega__gte=limite,
                data_entrega__lte=data_entrega,
            )
            if self.instance:
                recente = recente.exclude(pk=self.instance.pk)
            if recente.exists():
                raise serializers.ValidationError(
                    'Este cidadão já recebeu o mesmo benefício nos últimos 30 dias.',
                )

        if item and item.exige_laudo and cidadao:
            tem_laudo = DocumentoAnexo.objects.filter(
                cidadao=cidadao,
                categoria=DocumentoAnexo.Categoria.LAUDO_MEDICO,
            ).exists()
            if not tem_laudo:
                raise serializers.ValidationError(
                    'Este benefício exige laudo médico anexado ao cadastro do cidadão.',
                )
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated and not validated_data.get('entregue_por'):
            validated_data['entregue_por'] = request.user
        return super().create(validated_data)


class AgendamentoAssessoriaSerializer(RastreabilidadeModelSerializer):
    cidadao_nome = serializers.CharField(source='cidadao.nome', read_only=True)
    especialista_nome = serializers.SerializerMethodField()

    class Meta:
        model = AgendamentoAssessoria
        fields = (
            'id',
            'cidadao',
            'cidadao_nome',
            'tipo_nome',
            'tipo_descricao',
            'data_agendamento',
            'status',
            'especialista_responsavel',
            'especialista_nome',
            'created_at',
        )
        read_only_fields = ('id', 'created_at', 'cidadao_nome', 'especialista_nome')

    def get_especialista_nome(self, obj):
        u = obj.especialista_responsavel
        if not u:
            return ''
        return getattr(u, 'nome', None) or u.get_full_name() or u.email


class TurmaCursoSerializer(RastreabilidadeModelSerializer):
    tags_alvo = TagResumoSerializer(many=True, read_only=True)
    tags_alvo_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        source='tags_alvo',
        required=False,
        allow_empty=True,
        write_only=True,
    )
    vagas_ocupadas = serializers.SerializerMethodField()

    class Meta:
        model = TurmaCurso
        fields = (
            'id',
            'nome_curso',
            'vagas_totais',
            'vagas_ocupadas',
            'status',
            'tags_alvo',
            'tags_alvo_ids',
            'created_at',
        )
        read_only_fields = ('id', 'created_at', 'tags_alvo', 'vagas_ocupadas')

    def get_vagas_ocupadas(self, obj: TurmaCurso) -> int:
        return obj.vagas_ocupadas

    def validate_tags_alvo_ids(self, tags):
        return validar_tags_contexto_profissional(tags)

    def create(self, validated_data):
        tags = validated_data.pop('tags_alvo', [])
        turma = super().create(validated_data)
        if tags:
            turma.tags_alvo.set(tags)
        return turma

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags_alvo', None)
        instance = super().update(instance, validated_data)
        if tags is not None:
            instance.tags_alvo.set(tags)
        return instance


class InscricaoCursoSerializer(RastreabilidadeModelSerializer):
    cidadao_nome = serializers.CharField(source='cidadao.nome', read_only=True)
    turma_nome = serializers.CharField(source='turma.nome_curso', read_only=True)
    cidadao_id = serializers.PrimaryKeyRelatedField(
        source='cidadao',
        queryset=Cidadao.objects.all(),
        write_only=True,
    )

    class Meta:
        model = InscricaoCurso
        fields = (
            'id',
            'turma',
            'turma_nome',
            'cidadao',
            'cidadao_id',
            'cidadao_nome',
            'status',
            'created_at',
        )
        read_only_fields = ('id', 'created_at', 'cidadao', 'cidadao_nome', 'turma_nome')

    def validate(self, attrs):
        turma = attrs.get('turma') or (self.instance and self.instance.turma)
        cidadao = attrs.get('cidadao') or (self.instance and self.instance.cidadao)
        if turma and cidadao:
            qs = InscricaoCurso.objects.filter(turma=turma, cidadao=cidadao).exclude(
                status=InscricaoCurso.Status.CANCELADO,
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError('Cidadão já inscrito nesta turma.')
        return attrs

    def create(self, validated_data):
        turma = validated_data['turma']
        ocupadas = turma.inscricoes.filter(status=InscricaoCurso.Status.INSCRITO).count()
        if ocupadas >= turma.vagas_totais:
            validated_data['status'] = InscricaoCurso.Status.LISTA_ESPERA
        else:
            validated_data['status'] = InscricaoCurso.Status.INSCRITO
        return super().create(validated_data)
