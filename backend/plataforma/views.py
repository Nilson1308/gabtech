from django.conf import settings
from django.core.cache import cache
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from plataforma.models import CadastroGabinete
from plataforma.schema import PublicSchemaMixin
from plataforma.serializers import CadastroGabineteEntradaSerializer, CadastroGabineteStatusSerializer
from plataforma.services import enfileirar_provisionamento


def _client_ip(request) -> str | None:
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _throttle_signup(request) -> str | None:
    limite = int(getattr(settings, 'GABTECH_SIGNUP_RATE_LIMIT', 5))
    janela = int(getattr(settings, 'GABTECH_SIGNUP_RATE_WINDOW_SECONDS', 3600))
    ip = _client_ip(request) or 'unknown'
    chave = f'gabtech:signup:{ip}'
    atual = cache.get(chave, 0)
    if atual >= limite:
        return 'Muitas tentativas de cadastro. Tente novamente mais tarde.'
    cache.set(chave, atual + 1, timeout=janela)
    return None


class CadastroGabineteCreateView(PublicSchemaMixin, APIView):
    """Self-service: cria solicitação e provisiona tenant em background."""

    permission_classes = (AllowAny,)

    def post(self, request):
        if not getattr(settings, 'GABTECH_SIGNUP_ENABLED', True):
            return Response(
                {'detail': 'Cadastro de novos gabinetes está temporariamente desabilitado.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        throttle_msg = _throttle_signup(request)
        if throttle_msg:
            return Response({'detail': throttle_msg}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        serializer = CadastroGabineteEntradaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        CadastroGabinete.objects.filter(
            slug=data['slug'],
            status=CadastroGabinete.Status.FALHOU,
        ).delete()

        cadastro = CadastroGabinete.objects.create(
            slug=data['slug'],
            nome_gabinete=data['nome_gabinete'].strip(),
            logo=data.get('logo') or '',
            logo_formato=data.get('logo_formato') or '1:1',
            admin_nome=data['admin_nome'].strip(),
            admin_email=data['admin_email'].strip().lower(),
            aceite_termos=True,
            ip_origem=_client_ip(request),
        )

        senha = data['admin_senha']
        enfileirar_provisionamento(cadastro, senha)

        out = CadastroGabineteStatusSerializer(cadastro)
        return Response(out.data, status=status.HTTP_202_ACCEPTED)


class CadastroGabineteStatusView(PublicSchemaMixin, APIView):
    permission_classes = (AllowAny,)

    def get(self, request, cadastro_id):
        try:
            cadastro = CadastroGabinete.objects.get(pk=cadastro_id)
        except CadastroGabinete.DoesNotExist:
            return Response({'detail': 'Cadastro não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(CadastroGabineteStatusSerializer(cadastro).data)
