from django.db.models import Q
from django.http import FileResponse
from config.viewsets import GabineteModelViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from usuarios.permissions import ActionRBACPermission

from .permissions import CidadaoListAccessPermission, TagRBACPermission

from .geocode_service import geocodificar_endereco
from .models import Cidadao, DocumentoAnexo, Tag
from .serializers import (
    CidadaoBuscaSerializer,
    CidadaoListSerializer,
    CidadaoSerializer,
    DocumentoAnexoSerializer,
    GeocodeEntradaSerializer,
    TagSerializer,
)


class CidadaoPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class CidadaoViewSet(GabineteModelViewSet):
    serializer_class = CidadaoSerializer
    permission_classes = (IsAuthenticated, ActionRBACPermission)
    pagination_class = CidadaoPagination
    filter_backends = (SearchFilter,)
    search_fields = (
        'nome',
        'nome_social',
        'cpf',
        'telefone',
        'email',
        'endereco__bairro',
        'endereco__cidade',
    )

    rbac_action_map = {
        'list': 'ler_crm',
        'retrieve': 'ler_crm',
        'create': 'criar_crm',
        'update': 'editar_crm',
        'partial_update': 'editar_crm',
        'destroy': 'excluir_crm',
    }

    def get_rbac_codename(self):
        return self.rbac_action_map.get(self.action)

    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated(), CidadaoListAccessPermission()]
        return [IsAuthenticated(), ActionRBACPermission()]

    def get_serializer_class(self):
        if self.action == 'list':
            params = self.request.query_params
            if params.get('anexo_categoria', '').strip():
                return CidadaoBuscaSerializer
            return CidadaoListSerializer
        return CidadaoSerializer

    def get_queryset(self):
        qs = (
            Cidadao.objects.select_related('endereco')
            .prefetch_related('perfis_profissionais__tag', 'marcadores')
            .all()
        )
        anexo_categoria = (self.request.query_params.get('anexo_categoria') or '').strip()
        if anexo_categoria:
            qs = qs.filter(documentos__categoria=anexo_categoria).distinct()
        raw_tag_ids = (self.request.query_params.get('curriculo_tag_ids') or '').strip()
        if raw_tag_ids:
            tag_ids: list[int] = []
            for part in raw_tag_ids.split(','):
                part = part.strip()
                if part.isdigit():
                    tag_ids.append(int(part))
            if tag_ids:
                qs = qs.filter(
                    documentos__categoria=DocumentoAnexo.Categoria.CURRICULO,
                    documentos__etiquetas__id__in=tag_ids,
                ).distinct()
        raw_segmentacao = (self.request.query_params.get('segmentacao_tag_ids') or '').strip()
        if raw_segmentacao:
            seg_ids: list[int] = []
            for part in raw_segmentacao.split(','):
                part = part.strip()
                if part.isdigit():
                    seg_ids.append(int(part))
            if seg_ids:
                qs = qs.filter(
                    Q(marcadores__id__in=seg_ids)
                    | Q(perfis_profissionais__tag_id__in=seg_ids)
                    | Q(documentos__etiquetas__id__in=seg_ids),
                ).distinct()
        return qs


class TagViewSet(GabineteModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticated, TagRBACPermission)
    pagination_class = None


class DocumentoAnexoViewSet(GabineteModelViewSet):
    """Anexos de documentos vinculados ao cidadão (PDF, DOC, DOCX, JPG, PNG — máx. 10MB)."""

    serializer_class = DocumentoAnexoSerializer
    permission_classes = (IsAuthenticated, ActionRBACPermission)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    pagination_class = None
    http_method_names = ('get', 'post', 'patch', 'delete', 'head', 'options')

    rbac_action_map = {
        'list': 'ler_crm',
        'retrieve': 'ler_crm',
        'create': 'editar_crm',
        'partial_update': 'editar_crm',
        'destroy': 'editar_crm',
        'download': 'ler_crm',
    }

    def get_rbac_codename(self):
        codename = self.rbac_action_map.get(self.action)
        if codename:
            return codename
        return 'ler_crm'

    def get_queryset(self):
        qs = DocumentoAnexo.objects.select_related('cidadao', 'enviado_por').prefetch_related(
            'etiquetas',
        )
        cidadao_id = self.request.query_params.get('cidadao')
        categoria = (self.request.query_params.get('categoria') or '').strip()
        if categoria:
            qs = qs.filter(categoria=categoria)
        if self.action == 'list':
            if not cidadao_id:
                return qs.none()
            return qs.filter(cidadao_id=cidadao_id)
        return qs

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        documento = self.get_object()
        arquivo = documento.arquivo.open('rb')
        response = FileResponse(arquivo, as_attachment=True, filename=documento.nome_original)
        if documento.content_type:
            response['Content-Type'] = documento.content_type
        return response


class GeocodeEnderecoView(APIView):
    """Geocodifica endereço brasileiro (Nominatim → Photon → Open-Meteo)."""

    permission_classes = (IsAuthenticated, ActionRBACPermission)

    def get_rbac_codename(self):
        return 'ler_crm'

    def post(self, request):
        entrada = GeocodeEntradaSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)

        resultado = geocodificar_endereco(entrada.validated_data)
        if resultado is None:
            return Response(
                {'latitude': None, 'longitude': None, 'precisao': None},
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                'latitude': resultado.latitude,
                'longitude': resultado.longitude,
                'precisao': resultado.precisao,
            }
        )
