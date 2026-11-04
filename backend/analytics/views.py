from datetime import datetime

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .assessor_service import build_assessor_desempenho, build_equipe_desempenho
from .export_csv import build_assessor_desempenho_csv_response, build_equipe_desempenho_csv_response
from .permissions import codename_permission, codename_permission_any
from .services import (
    PINS_LIMIT_MAX,
    PINS_LIMIT_PADRAO,
    build_executivo,
    build_territorial,
    build_territorial_filtros,
    build_territorial_pins,
    build_territorial_zonas,
)

RequireDashboardExecutivo = codename_permission('view_dashboard_executivo')
RequireDashboardGestao = codename_permission_any(
    'view_dashboard_executivo',
    'view_dashboard_operacional',
)
RequireMapa = codename_permission('view_mapa')


def _parse_macrotema_id(raw) -> int | None:
    if raw in (None, ''):
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def _parse_territorial_filtros(request) -> tuple[str | None, int | None, str | None]:
    agrupamento = (request.query_params.get('agrupamento') or 'macrotema').strip().lower()
    bairro = (request.query_params.get('bairro') or '').strip() or None
    macrotema_id = _parse_macrotema_id(request.query_params.get('macrotema_id'))
    return agrupamento, macrotema_id, bairro


def _parse_bbox(request) -> dict[str, float] | None:
    keys = ('sw_lat', 'sw_lng', 'ne_lat', 'ne_lng')
    if not all(request.query_params.get(k) not in (None, '') for k in keys):
        return None
    try:
        return {
            'sw_lat': float(request.query_params['sw_lat']),
            'sw_lng': float(request.query_params['sw_lng']),
            'ne_lat': float(request.query_params['ne_lat']),
            'ne_lng': float(request.query_params['ne_lng']),
        }
    except (TypeError, ValueError):
        return None


def _parse_date_param(raw: str | None):
    if not raw:
        return None
    try:
        return datetime.strptime(raw.strip()[:10], '%Y-%m-%d').date()
    except (TypeError, ValueError):
        return None


def _parse_pins_limit(request) -> int:
    raw = request.query_params.get('limit')
    if raw in (None, ''):
        return PINS_LIMIT_PADRAO
    try:
        return min(max(int(raw), 1), PINS_LIMIT_MAX)
    except (TypeError, ValueError):
        return PINS_LIMIT_PADRAO


class ExecutivoAnalyticsView(APIView):
    permission_classes = (IsAuthenticated, RequireDashboardExecutivo)

    def get(self, request):
        return Response(build_executivo(request.user))


class TerritorialAnalyticsView(APIView):
    permission_classes = (IsAuthenticated, RequireMapa)

    def get(self, request):
        agrupamento, macrotema_id, bairro = _parse_territorial_filtros(request)
        return Response(
            build_territorial(
                request.user,
                agrupamento=agrupamento,
                macrotema_id=macrotema_id,
                bairro=bairro,
            )
        )


class TerritorialFiltrosView(APIView):
    permission_classes = (IsAuthenticated, RequireMapa)

    def get(self, request):
        _, macrotema_id, bairro = _parse_territorial_filtros(request)
        return Response(
            build_territorial_filtros(
                request.user,
                macrotema_id=macrotema_id,
                bairro=bairro,
            )
        )


class TerritorialZonasView(APIView):
    permission_classes = (IsAuthenticated, RequireMapa)

    def get(self, request):
        agrupamento, macrotema_id, bairro = _parse_territorial_filtros(request)
        return Response(
            build_territorial_zonas(
                request.user,
                agrupamento=agrupamento,
                macrotema_id=macrotema_id,
                bairro=bairro,
            )
        )


class TerritorialPinsView(APIView):
    permission_classes = (IsAuthenticated, RequireMapa)

    def get(self, request):
        _, macrotema_id, bairro = _parse_territorial_filtros(request)
        return Response(
            build_territorial_pins(
                request.user,
                macrotema_id=macrotema_id,
                bairro=bairro,
                bbox=_parse_bbox(request),
                limit=_parse_pins_limit(request),
            )
        )


def _parse_responsavel_id(request) -> tuple[int | None, Response | None]:
    raw_id = request.query_params.get('responsavel_id')
    if raw_id in (None, ''):
        return None, Response(
            {'detail': 'Informe responsavel_id.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        return int(raw_id), None
    except (TypeError, ValueError):
        return None, Response(
            {'detail': 'responsavel_id inválido.'},
            status=status.HTTP_400_BAD_REQUEST,
        )


class EquipeDesempenhoView(APIView):
    permission_classes = (IsAuthenticated, RequireDashboardGestao)

    def get(self, request):
        return Response(build_equipe_desempenho(request.user))


class EquipeDesempenhoExportView(APIView):
    permission_classes = (IsAuthenticated, RequireDashboardGestao)

    def get(self, request):
        return build_equipe_desempenho_csv_response(request.user)


class AssessorDesempenhoView(APIView):
    permission_classes = (IsAuthenticated, RequireDashboardGestao)

    def get(self, request):
        responsavel_id, err = _parse_responsavel_id(request)
        if err:
            return err

        de = _parse_date_param(request.query_params.get('de'))
        ate = _parse_date_param(request.query_params.get('ate'))
        payload = build_assessor_desempenho(
            request.user,
            responsavel_id,
            de=de,
            ate=ate,
        )
        if 'detail' in payload and len(payload) == 1:
            code = (
                status.HTTP_403_FORBIDDEN
                if 'permissão' in payload['detail'].lower()
                else status.HTTP_404_NOT_FOUND
            )
            return Response(payload, status=code)
        return Response(payload)


class AssessorDesempenhoExportView(APIView):
    permission_classes = (IsAuthenticated, RequireDashboardGestao)

    def get(self, request):
        responsavel_id, err = _parse_responsavel_id(request)
        if err:
            return err

        de = _parse_date_param(request.query_params.get('de'))
        ate = _parse_date_param(request.query_params.get('ate'))
        csv_response = build_assessor_desempenho_csv_response(
            request.user,
            responsavel_id,
            de=de,
            ate=ate,
        )
        if csv_response is None:
            payload = build_assessor_desempenho(
                request.user,
                responsavel_id,
                de=de,
                ate=ate,
            )
            code = (
                status.HTTP_403_FORBIDDEN
                if payload.get('detail', '').lower().find('permissão') >= 0
                else status.HTTP_404_NOT_FOUND
            )
            return Response(payload, status=code)
        return csv_response
