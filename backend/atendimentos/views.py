from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import FileResponse
from config.viewsets import GabineteModelViewSet
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from usuarios.permissions import ActionRBACPermission

from .anexo_serializers import AnexoSerializer
from .export_csv import build_atendimentos_csv_response, filtrar_queryset_exportacao
from .models import Anexo, Atendimento, ConfiguracaoSla, Despacho, Macrotema
from .visibility import filtrar_atendimentos_visiveis
from .serializers import (
    AtendimentoKanbanSerializer,
    AtendimentoSerializer,
    ConfiguracaoSlaSerializer,
    DespachoSerializer,
    MacrotemaSerializer,
    UsuarioResumoSerializer,
)


def _parse_id_list(raw: str | None) -> list[int]:
    if not raw:
        return []
    ids: list[int] = []
    for part in raw.split(','):
        part = part.strip()
        if part.isdigit():
            ids.append(int(part))
    return ids


def _ids_from_param_list(params, key: str) -> list[int]:
    values = params.getlist(key) if hasattr(params, 'getlist') else []
    if not values and params.get(key):
        values = [params.get(key)]
    ids: list[int] = []
    for raw in values:
        if raw is None:
            continue
        ids.extend(_parse_id_list(str(raw)))
    return list(dict.fromkeys(ids))


def filtrar_atendimentos_por_query(
    queryset,
    params,
    *,
    aplicar_status: bool = True,
):
    if aplicar_status:
        status = (params.get('status') or '').strip()
        if status:
            queryset = queryset.filter(status=status)

    macro_ids = _ids_from_param_list(params, 'macrotema')
    if macro_ids:
        queryset = queryset.filter(macrotema_id__in=macro_ids)

    tag_ids = _ids_from_param_list(params, 'tags')
    if tag_ids:
        queryset = queryset.filter(tags__in=tag_ids).distinct()

    cidadao_raw = (params.get('cidadao_id') or params.get('cidadao') or '').strip()
    if cidadao_raw.isdigit():
        queryset = queryset.filter(cidadao_id=int(cidadao_raw))

    return queryset

User = get_user_model()
# Quem pode ser responsável: opera protocolos (editar_atend), não recepção só leitura/cadastro.
PERMISSAO_RESPONSAVEL_ATENDIMENTO = 'editar_atend'


class AtendimentoPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500


class ConfiguracaoSlaView(APIView):
    permission_classes = (IsAuthenticated, ActionRBACPermission)

    rbac_action_map = {
        'get': 'ler_atend',
        'patch': 'manage_sla_atend',
        'put': 'manage_sla_atend',
    }

    def get_rbac_codename(self):
        return self.rbac_action_map.get(self.request.method.lower())

    def get(self, request):
        config = ConfiguracaoSla.get()
        return Response(ConfiguracaoSlaSerializer(config).data)

    def patch(self, request):
        config = ConfiguracaoSla.get()
        serializer = ConfiguracaoSlaSerializer(config, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ResponsaveisAtendimentoView(APIView):
    """
    Usuários elegíveis como responsável / reatribuição (chefes e assessores).
    """

    permission_classes = (IsAuthenticated, ActionRBACPermission)

    rbac_action_map = {
        'get': 'ler_atend',
    }

    def get_rbac_codename(self):
        return self.rbac_action_map.get(self.request.method.lower())

    def get(self, request):
        qs = (
            User.objects.filter(is_active=True, status=User.Status.ATIVO)
            .filter(
                Q(is_superuser=True)
                | Q(perfil__is_admin=True)
                | Q(perfil__permissoes__codename=PERMISSAO_RESPONSAVEL_ATENDIMENTO)
            )
            .select_related('perfil')
            .distinct()
            .order_by('first_name', 'last_name', 'email')
        )
        return Response(UsuarioResumoSerializer(qs, many=True).data)


class MacrotemaViewSet(GabineteModelViewSet):
    queryset = Macrotema.objects.all()
    serializer_class = MacrotemaSerializer
    permission_classes = (IsAuthenticated, ActionRBACPermission)
    pagination_class = None

    rbac_action_map = {
        'list': 'ler_atend',
        'retrieve': 'ler_atend',
        'create': 'manage_macrotemas',
        'update': 'manage_macrotemas',
        'partial_update': 'manage_macrotemas',
        'destroy': 'manage_macrotemas',
    }

    def get_rbac_codename(self):
        return self.rbac_action_map.get(self.action)


class AtendimentoViewSet(GabineteModelViewSet):
    serializer_class = AtendimentoSerializer
    permission_classes = (IsAuthenticated, ActionRBACPermission)
    pagination_class = AtendimentoPagination
    filter_backends = (SearchFilter,)
    search_fields = ('protocolo', 'assunto', 'cidadao__nome', 'descricao')

    rbac_action_map = {
        'list': 'ler_atend',
        'retrieve': 'ler_atend',
        'create': 'criar_atend',
        'update': 'editar_atend',
        'partial_update': 'editar_atend',
        'destroy': 'excluir_atend',
        'exportar_csv': 'exportar_atend',
        'kanban_resumo': 'ler_atend',
    }

    def get_rbac_codename(self):
        if self.action in ('update', 'partial_update'):
            data = self.request.data
            if isinstance(data, dict):
                keys = set(data.keys())
                if keys <= {'status'}:
                    return 'mudar_status'
                if keys <= {'responsavel_id'}:
                    return 'reatribuir'
            return 'editar_atend'
        return self.rbac_action_map.get(self.action)

    def _listagem_leve(self) -> bool:
        if self.action != 'list':
            return False
        params = self.request.query_params
        if params.get('view') == 'kanban':
            return True
        cidadao = (params.get('cidadao_id') or params.get('cidadao') or '').strip()
        return cidadao.isdigit()

    def get_serializer_class(self):
        if self._listagem_leve():
            return AtendimentoKanbanSerializer
        return AtendimentoSerializer

    def get_queryset(self):
        if self._listagem_leve():
            qs = (
                Atendimento.objects.select_related(
                    'cidadao',
                    'macrotema',
                    'responsavel',
                    'responsavel__perfil',
                )
                .prefetch_related('tags')
                .all()
            )
        else:
            qs = (
                Atendimento.objects.select_related(
                    'cidadao',
                    'macrotema',
                    'responsavel',
                    'responsavel__perfil',
                    'perfil_ativo',
                )
                .prefetch_related(
                    'tags',
                    'anexos',
                    'despachos__autor',
                    'despachos__autor__perfil',
                    'despachos__anexos',
                    'despachos__responsavel_anterior',
                    'despachos__responsavel_novo',
                    'cidadao__perfis_profissionais__tag',
                )
                .all()
            )
        return filtrar_atendimentos_visiveis(qs, self.request.user)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return filtrar_atendimentos_por_query(
            queryset,
            self.request.query_params,
            aplicar_status=True,
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if request.query_params.get('view') == 'kanban' or (
            request.query_params.get('cidadao_id') or request.query_params.get('cidadao') or ''
        ).strip().isdigit():
            queryset = queryset.order_by('-created_at')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='kanban-resumo')
    def kanban_resumo(self, request):
        qs = self.get_queryset()
        qs = super(AtendimentoViewSet, self).filter_queryset(qs)
        qs = filtrar_atendimentos_por_query(
            qs,
            request.query_params,
            aplicar_status=False,
        )
        por_status = {
            choice.value: qs.filter(status=choice.value).count()
            for choice in Atendimento.Status
        }
        return Response({'por_status': por_status, 'total': qs.count()})

    def perform_destroy(self, instance):
        if instance.status != Atendimento.Status.ABERTO:
            from rest_framework.exceptions import ValidationError

            raise ValidationError('Somente atendimentos com status Aberto podem ser excluídos.')
        super().perform_destroy(instance)

    @action(detail=False, methods=['get'], url_path='exportar-csv')
    def exportar_csv(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = filtrar_queryset_exportacao(queryset, request.query_params)
        queryset = queryset.order_by('-created_at')
        return build_atendimentos_csv_response(queryset)


class DespachoViewSet(GabineteModelViewSet):
    serializer_class = DespachoSerializer
    permission_classes = (IsAuthenticated, ActionRBACPermission)
    pagination_class = None
    http_method_names = ('get', 'post', 'head', 'options')

    rbac_action_map = {
        'list': 'ler_atend',
        'retrieve': 'ler_atend',
        'create': 'editar_atend',
    }

    def get_rbac_codename(self):
        return self.rbac_action_map.get(self.action)

    def get_queryset(self):
        visiveis = filtrar_atendimentos_visiveis(
            Atendimento.objects.all(),
            self.request.user,
        ).values_list('pk', flat=True)
        qs = Despacho.objects.select_related(
            'autor',
            'autor__perfil',
            'atendimento',
        ).filter(atendimento_id__in=visiveis)
        atendimento_id = self.request.query_params.get('atendimento')
        if atendimento_id:
            qs = qs.filter(atendimento_id=atendimento_id)
        return qs


class AnexoViewSet(GabineteModelViewSet):
    serializer_class = AnexoSerializer
    permission_classes = (IsAuthenticated, ActionRBACPermission)
    parser_classes = (MultiPartParser, FormParser)
    pagination_class = None
    http_method_names = ('get', 'post', 'delete', 'head', 'options')

    rbac_action_map = {
        'list': 'ler_atend',
        'retrieve': 'ler_atend',
        'create': 'editar_atend',
        'destroy': 'editar_atend',
        'download': 'ler_atend',
    }

    def get_rbac_codename(self):
        codename = self.rbac_action_map.get(self.action)
        return codename or 'ler_atend'

    def get_queryset(self):
        visiveis = filtrar_atendimentos_visiveis(
            Atendimento.objects.all(),
            self.request.user,
        ).values_list('pk', flat=True)
        qs = Anexo.objects.select_related('atendimento', 'despacho', 'enviado_por').filter(
            atendimento_id__in=visiveis,
        )
        atendimento_id = self.request.query_params.get('atendimento')
        if atendimento_id:
            qs = qs.filter(atendimento_id=atendimento_id)
        return qs

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        anexo = self.get_object()
        arquivo = anexo.arquivo.open('rb')
        response = FileResponse(arquivo, as_attachment=True, filename=anexo.nome_original)
        if anexo.content_type:
            response['Content-Type'] = anexo.content_type
        return response
