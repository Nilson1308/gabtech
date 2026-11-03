import os

MAX_DOCUMENTO_BYTES = 10 * 1024 * 1024

EXTENSOES_PERMITIDAS = {'.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png'}

MIME_PERMITIDOS = {
    'application/pdf',
    'image/jpeg',
    'image/png',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
}


def validar_arquivo_cidadao(arquivo) -> None:
    """Levanta ValidationError se o arquivo violar as regras do CRM."""
    from django.core.exceptions import ValidationError

    if not arquivo:
        raise ValidationError('Nenhum arquivo enviado.')

    tamanho = getattr(arquivo, 'size', None)
    if tamanho is None:
        raise ValidationError('Arquivo inválido.')
    if tamanho > MAX_DOCUMENTO_BYTES:
        raise ValidationError('Arquivo muito grande. Máximo 10MB.')

    nome = getattr(arquivo, 'name', '') or ''
    ext = os.path.splitext(nome)[1].lower()
    if ext not in EXTENSOES_PERMITIDAS:
        raise ValidationError(
            'Tipo de arquivo não permitido. Use PDF, DOC, DOCX, JPG ou PNG.',
        )

    content_type = getattr(arquivo, 'content_type', '') or ''
    if content_type and content_type not in MIME_PERMITIDOS:
        raise ValidationError('Tipo de arquivo não permitido.')
