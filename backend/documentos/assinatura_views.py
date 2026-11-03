from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .assinatura_validators import validar_arquivo_assinatura


class MinhaAssinaturaVisualView(APIView):
    """
    Assinatura visual reutilizável do usuário logado (PNG/JPG/WebP, máx. 2MB).
    GET: URL da imagem | POST: upload (multipart campo `arquivo`) | DELETE: remove
    """

    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def _url_assinatura(self, request, user) -> str | None:
        if not user.assinatura_visual:
            return None
        return request.build_absolute_uri(user.assinatura_visual.url)

    def get(self, request):
        url = self._url_assinatura(request, request.user)
        return Response({'url': url, 'has_assinatura': bool(url)})

    def post(self, request):
        arquivo = request.FILES.get('arquivo')
        if not arquivo:
            return Response({'arquivo': ['Envie o arquivo no campo «arquivo».']}, status=400)

        try:
            validar_arquivo_assinatura(arquivo)
        except DjangoValidationError as exc:
            return Response({'arquivo': list(exc.messages)}, status=400)

        user = request.user
        if user.assinatura_visual:
            user.assinatura_visual.delete(save=False)

        ext = 'png'
        if arquivo.content_type == 'image/jpeg':
            ext = 'jpg'
        elif arquivo.content_type == 'image/webp':
            ext = 'webp'

        nome = f'assinatura_{user.pk}.{ext}'
        user.assinatura_visual.save(nome, arquivo, save=True)

        return Response(
            {
                'url': self._url_assinatura(request, user),
                'has_assinatura': True,
            },
            status=200,
        )

    def delete(self, request):
        user = request.user
        if user.assinatura_visual:
            user.assinatura_visual.delete(save=True)
        return Response(status=204)
