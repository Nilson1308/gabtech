from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase

from crm.documento_validators import MAX_DOCUMENTO_BYTES, validar_arquivo_cidadao


class ValidarArquivoCidadaoTests(SimpleTestCase):
    def test_pdf_valido(self):
        arquivo = SimpleUploadedFile('rg.pdf', b'%PDF-1.4', content_type='application/pdf')
        validar_arquivo_cidadao(arquivo)

    def test_extensao_invalida(self):
        arquivo = SimpleUploadedFile('virus.exe', b'x', content_type='application/octet-stream')
        with self.assertRaises(ValidationError):
            validar_arquivo_cidadao(arquivo)

    def test_tamanho_maximo(self):
        arquivo = SimpleUploadedFile(
            'grande.pdf',
            b'0' * (MAX_DOCUMENTO_BYTES + 1),
            content_type='application/pdf',
        )
        with self.assertRaises(ValidationError):
            validar_arquivo_cidadao(arquivo)
