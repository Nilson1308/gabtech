"""Geocodifica em lote endereços CRM (lat/lng) para mapa territorial."""

from __future__ import annotations

import time
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django_tenants.utils import tenant_context

from core.models import Gabinete
from crm.geocode_service import geocodificar_endereco, normalizar_endereco
from crm.models import Endereco


def _coordenada(val: float) -> Decimal:
    return Decimal(str(val)).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)


def _elegivel(end: Endereco) -> bool:
    e = normalizar_endereco(
        {
            'logradouro': end.logradouro,
            'numero': end.numero,
            'bairro': end.bairro,
            'cidade': end.cidade,
            'estado': end.estado,
            'cep': end.cep,
        },
    )
    return bool(e['cidade'] or e['cep'] or (e['logradouro'] and e['bairro']))


class Command(BaseCommand):
    help = (
        'Preenche latitude/longitude dos endereços CRM via geocodificação '
        '(Nominatim → Photon → Open-Meteo). Respeite rate limit com --pausa.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            default='gab_edsonsantos',
            help='schema_name do tenant (padrão: gab_edsonsantos)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular — não grava coordenadas',
        )
        parser.add_argument(
            '--executar',
            action='store_true',
            help='Gravar lat/lng no banco',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Processar no máximo N endereços (teste)',
        )
        parser.add_argument(
            '--pausa',
            type=float,
            default=1.1,
            help='Segundos entre chamadas externas (padrão 1.1 — Nominatim)',
        )
        parser.add_argument(
            '--reprocessar',
            action='store_true',
            help='Incluir endereços que já têm lat/lng',
        )
        parser.add_argument(
            '--cidadao-id',
            type=int,
            default=None,
            help='Geocodificar só este cidadão (ID GabTech)',
        )

    def handle(self, *args, **options):
        executar = options['executar']
        dry_run = options['dry_run'] or not executar
        if executar and options['dry_run']:
            dry_run = False

        schema = options['schema'].strip()
        try:
            gabinete = Gabinete.objects.get(schema_name=schema)
        except Gabinete.DoesNotExist as exc:
            raise CommandError(f'Tenant "{schema}" não encontrado.') from exc

        if dry_run:
            self.stdout.write(self.style.WARNING('Modo dry-run — nenhuma gravação.'))
        else:
            self.stdout.write(self.style.WARNING('Modo EXECUTAR — gravando coordenadas.'))

        pausa = max(0.0, float(options['pausa']))
        stats = Counter()
        erros: list[str] = []

        with tenant_context(gabinete):
            qs = Endereco.objects.select_related('cidadao').order_by('pk')
            if not options['reprocessar']:
                qs = qs.filter(Q(latitude__isnull=True) | Q(longitude__isnull=True))
            if options['cidadao_id']:
                qs = qs.filter(cidadao_id=options['cidadao_id'])

            total_candidatos = qs.count()
            sem_dados = 0
            processados = 0

            for end in qs.iterator(chunk_size=200):
                if options['limit'] is not None and processados >= options['limit']:
                    break
                if not _elegivel(end):
                    sem_dados += 1
                    stats['pulados_sem_endereco'] += 1
                    continue

                payload = {
                    'logradouro': end.logradouro,
                    'numero': end.numero,
                    'bairro': end.bairro,
                    'cidade': end.cidade,
                    'estado': end.estado,
                    'cep': end.cep,
                }

                if dry_run:
                    stats['simulados'] += 1
                    processados += 1
                    continue

                try:
                    resultado = geocodificar_endereco(payload)
                except Exception as exc:
                    stats['falhas'] += 1
                    if len(erros) < 15:
                        erros.append(f'cidadao {end.cidadao_id}: {exc}')
                    if pausa:
                        time.sleep(pausa)
                    continue

                if resultado is None:
                    stats['sem_resultado'] += 1
                    if len(erros) < 15:
                        erros.append(
                            f'cidadao {end.cidadao_id}: sem resultado '
                            f'({end.bairro}, {end.cidade})',
                        )
                else:
                    end.latitude = _coordenada(resultado.latitude)
                    end.longitude = _coordenada(resultado.longitude)
                    end.save(update_fields=['latitude', 'longitude'])
                    stats[resultado.precisao] += 1
                    stats['gravados'] += 1

                processados += 1
                if pausa:
                    time.sleep(pausa)

        modo = 'DRY-RUN' if dry_run else 'EXECUTADO'
        self.stdout.write(
            self.style.SUCCESS(
                f'[{modo}] candidatos={total_candidatos} processados={processados} '
                f'pulados_sem_endereco={sem_dados} gravados={stats.get("gravados", 0)} '
                f'sem_resultado={stats.get("sem_resultado", 0)} falhas={stats.get("falhas", 0)} '
                f'precisao_endereco={stats.get("endereco", 0)} '
                f'precisao_bairro={stats.get("bairro", 0)} '
                f'precisao_municipio={stats.get("municipio", 0)}',
            ),
        )
        for msg in erros:
            self.stdout.write(self.style.ERROR(msg))
        if dry_run and processados:
            est_min = (processados * pausa) / 60
            self.stdout.write(
                f'Estimativa em --executar (só pausa): ~{est_min:.0f} min para {processados} registros.',
            )
        if not dry_run and stats.get('gravados'):
            self.stdout.write(
                self.style.SUCCESS(
                    'Mapa territorial passará a exibir pins conforme permissões de analytics.',
                ),
            )
