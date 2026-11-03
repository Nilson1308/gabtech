from django.conf import settings
from rest_framework import serializers

from core.provisioning import (
    montar_dominio_tenant,
    normalizar_slug,
    slug_para_schema_name,
    validar_disponibilidade,
    validar_slug,
)
from plataforma.logo_utils import normalizar_logo_formato, validar_logo_data_url
from plataforma.models import CadastroGabinete


class CadastroGabineteEntradaSerializer(serializers.Serializer):
    nome_gabinete = serializers.CharField(max_length=200)
    slug = serializers.SlugField(max_length=50)
    admin_nome = serializers.CharField(max_length=300)
    admin_email = serializers.EmailField()
    admin_senha = serializers.CharField(min_length=8, max_length=128, write_only=True, trim_whitespace=False)
    admin_senha_confirmacao = serializers.CharField(
        min_length=8,
        max_length=128,
        write_only=True,
        trim_whitespace=False,
    )
    aceite_termos = serializers.BooleanField()
    codigo_convite = serializers.CharField(required=False, allow_blank=True, max_length=64)
    logo = serializers.CharField(required=False, allow_blank=True, write_only=True)
    logo_formato = serializers.CharField(required=False, allow_blank=True, max_length=5)

    def validate_logo(self, value: str) -> str:
        return validar_logo_data_url(value)

    def validate_logo_formato(self, value: str) -> str:
        return normalizar_logo_formato(value)

    def validate_slug(self, value: str) -> str:
        slug = normalizar_slug(value)
        try:
            validar_slug(slug)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        schema = slug_para_schema_name(slug)
        domain = montar_dominio_tenant(slug)
        try:
            validar_disponibilidade(slug, schema, domain)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        if CadastroGabinete.objects.filter(slug=slug).exclude(
            status=CadastroGabinete.Status.FALHOU,
        ).exists():
            raise serializers.ValidationError('Já existe um cadastro em andamento para este identificador.')
        return slug

    def validate(self, attrs):
        if not attrs.get('aceite_termos'):
            raise serializers.ValidationError({'aceite_termos': 'É necessário aceitar os termos de uso.'})

        if attrs['admin_senha'] != attrs['admin_senha_confirmacao']:
            raise serializers.ValidationError({'admin_senha_confirmacao': 'As senhas não conferem.'})

        codigo_obrigatorio = getattr(settings, 'GABTECH_SIGNUP_CODIGO_CONVITE', '').strip()
        if codigo_obrigatorio:
            informado = (attrs.get('codigo_convite') or '').strip()
            if informado != codigo_obrigatorio:
                raise serializers.ValidationError({'codigo_convite': 'Código de convite inválido.'})

        return attrs


class CadastroGabineteStatusSerializer(serializers.ModelSerializer):
    login_url = serializers.SerializerMethodField()
    api_base_url = serializers.SerializerMethodField()
    app_url_sugerida = serializers.SerializerMethodField()

    class Meta:
        model = CadastroGabinete
        fields = (
            'id',
            'status',
            'slug',
            'nome_gabinete',
            'logo',
            'logo_formato',
            'schema_name',
            'domain',
            'admin_email',
            'erro_mensagem',
            'created_at',
            'concluido_em',
            'login_url',
            'api_base_url',
            'app_url_sugerida',
        )
        read_only_fields = fields

    def get_login_url(self, obj: CadastroGabinete) -> str | None:
        if obj.status != CadastroGabinete.Status.CONCLUIDO or not obj.domain:
            return None
        from core.provisioning import url_api_tenant

        return f'{url_api_tenant(obj.domain)}/api/auth/login/'

    def get_api_base_url(self, obj: CadastroGabinete) -> str | None:
        if obj.status != CadastroGabinete.Status.CONCLUIDO or not obj.domain:
            return None
        from core.provisioning import url_api_tenant

        return url_api_tenant(obj.domain)

    def get_app_url_sugerida(self, obj: CadastroGabinete) -> str | None:
        if obj.status != CadastroGabinete.Status.CONCLUIDO or not obj.domain:
            return None
        port = getattr(settings, 'GABTECH_TENANT_APP_PORT', '5174')
        scheme = getattr(settings, 'GABTECH_TENANT_URL_SCHEME', 'http')
        return f'{scheme}://{obj.domain}:{port}/login'
