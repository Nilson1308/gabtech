from unittest.mock import patch

from django.test import SimpleTestCase

from crm.geocode_service import geocodificar_endereco, normalizar_endereco


class NormalizarEnderecoTests(SimpleTestCase):
    def test_estado_em_maiusculas(self):
        e = normalizar_endereco({'estado': 'sp', 'cep': '01310-100'})
        self.assertEqual(e['estado'], 'SP')
        self.assertEqual(e['cep'], '01310100')


class GeocodificarEnderecoTests(SimpleTestCase):
    @patch('crm.geocode_service._open_meteo_municipio')
    @patch('crm.geocode_service._photon')
    @patch('crm.geocode_service._nominatim')
    def test_fallback_open_meteo(self, mock_nominatim, mock_photon, mock_meteo):
        from crm.geocode_service import GeocodeResult

        mock_nominatim.return_value = None
        mock_photon.return_value = None
        mock_meteo.return_value = GeocodeResult(-23.5505, -46.6333, 'municipio')

        hit = geocodificar_endereco({'cidade': 'São Paulo', 'estado': 'SP'})
        self.assertIsNotNone(hit)
        assert hit is not None
        self.assertEqual(hit.precisao, 'municipio')
        mock_meteo.assert_called_once()

    @patch('crm.geocode_service._nominatim')
    def test_nominatim_estruturado_primeiro(self, mock_nominatim):
        from crm.geocode_service import GeocodeResult

        mock_nominatim.return_value = GeocodeResult(-23.0, -46.0, 'endereco')

        hit = geocodificar_endereco(
            {
                'logradouro': 'Av Paulista',
                'numero': '1000',
                'cidade': 'São Paulo',
                'estado': 'SP',
            }
        )
        self.assertIsNotNone(hit)
        mock_nominatim.assert_called_once()
        self.assertTrue(mock_nominatim.call_args.kwargs.get('structured'))
