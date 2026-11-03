from rest_framework import serializers

LOGO_MAX_BYTES = 512_000

LOGO_FORMATOS = ('1:1', '1:3', '3:1')
LOGO_FORMATO_PADRAO = '1:1'


def normalizar_logo_formato(value: str | None) -> str:
    if not value or not str(value).strip():
        return LOGO_FORMATO_PADRAO
    fmt = str(value).strip()
    if fmt not in LOGO_FORMATOS:
        raise serializers.ValidationError(
            f'Formato inválido. Use um de: {", ".join(LOGO_FORMATOS)}.',
        )
    return fmt


def validar_logo_data_url(value: str | None) -> str:
    if not value:
        return ''
    trimmed = value.strip()
    if not trimmed:
        return ''
    if not trimmed.startswith('data:image/'):
        raise serializers.ValidationError('Envie uma imagem (PNG, JPG ou WebP).')
    if ';base64,' not in trimmed:
        raise serializers.ValidationError('Formato de imagem inválido.')
    if len(trimmed.encode('utf-8')) > LOGO_MAX_BYTES:
        raise serializers.ValidationError(
            'Imagem muito grande. Reduza o tamanho ou use o recorte (máx. ~500 KB).',
        )
    return trimmed
