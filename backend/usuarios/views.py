from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginResponseSerializer, LoginSerializer


class LoginView(APIView):
    """
    POST /api/auth/login/
    Retorna JWT + usuário no formato esperado pelo Pinia (authStore).
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.save()

        response_data = {
            'token': payload['token'],
            'user': payload['user'],
        }
        output = LoginResponseSerializer(response_data)
        return Response(output.data, status=status.HTTP_200_OK)
