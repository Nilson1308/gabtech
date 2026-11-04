import uuid

from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from agenda.models import Evento
from config.viewsets import GabineteModelViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from usuarios.permissions import ActionRBACPermission

from .credenciamento_config import normalize_credenciamento_config
from .list_service import build_eventos_resumo
from .models import (
    ComunicacaoDisparo,
    ConvidadoEvento,
    Credenciado,
    EventoCerimonial,
    ItemChecklist,
    ItemChecklistPadrao,
)
from .serializers import (
    ComunicacaoDisparoSerializer,
    ConvidadoEventoSerializer,
    CredenciadoSerializer,
    EventoCerimonialListSerializer,
    EventoCerimonialSerializer,
    EventoPublicoSerializer,
    ItemChecklistPadraoSerializer,
    ItemChecklistSerializer,
    ReordenarConvidadosSerializer,
)


class EventoCerimonialPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 100


class EventoCerimonialViewSet(GabineteModelViewSet):
    queryset = EventoCerimonial.objects.select_related(
        'evento_agenda',
        'evento_agenda__tipo',
        'evento_agenda__espaco',
    ).prefetch_related(
        'checklist',
        'convidados__cidadao',
        'convidados__perfil_ativo',
        'credenciados',
        'comunicacoes',
    )
    permission_classes = (IsAuthenticated, ActionRBACPermission)
    pagination_class = EventoCerimonialPagination

    rbac_action_map = {
        'list': 'ler_eventos',
        'retrieve': 'ler_eventos',
        'create': 'criar_eventos',
        'update': 'criar_eventos',
        'partial_update': 'criar_eventos',
        'destroy': 'criar_eventos',
        'resumo': 'ler_eventos',
        'reordenar_convidados': 'gerenciar_convidados',
        'publico': None,
        'credenciamento_publico': None,
        'ativar_link_logistica': 'criar_eventos',
        'revogar_link_logistica': 'criar_eventos',
    }

    def get_rbac_codename(self):
        return self.rbac_action_map.get(self.action)

    def get_permissions(self):
        if self.action in ('publico', 'credenciamento_publico'):
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'list':
            return EventoCerimonialListSerializer
        if self.action == 'publico':
            return EventoPublicoSerializer
        return EventoCerimonialSerializer

    def get_queryset(self):
        if self.action == 'list':
            qs = EventoCerimonial.objects.select_related(
                'evento_agenda',
                'evento_agenda__tipo',
                'evento_agenda__espaco',
            ).annotate(total_convidados_ann=Count('convidados', distinct=True))
            qs = qs.order_by('-evento_agenda__data', '-evento_agenda__hora_inicio', '-id')

            busca = self.request.query_params.get('q')
            status_param = self.request.query_params.get('status_logistico')
            if busca:
                qs = qs.filter(
                    Q(evento_agenda__titulo__icontains=busca)
                    | Q(evento_agenda__espaco__nome__icontains=busca),
                )
            if status_param == 'confirmado':
                qs = qs.filter(
                    evento_agenda__status=Evento.Status.AGENDADO,
                    status_logistico=EventoCerimonial.StatusLogistico.PLANEJAMENTO,
                )
            elif status_param:
                qs = qs.filter(status_logistico=status_param)
            return qs

        return super().get_queryset()

    @action(detail=False, methods=['get'], url_path='resumo')
    def resumo(self, request):
        return Response(build_eventos_resumo())

    def perform_destroy(self, instance):
        evento_agenda = instance.evento_agenda
        super().perform_destroy(instance)
        evento_agenda.delete()

    @action(detail=True, methods=['get'], url_path='publico')
    def publico(self, request, pk=None):
        evento = self.get_object()
        if evento.status_logistico == EventoCerimonial.StatusLogistico.CANCELADO:
            return Response({'detail': 'Evento indisponível.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = EventoPublicoSerializer(evento)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='credenciamento-publico')
    def credenciamento_publico(self, request, pk=None):
        evento = self.get_object()
        if evento.status_logistico == EventoCerimonial.StatusLogistico.CANCELADO:
            raise ValidationError('Credenciamento indisponível para este evento.')

        serializer = CredenciadoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        config = normalize_credenciamento_config(evento.credenciamento_config)
        telefone = serializer.validated_data['telefone']
        if Credenciado.objects.filter(evento=evento, telefone=telefone).exists():
            raise ValidationError('Este telefone já foi registrado neste evento.')

        email = serializer.validated_data.get('email', '') or ''
        data_nascimento = serializer.validated_data.get('data_nascimento')
        orgao_instituicao = serializer.validated_data.get('orgao_instituicao', '') or ''
        if not config['mostrar_email']:
            email = ''
        if not config['mostrar_data_nascimento']:
            data_nascimento = None
        if not config['mostrar_orgao_instituicao']:
            orgao_instituicao = ''

        credenciado = Credenciado.objects.create(
            evento=evento,
            nome=serializer.validated_data['nome'],
            telefone=telefone,
            email=email,
            data_nascimento=data_nascimento,
            orgao_instituicao=orgao_instituicao,
            cpf=serializer.validated_data.get('cpf', '') or '',
            aceitou_lgpd=True,
            status_presenca=Credenciado.StatusPresenca.PRESENTE,
        )
        return Response(CredenciadoSerializer(credenciado).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='reordenar-convidados')
    def reordenar_convidados(self, request, pk=None):
        evento = self.get_object()
        payload = ReordenarConvidadosSerializer(data=request.data)
        payload.is_valid(raise_exception=True)

        with transaction.atomic():
            for item in payload.validated_data['ordens']:
                conv_id = item['id']
                ordem = int(item['ordem_precedencia'])
                updated = ConvidadoEvento.objects.filter(
                    evento=evento,
                    pk=conv_id,
                ).update(ordem_precedencia=ordem, updated_at=timezone.now())
                if not updated:
                    raise ValidationError(f'Convidado {conv_id} não encontrado neste evento.')

        convidados = evento.convidados.select_related('cidadao', 'perfil_ativo').order_by('ordem_precedencia')
        return Response(ConvidadoEventoSerializer(convidados, many=True).data)

    @action(detail=True, methods=['post'], url_path='ativar-link-logistica')
    def ativar_link_logistica(self, request, pk=None):
        evento = self.get_object()
        evento.token_logistica = uuid.uuid4()
        evento.logistica_publica_ativa = True
        evento.save(update_fields=['token_logistica', 'logistica_publica_ativa', 'updated_at'])
        return Response(
            {
                'token': str(evento.token_logistica),
                'logistica_publica_ativa': True,
            },
        )

    @action(detail=True, methods=['post'], url_path='revogar-link-logistica')
    def revogar_link_logistica(self, request, pk=None):
        evento = self.get_object()
        evento.logistica_publica_ativa = False
        evento.save(update_fields=['logistica_publica_ativa', 'updated_at'])
        return Response({'logistica_publica_ativa': False})


class ItemChecklistViewSet(GabineteModelViewSet):
    queryset = ItemChecklist.objects.select_related('evento')
    serializer_class = ItemChecklistSerializer
    permission_classes = (IsAuthenticated, ActionRBACPermission)
    pagination_class = None

    rbac_action_map = {
        'list': 'ler_eventos',
        'retrieve': 'ler_eventos',
        'create': 'criar_eventos',
        'update': 'criar_eventos',
        'partial_update': 'criar_eventos',
        'destroy': 'criar_eventos',
        'toggle': 'criar_eventos',
    }

    def get_rbac_codename(self):
        return self.rbac_action_map.get(self.action)

    def get_queryset(self):
        qs = super().get_queryset()
        evento_id = self.request.query_params.get('evento_id')
        if evento_id:
            qs = qs.filter(evento_id=evento_id)
        return qs

    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        item = self.get_object()
        if item.status == ItemChecklist.Status.PENDENTE:
            item.status = ItemChecklist.Status.PROVIDENCIADO
        elif item.status == ItemChecklist.Status.PROVIDENCIADO:
            item.status = ItemChecklist.Status.PENDENTE
        item.save(update_fields=['status', 'updated_at'])
        return Response(ItemChecklistSerializer(item).data)


class ItemChecklistPadraoViewSet(GabineteModelViewSet):
    queryset = ItemChecklistPadrao.objects.all()
    serializer_class = ItemChecklistPadraoSerializer
    permission_classes = (IsAuthenticated, ActionRBACPermission)
    pagination_class = None

    rbac_action_map = {
        'list': 'ler_eventos',
        'retrieve': 'ler_eventos',
        'create': 'criar_eventos',
        'update': 'criar_eventos',
        'partial_update': 'criar_eventos',
        'destroy': 'criar_eventos',
    }

    def get_rbac_codename(self):
        return self.rbac_action_map.get(self.action)


class ConvidadoEventoViewSet(GabineteModelViewSet):
    queryset = ConvidadoEvento.objects.select_related('cidadao', 'perfil_ativo', 'evento')
    serializer_class = ConvidadoEventoSerializer
    permission_classes = (IsAuthenticated, ActionRBACPermission)
    pagination_class = None

    rbac_action_map = {
        'list': 'ler_eventos',
        'retrieve': 'ler_eventos',
        'create': 'gerenciar_convidados',
        'update': 'gerenciar_convidados',
        'partial_update': 'gerenciar_convidados',
        'destroy': 'gerenciar_convidados',
    }

    def get_rbac_codename(self):
        return self.rbac_action_map.get(self.action)

    def get_queryset(self):
        qs = super().get_queryset()
        evento_id = self.request.query_params.get('evento_id')
        if evento_id:
            qs = qs.filter(evento_id=evento_id)
        return qs.order_by('ordem_precedencia', 'id')

    def perform_create(self, serializer):
        evento = serializer.validated_data['evento']
        max_ordem = (
            ConvidadoEvento.objects.filter(evento=evento)
            .order_by('-ordem_precedencia')
            .values_list('ordem_precedencia', flat=True)
            .first()
        ) or 0
        serializer.save(ordem_precedencia=max_ordem + 1)
        self._auditoria_registrar(serializer.instance, 'criar')


class CredenciadoViewSet(GabineteModelViewSet):
    queryset = Credenciado.objects.select_related('evento')
    serializer_class = CredenciadoSerializer
    permission_classes = (IsAuthenticated, ActionRBACPermission)
    pagination_class = None

    rbac_action_map = {
        'list': 'credenciamento',
        'retrieve': 'credenciamento',
        'create': 'credenciamento',
        'update': 'credenciamento',
        'partial_update': 'credenciamento',
        'destroy': 'credenciamento',
        'checkin': 'credenciamento',
    }

    def get_rbac_codename(self):
        return self.rbac_action_map.get(self.action)

    def get_queryset(self):
        qs = super().get_queryset()
        evento_id = self.request.query_params.get('evento_id')
        if evento_id:
            qs = qs.filter(evento_id=evento_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(status_presenca=Credenciado.StatusPresenca.PRESENTE)
        self._auditoria_registrar(serializer.instance, 'criar')

    @action(detail=True, methods=['post'])
    def checkin(self, request, pk=None):
        credenciado = self.get_object()
        credenciado.status_presenca = Credenciado.StatusPresenca.PRESENTE
        credenciado.save(update_fields=['status_presenca'])
        return Response(CredenciadoSerializer(credenciado).data)


class ComunicacaoDisparoViewSet(GabineteModelViewSet):
    queryset = ComunicacaoDisparo.objects.select_related('evento')
    serializer_class = ComunicacaoDisparoSerializer
    permission_classes = (IsAuthenticated, ActionRBACPermission)
    pagination_class = None
    http_method_names = ['get', 'post', 'head', 'options']

    rbac_action_map = {
        'list': 'disparar_comunicacao',
        'retrieve': 'disparar_comunicacao',
        'create': 'disparar_comunicacao',
    }

    def get_rbac_codename(self):
        return self.rbac_action_map.get(self.action)

    def get_queryset(self):
        qs = super().get_queryset()
        evento_id = self.request.query_params.get('evento_id')
        if evento_id:
            qs = qs.filter(evento_id=evento_id)
        return qs

    def perform_create(self, serializer):
        disparo = serializer.save(
            criado_por=self.request.user if self.request.user.is_authenticated else None,
            status=ComunicacaoDisparo.Status.ENVIADO,
        )
        if not disparo.quantidade_envios:
            estimativa = 0
            publico = disparo.publico_alvo or {}
            if publico.get('convidados'):
                estimativa += disparo.evento.convidados.filter(
                    status_confirmacao=ConvidadoEvento.StatusConfirmacao.CONFIRMADO,
                ).count()
            estimativa += int(publico.get('quantidade_estimada') or 0)
            disparo.quantidade_envios = estimativa
            disparo.save(update_fields=['quantidade_envios'])
        self._auditoria_registrar(disparo, 'criar')
