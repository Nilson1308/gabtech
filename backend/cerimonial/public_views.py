from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import EventoCerimonial, ItemChecklist
from .serializers import (
    ItemChecklistPublicSerializer,
    LogisticaPublicaEnviarSerializer,
    LogisticaPublicaEventoSerializer,
)


def _evento_por_token(token):
    return get_object_or_404(
        EventoCerimonial.objects.select_related('evento_agenda', 'evento_agenda__espaco'),
        token_logistica=token,
        logistica_publica_ativa=True,
    )


class LogisticaPublicaView(APIView):
    """GET checklist logístico via token (colaboradores externos)."""

    permission_classes = (AllowAny,)
    authentication_classes = ()

    def get(self, request, token):
        evento = _evento_por_token(token)
        serializer = LogisticaPublicaEventoSerializer(evento)
        return Response(serializer.data)


class LogisticaPublicaEnviarView(APIView):
    """
    POST — colaborador externo envia em lote alterações e descartes.
    Só persiste no banco quando este endpoint é chamado.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()

    @transaction.atomic
    def post(self, request, token):
        evento = _evento_por_token(token)
        payload = LogisticaPublicaEnviarSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        data = payload.validated_data

        for row in data['itens']:
            item_id = row['id']
            item = get_object_or_404(ItemChecklist, pk=item_id, evento=evento)

            if row.get('descartar'):
                item.delete()
                continue

            if 'responsavel' in row:
                item.responsavel = row['responsavel'] or ''
            if 'prazo' in row:
                item.prazo = row['prazo']
            if 'observacoes' in row:
                item.observacoes = row['observacoes'] or ''
            if row.get('status'):
                item.status = row['status']
            item.save()

        update_fields = ['logistica_publica_ativa', 'updated_at']
        if data.get('observacao_envio'):
            evento.observacao_logistica_externa = data['observacao_envio'].strip()
            update_fields.append('observacao_logistica_externa')

        # Encerra o link após envio — nova edição exige novo token no painel interno.
        evento.logistica_publica_ativa = False
        evento.save(update_fields=update_fields)

        evento.refresh_from_db()
        return Response(
            {
                'ok': True,
                'mensagem': 'Checklist atualizada com sucesso. Este link foi encerrado.',
                'link_encerrado': True,
                'checklist': ItemChecklistPublicSerializer(
                    evento.checklist.all(),
                    many=True,
                ).data,
            },
        )
