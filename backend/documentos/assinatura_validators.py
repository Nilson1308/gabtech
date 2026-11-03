from django.core.exceptions import ValidationError

MAX_ASSINATURA_BYTES = 2 * 1024 * 1024
TIPOS_PERMITIDOS = {
    'image/jpeg',
    'image/png',
    'image/webp',
}


def validar_arquivo_assinatura(arquivo) -> None:
    content_type = getattr(arquivo, 'content_type', '') or ''
    if content_type not in TIPOS_PERMITIDOS:
        raise ValidationError('Formato inválido. Use PNG, JPG ou WebP.')

    tamanho = getattr(arquivo, 'size', 0) or 0
    if tamanho > MAX_ASSINATURA_BYTES:
        raise ValidationError('A assinatura deve ter no máximo 2MB.')
