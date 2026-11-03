from django.db.models import Q
from django.utils import timezone
from config.viewsets import GabineteModelViewSet, GabineteReadOnlyModelViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from usuarios.permissions import ActionRBACPermission

from .models import (
    Documento,
    EtiquetaDocumento,
    PastaDocumento,
    TemplateDocumento,
    TipoDocumento,
    VersaoDocumento,
)
from .serializers import (
    DocumentoSerializer,
    EtiquetaDocumentoSerializer,
    PastaDocumentoSerializer,
    TemplateDocumentoSerializer,
    TipoDocumentoSerializer,
    TipoDocumentoWriteSerializer,
    VersaoDocumentoSerializer,
)


class TipoDocumentoViewSet(GabineteModelViewSet):
    queryset = TipoDocumento.objects.all()
    permission_classes = (IsAuthenticated, ActionRBACPermission)
    pagination_class = None

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(TipoDocumentoSerializer(instance).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(TipoDocumentoSerializer(instance).data)

    rbac_action_map = {
        'list': 'ler_docs',
        'retrieve': 'ler_docs',
        'create': 'manage_docs_config',
        'update': 'manage_docs_config',
        'partial_update': 'manage_docs_config',
        'destroy': 'manage_docs_config',
    }

    def get_rbac_codename(self):
        return self.rbac_action_map.get(self.action)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return TipoDocumentoWriteSerializer
        return TipoDocumentoSerializer

    def perform_destroy(self, instance):
        if instance.is_sistema:
            raise ValidationError('Tipos do sistema não podem ser excluídos.')
        if instance.documentos.exists():
            raise ValidationError('Existem documentos vinculados a este tipo.')
        if instance.templates.exists():
            raise ValidationError('Existem templates vinculados a este tipo.')
        super().perform_destroy(instance)


class TemplateDocumentoViewSet(GabineteModelViewSet):
    queryset = TemplateDocumento.objects.select_related('tipo_documento')
    serializer_class = TemplateDocumentoSerializer
    permission_classes = (IsAuthenticated, ActionRBACPermission)
    pagination_class = None

    rbac_action_map = {
        'list': 'ler_docs',
        'retrieve': 'ler_docs',
        'create': 'criar_docs',
        'update': 'editar_docs',
        'partial_update': 'editar_docs',
        'destroy': 'excluir_docs',
    }

    def get_rbac_codename(self):
        return self.rbac_action_map.get(self.action)

    def get_queryset(self):
        qs = super().get_queryset()
        tipo_slug = self.request.query_params.get('tipo')
        if tipo_slug:
            qs = qs.filter(tipo_documento__slug=tipo_slug)
        return qs

    def perform_destroy(self, instance):
        if instance.is_default:
            outros = TemplateDocumento.objects.filter(tipo_documento=instance.tipo_documento).exclude(
                pk=instance.pk,
            )
            if not outros.exists():
                raise ValidationError('Não é possível excluir o único template deste tipo.')
        super().perform_destroy(instance)


class EtiquetaDocumentoViewSet(GabineteModelViewSet):
    queryset = EtiquetaDocumento.objects.all()
    serializer_class = EtiquetaDocumentoSerializer
    permission_classes = (IsAuthenticated, ActionRBACPermission)
    pagination_class = None

    rbac_action_map = {
        'list': 'ler_docs',
        'retrieve': 'ler_docs',
        'create': 'editar_docs',
        'update': 'editar_docs',
        'partial_update': 'editar_docs',
        'destroy': 'editar_docs',
    }

    def get_rbac_codename(self):
        return self.rbac_action_map.get(self.action)

    def perform_destroy(self, instance):
        if instance.documentos.exists():
            raise ValidationError(
                'Não é possível excluir uma etiqueta vinculada a documentos.',
            )
        super().perform_destroy(instance)


class PastaDocumentoViewSet(GabineteModelViewSet):
    queryset = PastaDocumento.objects.all()
    serializer_class = PastaDocumentoSerializer
    permission_classes = (IsAuthenticated, ActionRBACPermission)
    pagination_class = None

    rbac_action_map = {
        'list': 'ler_docs',
        'retrieve': 'ler_docs',
        'create': 'manage_docs_config',
        'update': 'manage_docs_config',
        'partial_update': 'manage_docs_config',
        'destroy': 'manage_docs_config',
    }

    def get_rbac_codename(self):
        return self.rbac_action_map.get(self.action)

    def perform_destroy(self, instance):
        if instance.documentos.exists():
            raise ValidationError(
                'Não é possível excluir uma pasta que contém documentos.',
            )
        if instance.filhos.exists():
            raise ValidationError(
                'Não é possível excluir uma pasta que possui subpastas.',
            )
        super().perform_destroy(instance)


class DocumentoViewSet(GabineteModelViewSet):
    serializer_class = DocumentoSerializer
    permission_classes = (IsAuthenticated, ActionRBACPermission)
    pagination_class = None

    rbac_action_map = {
        'list': 'ler_docs',
        'retrieve': 'ler_docs',
        'create': 'criar_docs',
        'update': 'editar_docs',
        'partial_update': 'editar_docs',
        'destroy': 'excluir_docs',
        'restaurar_versao': 'editar_docs',
    }

    def get_rbac_codename(self):
        codename = self.rbac_action_map.get(self.action)
        if self.action in ('update', 'partial_update') and self.request.method in ('PUT', 'PATCH'):
            data = self.request.data
            if data.get('status') == Documento.Status.FINALIZADO:
                return 'sign_docs'
        return codename

    def get_queryset(self):
        qs = (
            Documento.objects.select_related(
                'tipo_documento',
                'pasta',
                'autor',
                'autor__perfil',
            )
            .prefetch_related(
                'assinantes',
                'assinantes__perfil',
                'etiquetas',
                'versoes',
                'versoes__autor',
                'versoes__autor__perfil',
            )
        )
        status_param = self.request.query_params.get('status')
        pasta_id = self.request.query_params.get('pasta_id')
        sem_pasta = self.request.query_params.get('sem_pasta')
        etiqueta_id = self.request.query_params.get('etiqueta_id')
        busca = self.request.query_params.get('q')

        if status_param:
            qs = qs.filter(status=status_param)
        if pasta_id:
            qs = qs.filter(pasta_id=pasta_id)
        if sem_pasta in ('1', 'true', 'True'):
            qs = qs.filter(pasta__isnull=True)
        if etiqueta_id:
            qs = qs.filter(etiquetas__id=etiqueta_id).distinct()
        if busca:
            qs = qs.filter(
                Q(titulo__icontains=busca) | Q(etiquetas__nome__icontains=busca),
            ).distinct()
        return qs

    @action(detail=True, methods=['post'], url_path='restaurar-versao')
    def restaurar_versao(self, request, pk=None):
        documento = self.get_object()
        if documento.status == Documento.Status.FINALIZADO:
            raise ValidationError('Documento finalizado não pode ser restaurado.')

        numero = request.data.get('numero_versao')
        if numero is None:
            raise ValidationError({'numero_versao': 'Informe o número da versão.'})

        versao = VersaoDocumento.objects.filter(documento=documento, numero_versao=numero).first()
        if not versao:
            raise ValidationError('Versão não encontrada.')

        serializer = self.get_serializer(
            documento,
            data={'conteudo': versao.conteudo},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        if instance.status == Documento.Status.FINALIZADO:
            raise ValidationError('Documentos finalizados não podem ser excluídos.')
        super().perform_destroy(instance)


class VersaoDocumentoViewSet(GabineteReadOnlyModelViewSet):
    serializer_class = VersaoDocumentoSerializer
    permission_classes = (IsAuthenticated, ActionRBACPermission)
    pagination_class = None

    rbac_action_map = {
        'list': 'ler_docs',
        'retrieve': 'ler_docs',
    }

    def get_rbac_codename(self):
        return self.rbac_action_map.get(self.action)

    def get_queryset(self):
        qs = VersaoDocumento.objects.select_related('documento', 'autor', 'autor__perfil')
        documento_id = self.request.query_params.get('documento')
        if documento_id:
            qs = qs.filter(documento_id=documento_id)
        return qs
