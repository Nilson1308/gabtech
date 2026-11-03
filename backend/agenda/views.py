from config.viewsets import GabineteModelViewSet
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from usuarios.permissions import ActionRBACPermission

from .models import Espaco, Evento, TipoEvento
from .serializers import EspacoSerializer, EventoSerializer, TipoEventoSerializer


class EventoPagination(PageNumberPagination):
    page_size = 500
    page_size_query_param = 'page_size'
    max_page_size = 2000


class TipoEventoViewSet(GabineteModelViewSet):
    queryset = TipoEvento.objects.all()
    serializer_class = TipoEventoSerializer
    permission_classes = (IsAuthenticated, ActionRBACPermission)
    pagination_class = None

    rbac_action_map = {
        'list': 'ler_agenda',
        'retrieve': 'ler_agenda',
        'create': 'manage_agenda_cerimonial',
        'update': 'manage_agenda_cerimonial',
        'partial_update': 'manage_agenda_cerimonial',
        'destroy': 'manage_agenda_cerimonial',
    }

    def get_rbac_codename(self):
        return self.rbac_action_map.get(self.action)

    def perform_destroy(self, instance):
        em_uso = Evento.objects.filter(tipo=instance, status=Evento.Status.AGENDADO).count()
        if em_uso:
            raise ValidationError(
                f'Não é possível excluir. Existem {em_uso} evento(s) agendado(s) com este tipo.',
            )
        super().perform_destroy(instance)


class EspacoViewSet(GabineteModelViewSet):
    queryset = Espaco.objects.all()
    serializer_class = EspacoSerializer
    permission_classes = (IsAuthenticated, ActionRBACPermission)
    pagination_class = None

    rbac_action_map = {
        'list': 'ler_agenda',
        'retrieve': 'ler_agenda',
        'create': 'manage_agenda_cerimonial',
        'update': 'manage_agenda_cerimonial',
        'partial_update': 'manage_agenda_cerimonial',
        'destroy': 'manage_agenda_cerimonial',
    }

    def get_rbac_codename(self):
        return self.rbac_action_map.get(self.action)

    def perform_destroy(self, instance):
        em_uso = Evento.objects.filter(espaco=instance, status=Evento.Status.AGENDADO).count()
        if em_uso:
            raise ValidationError(
                f'Não é possível excluir. Existem {em_uso} evento(s) agendado(s) neste espaço.',
            )
        super().perform_destroy(instance)


class EventoViewSet(GabineteModelViewSet):
    serializer_class = EventoSerializer
    permission_classes = (IsAuthenticated, ActionRBACPermission)
    pagination_class = EventoPagination

    rbac_action_map = {
        'list': 'ler_agenda',
        'retrieve': 'ler_agenda',
        'create': 'criar_agenda',
        'update': 'editar_agenda',
        'partial_update': 'editar_agenda',
        'destroy': 'excluir_agenda',
    }

    def get_rbac_codename(self):
        return self.rbac_action_map.get(self.action)

    def get_queryset(self):
        qs = (
            Evento.objects.select_related('tipo', 'espaco', 'criado_por', 'criado_por__perfil')
            .prefetch_related('convidados', 'convidados__perfis_profissionais__tag')
        )
        data_de = self.request.query_params.get('data_de')
        data_ate = self.request.query_params.get('data_ate')
        if data_de:
            qs = qs.filter(data__gte=data_de)
        if data_ate:
            qs = qs.filter(data__lte=data_ate)
        return qs
