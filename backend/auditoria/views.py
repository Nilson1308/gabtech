from django.contrib.contenttypes.models import ContentType
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import EventoAuditoria
from .serializers import EventoAuditoriaSerializer


class HistoricoAuditoriaView(APIView):
    """
    Histórico completo de auditoria de um registro.
    GET ?app_label=crm&model=cidadao&object_id=42
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        app_label = (request.query_params.get('app_label') or '').strip()
        model = (request.query_params.get('model') or '').strip().lower()
        object_id = (request.query_params.get('object_id') or '').strip()

        if not app_label or not model or not object_id:
            raise ValidationError(
                {'detail': 'Informe app_label, model e object_id na query string.'},
            )

        try:
            content_type = ContentType.objects.get(app_label=app_label, model=model)
        except ContentType.DoesNotExist as exc:
            raise NotFound('Tipo de registro não encontrado.') from exc

        limite = min(int(request.query_params.get('limit', 100)), 500)
        base_qs = EventoAuditoria.objects.filter(content_type=content_type, object_id=str(object_id))
        total = base_qs.count()
        qs = base_qs.select_related('usuario').order_by('-ocorrido_em')[:limite]
        serializer = EventoAuditoriaSerializer(qs, many=True)
        return Response(
            {
                'app_label': app_label,
                'model': model,
                'object_id': object_id,
                'total': total,
                'eventos': serializer.data,
            },
        )
