from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import codename_permission
from .services import build_executivo, build_territorial

RequireDashboardExecutivo = codename_permission('view_dashboard_executivo')
RequireMapa = codename_permission('view_mapa')


class ExecutivoAnalyticsView(APIView):
    permission_classes = (IsAuthenticated, RequireDashboardExecutivo)

    def get(self, request):
        return Response(build_executivo(request.user))


class TerritorialAnalyticsView(APIView):
    permission_classes = (IsAuthenticated, RequireMapa)

    def get(self, request):
        agrupamento = (request.query_params.get('agrupamento') or 'macrotema').strip().lower()
        bairro = (request.query_params.get('bairro') or '').strip() or None
        macrotema_id = None
        raw_macro = request.query_params.get('macrotema_id')
        if raw_macro not in (None, ''):
            try:
                macrotema_id = int(raw_macro)
            except (TypeError, ValueError):
                macrotema_id = None

        return Response(
            build_territorial(
                request.user,
                agrupamento=agrupamento,
                macrotema_id=macrotema_id,
                bairro=bairro,
            )
        )
