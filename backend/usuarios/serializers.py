from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from auditoria.mixins import RastreabilidadeModelSerializer

from usuarios.models import Perfil, Permissao
from usuarios.rbac_utils import vincular_perfil_administrador

User = get_user_model()


class PerfilBasicoSerializer(RastreabilidadeModelSerializer):
    """Dados mínimos do perfil para listagens de usuários."""

    class Meta:
        model = Perfil
        fields = ('id', 'nome', 'cor', 'is_admin')
        rastreabilidade_habilitada = False


class PerfilSerializer(RastreabilidadeModelSerializer):
    """Perfis RBAC — leitura e escrita (permissoes = lista de codenames)."""

    permissoes = serializers.SlugRelatedField(
        many=True,
        slug_field='codename',
        queryset=Permissao.objects.all(),
    )

    class Meta:
        model = Perfil
        fields = (
            'id',
            'nome',
            'cor',
            'icone',
            'descricao',
            'is_admin',
            'permissoes',
            'created_at',
        )
        read_only_fields = ('id', 'is_admin', 'created_at')

    def validate_nome(self, value: str) -> str:
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError('Informe o nome do perfil.')
        return value

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)
        if instance and instance.is_admin:
            bloqueados = {'permissoes', 'nome', 'cor', 'icone', 'descricao'}
            if bloqueados.intersection(attrs.keys()):
                raise serializers.ValidationError(
                    'O perfil Administrador é protegido e não pode ser alterado pela API.',
                )
        return attrs

    def create(self, validated_data):
        validated_data['is_admin'] = False
        return super().create(validated_data)


def _username_disponivel(base: str) -> str:
    candidato = base[:150]
    if not User.objects.filter(username=candidato).exists():
        return candidato
    raiz = base[:140]
    sufixo = 1
    while True:
        candidato = f'{raiz}_{sufixo}'[:150]
        if not User.objects.filter(username=candidato).exists():
            return candidato
        sufixo += 1


def _aplicar_nome(user: User, nome: str) -> None:
    nome = (nome or '').strip()
    partes = nome.split(None, 1)
    user.first_name = partes[0] if partes else ''
    user.last_name = partes[1] if len(partes) > 1 else ''


def _sincronizar_status_ativo(user: User) -> None:
    user.is_active = user.status == User.Status.ATIVO


class UsuarioSerializer(RastreabilidadeModelSerializer):
    nome = serializers.CharField(max_length=300)
    cargo = serializers.CharField(read_only=True)
    perfil = PerfilBasicoSerializer(read_only=True)
    perfil_id = serializers.PrimaryKeyRelatedField(
        queryset=Perfil.objects.all(),
        source='perfil',
        write_only=True,
        required=True,
    )
    password = serializers.CharField(
        write_only=True,
        required=False,
        trim_whitespace=False,
        style={'input_type': 'password'},
    )
    created_at = serializers.DateTimeField(source='date_joined', read_only=True)
    updated_at = serializers.DateTimeField(source='last_login', read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'nome',
            'email',
            'avatar',
            'cargo',
            'status',
            'perfil',
            'perfil_id',
            'password',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'cargo', 'perfil', 'created_at', 'updated_at')
        extra_kwargs = {
            'email': {'required': True},
        }

    def validate_email(self, value: str) -> str:
        email = value.strip().lower()
        qs = User.objects.filter(email__iexact=email)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Já existe um usuário com este e-mail.')
        return email

    def validate(self, attrs):
        if self.instance is None and not attrs.get('password'):
            raise serializers.ValidationError({'password': 'Senha obrigatória para novo usuário.'})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        nome = validated_data.pop('nome', '')
        email = validated_data['email']
        username = _username_disponivel(email.split('@')[0].replace('.', '_') or 'usuario')

        user = User(
            username=username,
            email=email,
            avatar=validated_data.get('avatar', ''),
            status=validated_data.get('status', User.Status.ATIVO),
            perfil=validated_data.get('perfil'),
        )
        _aplicar_nome(user, nome)
        user.set_password(password)
        _sincronizar_status_ativo(user)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        nome = validated_data.pop('nome', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if nome is not None:
            _aplicar_nome(instance, nome)

        if password:
            instance.set_password(password)

        _sincronizar_status_ativo(instance)
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    """Contrato de entrada alinhado ao Pinia (email + senha)."""

    email = serializers.EmailField()
    senha = serializers.CharField(write_only=True, trim_whitespace=False)

    default_error_messages = {
        'invalid_credentials': 'Credenciais inválidas.',
        'inactive_user': 'Usuário inativo ou sem permissão de acesso.',
    }

    def validate(self, attrs):
        email = attrs['email'].strip().lower()
        senha = attrs['senha']

        user = (
            User.objects.select_related('perfil')
            .filter(email__iexact=email)
            .first()
        )

        if user is None or not user.check_password(senha):
            self.fail('invalid_credentials')

        if not user.is_active or user.status != User.Status.ATIVO:
            self.fail('inactive_user')

        if user.is_superuser:
            vincular_perfil_administrador(user)
            user.refresh_from_db(fields=['perfil'])

        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data['user']
        refresh = RefreshToken.for_user(user)
        return {
            'token': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user,
        }


class AuthUserSerializer(RastreabilidadeModelSerializer):
    """Payload de usuário injetado na authStore do frontend."""

    nome = serializers.CharField(read_only=True)
    cargo = serializers.CharField(read_only=True)
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'nome', 'email', 'avatar', 'cargo', 'permissions')
        rastreabilidade_habilitada = False

    def get_permissions(self, obj: User) -> list[str]:
        return obj.get_permissao_codenames()


class LoginResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    user = AuthUserSerializer()
