"""
Popula dados de demonstração no tenant (CRM, atendimentos, agenda, documentos, cerimonial).

Uso:
  python manage.py seed_demo --schema=gabinete_demo
  python manage.py seed_demo --schema=gabinete_demo --reset
"""

from __future__ import annotations

import random
from datetime import time, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django_tenants.utils import schema_context

from agenda.models import Espaco, Evento, TipoEvento
from atendimentos.models import Atendimento, Despacho, Macrotema
from cerimonial.models import EventoCerimonial
from core.demo_seed_data import (
    ASSUNTOS_DEMO,
    CIDADAO_NOMES,
    DEMO_ASSUNTO_PREFIX,
    MOGI_PONTOS,
    SEED_MARKER,
    TAGS_DEMO,
)
from core.models import Gabinete
from crm.models import Cidadao, Endereco, Tag
from documentos.models import Documento, PastaDocumento, TipoDocumento
from usuarios.models import User


class Command(BaseCommand):
    help = 'Seed de dados demo (Mogi das Cruzes) para painéis e módulos do SaaS.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            required=True,
            help='Schema PostgreSQL do tenant (ex.: gabinete_demo)',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Remove dados marcados com seed demo antes de recriar',
        )

    def handle(self, *args, **options):
        schema_name = options['schema'].strip().lower()
        reset = options['reset']

        try:
            gabinete = Gabinete.objects.get(schema_name=schema_name)
        except Gabinete.DoesNotExist as exc:
            raise CommandError(f'Tenant/schema "{schema_name}" não encontrado.') from exc

        with schema_context(gabinete.schema_name):
            with transaction.atomic():
                if reset:
                    self._limpar_demo()
                elif self._ja_tem_demo():
                    self.stdout.write(
                        self.style.WARNING(
                            'Seed demo já aplicado. Use --reset para recriar.'
                        )
                    )
                    return

                stats = self._criar_demo()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Seed demo em "{schema_name}": '
                        f'{stats["cidadaos"]} cidadãos, '
                        f'{stats["atendimentos"]} atendimentos, '
                        f'{stats["eventos"]} eventos, '
                        f'{stats["documentos"]} documentos.'
                    )
                )

    def _ja_tem_demo(self) -> bool:
        return Cidadao.objects.filter(observacoes__contains=SEED_MARKER).exists()

    def _limpar_demo(self) -> None:
        from cerimonial.models import ConvidadoEvento
        from crm.models import DocumentoAnexo
        from servicos.models import CandidaturaTalento

        demo_cidadaos = Cidadao.objects.filter(observacoes__contains=SEED_MARKER)
        ids = list(demo_cidadaos.values_list('pk', flat=True))
        if ids:
            Atendimento.objects.filter(cidadao_id__in=ids).delete()
            ConvidadoEvento.objects.filter(cidadao_id__in=ids).delete()
            CandidaturaTalento.objects.filter(candidato_id__in=ids).delete()
            DocumentoAnexo.objects.filter(cidadao_id__in=ids).delete()
            for ev in Evento.objects.filter(convidados__in=demo_cidadaos).distinct():
                ev.convidados.remove(*ids)
        Atendimento.objects.filter(assunto__startswith=DEMO_ASSUNTO_PREFIX).delete()
        for ev in Evento.objects.filter(titulo__startswith=DEMO_ASSUNTO_PREFIX):
            ev.convidados.clear()
            EventoCerimonial.objects.filter(evento_agenda=ev).delete()
            ev.delete()
        Documento.objects.filter(titulo__startswith=DEMO_ASSUNTO_PREFIX).delete()
        demo_cidadaos.delete()
        Tag.objects.filter(nome__in=[t[0] for t in TAGS_DEMO]).delete()

    def _criar_demo(self) -> dict[str, int]:
        random.seed(42)
        agora = timezone.now()

        tags = []
        for nome, cor in TAGS_DEMO:
            tag, _ = Tag.objects.get_or_create(
                nome=nome,
                defaults={'cor': cor, 'tipo': Tag.Tipo.SEGMENTACAO},
            )
            tags.append(tag)

        responsaveis = list(
            User.objects.filter(is_active=True, status=User.Status.ATIVO).order_by('id')
        )
        if not responsaveis:
            raise CommandError('Nenhum usuário ativo no tenant para atribuir atendimentos.')

        macrotemas = list(Macrotema.objects.all())
        if not macrotemas:
            raise CommandError('Macrotemas não encontrados. Rode as migrations do tenant.')

        cidadaos: list[Cidadao] = []
        for idx, nome in enumerate(CIDADAO_NOMES):
            ponto = MOGI_PONTOS[idx % len(MOGI_PONTOS)]
            cidadao = Cidadao.objects.create(
                nome=nome,
                cpf=f'999.{idx + 1:03d}.00-01',
                telefone=f'(11) 9{8000 + idx:04d}-0000',
                email=f'demo.cidadao{idx + 1}@mogi.local',
                observacoes=f'{SEED_MARKER} Cidadão fictício para demonstração.',
            )
            cidadao.marcadores.set(random.sample(tags, k=min(2, len(tags))))
            Endereco.objects.create(
                cidadao=cidadao,
                logradouro=ponto['logradouro'],
                numero=ponto['numero'],
                bairro=ponto['bairro'],
                cidade='Mogi das Cruzes',
                estado='SP',
                cep='08700-000',
                latitude=ponto['lat'],
                longitude=ponto['lng'],
            )
            cidadaos.append(cidadao)

        statuses = [
            Atendimento.Status.ABERTO,
            Atendimento.Status.EM_ANDAMENTO,
            Atendimento.Status.AGUARDANDO_TERCEIROS,
            Atendimento.Status.CONCLUIDO,
        ]
        prioridades = [
            Atendimento.Prioridade.BAIXA,
            Atendimento.Prioridade.MEDIA,
            Atendimento.Prioridade.ALTA,
            Atendimento.Prioridade.URGENTE,
        ]

        atendimentos_criados: list[Atendimento] = []
        for i in range(48):
            cidadao = cidadaos[i % len(cidadaos)]
            macro = macrotemas[i % len(macrotemas)]
            resp = responsaveis[i % len(responsaveis)]
            status = statuses[i % len(statuses)]
            prioridade = prioridades[i % len(prioridades)]
            assunto_base = ASSUNTOS_DEMO[i % len(ASSUNTOS_DEMO)]
            dias_atras = random.randint(1, 45)

            att = Atendimento(
                cidadao=cidadao,
                assunto=f'{DEMO_ASSUNTO_PREFIX}{assunto_base}',
                descricao=f'Demanda registrada em {cidadao.endereco.bairro} para fins de demo.',
                macrotema=macro,
                status=status,
                responsavel=resp,
                prioridade=prioridade,
            )
            att.save()
            created = agora - timedelta(days=dias_atras, hours=random.randint(0, 12))
            updates = {'created_at': created, 'updated_at': created}
            if status != Atendimento.Status.CONCLUIDO:
                if i % 5 == 0:
                    updates['sla_vencimento'] = agora - timedelta(hours=random.randint(2, 72))
                else:
                    updates['sla_vencimento'] = agora + timedelta(hours=random.randint(12, 120))
            else:
                updates['sla_vencimento'] = None
            Atendimento.objects.filter(pk=att.pk).update(**updates)
            att.refresh_from_db()
            atendimentos_criados.append(att)

        autor = responsaveis[0]
        for att in atendimentos_criados[:20]:
            if att.status == Atendimento.Status.CONCLUIDO:
                Despacho.objects.create(
                    atendimento=att,
                    autor=autor,
                    tipo=Despacho.Tipo.MUDANCA_STATUS,
                    conteudo='Encerramento após atendimento presencial.',
                    status_anterior=Atendimento.Status.EM_ANDAMENTO,
                    status_novo=Atendimento.Status.CONCLUIDO,
                )
            elif random.random() < 0.35:
                novo_resp = random.choice(responsaveis)
                Despacho.objects.create(
                    atendimento=att,
                    autor=autor,
                    tipo=Despacho.Tipo.REATRIBUICAO,
                    conteudo='Redistribuição para equipe de campo.',
                    responsavel_anterior=att.responsavel,
                    responsavel_novo=novo_resp,
                )
                Atendimento.objects.filter(pk=att.pk).update(responsavel=novo_resp)
            else:
                Despacho.objects.create(
                    atendimento=att,
                    autor=att.responsavel,
                    tipo=Despacho.Tipo.MUDANCA_STATUS,
                    conteudo='Atualização de status na fila.',
                    status_anterior=Atendimento.Status.ABERTO,
                    status_novo=att.status,
                )

        eventos_count = self._seed_agenda_cerimonial(responsaveis, cidadaos, agora)
        docs_count = self._seed_documentos(responsaveis, agora)

        return {
            'cidadaos': len(cidadaos),
            'atendimentos': len(atendimentos_criados),
            'eventos': eventos_count,
            'documentos': docs_count,
        }

    def _seed_agenda_cerimonial(
        self,
        responsaveis: list[User],
        cidadaos: list[Cidadao],
        agora,
    ) -> int:
        tipo, _ = TipoEvento.objects.get_or_create(
            nome='Audiência pública',
            defaults={'cor': '#ec4899', 'icone': 'megaphone'},
        )
        espaco, _ = Espaco.objects.get_or_create(
            nome='Salão principal',
            defaults={'capacidade': 80, 'cor': '#3b82f6', 'icone': 'building'},
        )
        criador = responsaveis[0]
        titulos = [
            'Audiência — Saúde no bairro',
            'Reunião com lideranças — Zeladoria',
            'Entrega de certificados — Educação',
        ]
        count = 0
        for offset, titulo in enumerate(titulos, start=1):
            data = (agora + timedelta(days=offset * 7)).date()
            ev = Evento.objects.create(
                titulo=f'{DEMO_ASSUNTO_PREFIX}{titulo}',
                descricao='Evento de demonstração vinculado ao cerimonial.',
                data=data,
                hora_inicio=time(14, 0),
                hora_fim=time(16, 0),
                tipo=tipo,
                espaco=espaco,
                criado_por=criador,
            )
            ev.convidados.set(cidadaos[:5])
            EventoCerimonial.objects.get_or_create(
                evento_agenda=ev,
                defaults={'status_logistico': EventoCerimonial.StatusLogistico.PLANEJAMENTO},
            )
            count += 1
        return count

    def _seed_documentos(self, responsaveis: list[User], agora) -> int:
        tipo = TipoDocumento.objects.first()
        pasta = PastaDocumento.objects.first()
        if not tipo:
            return 0
        autor = responsaveis[0]
        titulos = [
            'Ofício ao secretário de saúde',
            'Memorando — mutirão de zeladoria',
            'Requerimento — iluminação pública',
        ]
        count = 0
        for titulo in titulos:
            Documento.objects.create(
                titulo=f'{DEMO_ASSUNTO_PREFIX}{titulo}',
                tipo_documento=tipo,
                pasta=pasta,
                conteudo='<p>Documento gerado automaticamente para demo.</p>',
                autor=autor,
                status=Documento.Status.FINALIZADO,
            )
            count += 1
        return count
