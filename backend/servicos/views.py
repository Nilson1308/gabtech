from config.viewsets import GabineteModelViewSet, GabineteReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from usuarios.permissions import ActionRBACPermission

from .matchmaking import sugerir_candidatos_para_vaga, sugerir_publico_por_tags
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
from .serializers import (
    AgendamentoAssessoriaSerializer,
    CandidaturaTalentoSerializer,
    CidadaoSugestaoSerializer,
    EntregaBeneficioSerializer,
    EixoServicoSerializer,
    InscricaoCursoSerializer,
    ItemBeneficioSerializer,
    TurmaCursoSerializer,
    VagaEmpregoSerializer,
)


class ServicosRBACMixin:
    """RBAC por seção do módulo Serviços (ver rbac_manage_codename em cada ViewSet)."""

    permission_classes = (IsAuthenticated, ActionRBACPermission)
    pagination_class = None
    rbac_manage_codename: str | None = None

    _READ_ACTIONS = frozenset(
        {
            'list',
            'retrieve',
            'sugerir_candidatos',
            'sugerir_publico',
        },
    )

    def get_rbac_codename(self):
        codename = self.rbac_action_map.get(self.action)
        if not codename:
            return codename
        manage = self.rbac_manage_codename
        if manage and self.action in self._READ_ACTIONS:
            user = self.request.user
            if user and user.is_authenticated and manage in user.get_permissao_codenames():
                return manage
        return codename


class EixoServicoViewSet(ServicosRBACMixin, GabineteReadOnlyModelViewSet):
    serializer_class = EixoServicoSerializer

    rbac_action_map = {
        'list': 'ler_servicos',
        'retrieve': 'ler_servicos',
    }

    def get_queryset(self):
        return EixoServico.objects.filter(ativo=True).order_by('nome')


class VagaEmpregoViewSet(ServicosRBACMixin, GabineteModelViewSet):
    serializer_class = VagaEmpregoSerializer
    rbac_manage_codename = 'gerenciar_talentos'

    rbac_action_map = {
        'list': 'ler_servicos',
        'retrieve': 'ler_servicos',
        'sugerir_candidatos': 'ler_servicos',
        'create': 'gerenciar_talentos',
        'update': 'gerenciar_talentos',
        'partial_update': 'gerenciar_talentos',
        'destroy': 'gerenciar_talentos',
    }

    def get_queryset(self):
        qs = VagaEmprego.objects.select_related('eixo').prefetch_related('tags_alvo').all()
        eixo_id = self.request.query_params.get('eixo')
        if eixo_id:
            qs = qs.filter(eixo_id=eixo_id)
        status = (self.request.query_params.get('status') or '').strip()
        if status:
            qs = qs.filter(status=status)
        return qs

    @action(detail=True, methods=['get'], url_path='sugerir_candidatos')
    def sugerir_candidatos(self, request, pk=None):
        vaga = self.get_object()
        limite = min(int(request.query_params.get('limit', 50)), 100)
        matches = sugerir_candidatos_para_vaga(vaga, limit=limite)
        data = [
            CidadaoSugestaoSerializer.from_match(m, context={'request': request}).data
            for m in matches
        ]
        return Response(data)


class CandidaturaTalentoViewSet(ServicosRBACMixin, GabineteModelViewSet):
    serializer_class = CandidaturaTalentoSerializer
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')
    rbac_manage_codename = 'gerenciar_talentos'

    rbac_action_map = {
        'list': 'ler_servicos',
        'retrieve': 'ler_servicos',
        'create': 'gerenciar_talentos',
        'partial_update': 'gerenciar_talentos',
        'destroy': 'gerenciar_talentos',
    }

    def get_queryset(self):
        qs = CandidaturaTalento.objects.select_related(
            'vaga',
            'vaga__eixo',
            'candidato',
            'candidato__endereco',
        ).prefetch_related('vaga__tags_alvo').all()
        vaga_id = self.request.query_params.get('vaga')
        if vaga_id:
            qs = qs.filter(vaga_id=vaga_id)
        return qs


class ItemBeneficioViewSet(ServicosRBACMixin, GabineteModelViewSet):
    serializer_class = ItemBeneficioSerializer
    rbac_manage_codename = 'gerenciar_assistencia'

    rbac_action_map = {
        'list': 'ler_servicos',
        'retrieve': 'ler_servicos',
        'sugerir_publico': 'ler_servicos',
        'create': 'gerenciar_assistencia',
        'update': 'gerenciar_assistencia',
        'partial_update': 'gerenciar_assistencia',
        'destroy': 'gerenciar_assistencia',
    }

    def get_queryset(self):
        return ItemBeneficio.objects.prefetch_related('tags_alvo').order_by('nome')

    @action(detail=True, methods=['get'], url_path='sugerir_publico')
    def sugerir_publico(self, request, pk=None):
        item = self.get_object()
        limite = min(int(request.query_params.get('limit', 50)), 100)
        matches = sugerir_publico_por_tags(item.tags_alvo, limit=limite, exigir_curriculo=False)
        data = [
            CidadaoSugestaoSerializer.from_match(m, context={'request': request}).data
            for m in matches
        ]
        return Response(data)


class EntregaBeneficioViewSet(ServicosRBACMixin, GabineteModelViewSet):
    serializer_class = EntregaBeneficioSerializer
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')
    rbac_manage_codename = 'gerenciar_assistencia'

    rbac_action_map = {
        'list': 'ler_servicos',
        'retrieve': 'ler_servicos',
        'create': 'gerenciar_assistencia',
        'partial_update': 'gerenciar_assistencia',
        'destroy': 'gerenciar_assistencia',
    }

    def get_queryset(self):
        qs = EntregaBeneficio.objects.select_related('cidadao', 'item', 'entregue_por').all()
        cidadao_id = self.request.query_params.get('cidadao')
        if cidadao_id:
            qs = qs.filter(cidadao_id=cidadao_id)
        item_id = self.request.query_params.get('item')
        if item_id:
            qs = qs.filter(item_id=item_id)
        return qs


class AgendamentoAssessoriaViewSet(ServicosRBACMixin, GabineteModelViewSet):
    serializer_class = AgendamentoAssessoriaSerializer
    rbac_manage_codename = 'gerenciar_assistencia'

    rbac_action_map = {
        'list': 'ler_servicos',
        'retrieve': 'ler_servicos',
        'create': 'gerenciar_assistencia',
        'update': 'gerenciar_assistencia',
        'partial_update': 'gerenciar_assistencia',
        'destroy': 'gerenciar_assistencia',
    }

    def get_queryset(self):
        qs = AgendamentoAssessoria.objects.select_related(
            'cidadao',
            'especialista_responsavel',
        ).all()
        cidadao_id = self.request.query_params.get('cidadao')
        if cidadao_id:
            qs = qs.filter(cidadao_id=cidadao_id)
        return qs


class TurmaCursoViewSet(ServicosRBACMixin, GabineteModelViewSet):
    serializer_class = TurmaCursoSerializer
    rbac_manage_codename = 'gerenciar_cursos'

    rbac_action_map = {
        'list': 'ler_servicos',
        'retrieve': 'ler_servicos',
        'sugerir_publico': 'ler_servicos',
        'create': 'gerenciar_cursos',
        'update': 'gerenciar_cursos',
        'partial_update': 'gerenciar_cursos',
        'destroy': 'gerenciar_cursos',
    }

    def get_queryset(self):
        return TurmaCurso.objects.prefetch_related('tags_alvo').all()

    @action(detail=True, methods=['get'], url_path='sugerir_publico')
    def sugerir_publico(self, request, pk=None):
        turma = self.get_object()
        limite = min(int(request.query_params.get('limit', 50)), 100)
        matches = sugerir_publico_por_tags(turma.tags_alvo, limit=limite, exigir_curriculo=False)
        data = [
            CidadaoSugestaoSerializer.from_match(m, context={'request': request}).data
            for m in matches
        ]
        return Response(data)


class InscricaoCursoViewSet(ServicosRBACMixin, GabineteModelViewSet):
    serializer_class = InscricaoCursoSerializer
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')
    rbac_manage_codename = 'gerenciar_cursos'

    rbac_action_map = {
        'list': 'ler_servicos',
        'retrieve': 'ler_servicos',
        'create': 'gerenciar_cursos',
        'partial_update': 'gerenciar_cursos',
        'destroy': 'gerenciar_cursos',
    }

    def get_queryset(self):
        qs = InscricaoCurso.objects.select_related('turma', 'cidadao').all()
        turma_id = self.request.query_params.get('turma')
        if turma_id:
            qs = qs.filter(turma_id=turma_id)
        return qs
