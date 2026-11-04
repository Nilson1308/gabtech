from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count

from atendimentos.models import Atendimento, Despacho
from core.legado.atendimento_edsons79 import iter_atendimentos
from core.legado.cadastro_edsons79 import ler_sql
from core.legado.config_edsonsantos import MigracaoConfig
from core.legado.usuarios_edsons79 import UsuarioLegado, iter_usuarios
from crm.models import MigracaoLegadoRef
from usuarios.models import Perfil

User = get_user_model()

TIPO_USUARIO = 'usuario_legado'
MARCADOR_DESPACHO_LEGADO = 'Importado do sistema legado'


def _slug_email_local(login: str) -> str:
    raw = (login or '').strip().lower()
    normalized = unicodedata.normalize('NFKD', raw)
    ascii_only = normalized.encode('ascii', 'ignore').decode('ascii')
    local = re.sub(r'[^a-z0-9]+', '.', ascii_only).strip('.')
    return local or 'usuario'


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


@dataclass
class ResultadoProvisionamentoUsuarios:
    usuarios_legado_total: int = 0
    elegiveis_criacao: int = 0
    criados: int = 0
    ja_existiam: int = 0
    vinculados_admin: int = 0
    ignorados: int = 0
    atendimentos_reatribuir: int = 0
    atendimentos_atualizados: int = 0
    despachos_legado_atualizados: int = 0
    sem_usuario_mapeado: int = 0
    por_v_usu: dict[int, int] = field(default_factory=dict)
    plano: list[dict[str, Any]] = field(default_factory=list)
    erros: list[str] = field(default_factory=list)
    dry_run: bool = True

    def resumo(self) -> str:
        modo = 'DRY-RUN' if self.dry_run else 'EXECUTADO'
        return (
            f'[{modo}] legado={self.usuarios_legado_total} elegíveis={self.elegiveis_criacao} '
            f'criados={self.criados} existiam={self.ja_existiam} admin_legado={self.vinculados_admin} '
            f'ignorados={self.ignorados} | atendimentos reatrib={self.atendimentos_atualizados}/'
            f'{self.atendimentos_reatribuir} despachos={self.despachos_legado_atualizados} '
            f'sem_mapa={self.sem_usuario_mapeado} erros={len(self.erros)}'
        )


def _cfg_provisionamento(config: MigracaoConfig) -> dict[str, Any]:
    raw = config.raw.get('usuarios_legado', {}).get('provisionamento', {})
    return raw if isinstance(raw, dict) else {}


def _email_para_legado(
    config: MigracaoConfig,
    u: UsuarioLegado,
    dominio: str,
) -> str:
    override = config.mapa_usuarios_legado.get(str(u.legacy_id))
    if override and str(override).strip():
        return str(override).strip().lower()
    local = _slug_email_local(u.login)
    return f'{local}@{dominio}'.lower()


def _ids_com_atendimentos(sql_text: str) -> set[int]:
    return {row.v_usu for row in iter_atendimentos(sql_text)}


def _carregar_refs_usuario_legado() -> dict[int, User]:
    out: dict[int, User] = {}
    for ref in MigracaoLegadoRef.objects.filter(tipo=TIPO_USUARIO):
        user = User.objects.filter(pk=ref.gabtech_id).first()
        if user:
            out[ref.legacy_id] = user
    return out


def _mapa_legado_para_user(
    config: MigracaoConfig,
    usuarios: list[UsuarioLegado],
    *,
    ids_atendimento: set[int],
    dry_run: bool,
    senha: str | None,
) -> tuple[dict[int, User], set[int], ResultadoProvisionamentoUsuarios]:
    res = ResultadoProvisionamentoUsuarios(dry_run=dry_run)
    prov = _cfg_provisionamento(config)
    dominio = str(prov.get('email_dominio', 'legado.local')).strip()
    perfil_nome = str(prov.get('perfil_nome', 'Assessor Parlamentar')).strip()
    apenas_at = bool(prov.get('apenas_com_atendimentos', True))
    admin_legado_id = int(prov.get('vincular_admin_legado_id', 1))
    stts_inativo = {int(x) for x in prov.get('stts_inativo_no_legado', [1])}
    ignorar_ids = {int(x) for x in prov.get('ignorar_ids', [12])}

    perfil = Perfil.objects.filter(nome=perfil_nome).first()
    if perfil is None:
        res.erros.append(f'Perfil não encontrado: {perfil_nome}')

    admin_user = User.objects.filter(email__iexact=config.default_responsavel_email).first()
    if admin_user is None:
        res.erros.append(f'Responsável padrão não encontrado: {config.default_responsavel_email}')

    mapa: dict[int, User] = dict(_carregar_refs_usuario_legado())
    v_usu_cobertos: set[int] = set(mapa.keys())
    res.usuarios_legado_total = len(usuarios)

    for u in usuarios:
        if u.legacy_id in ignorar_ids:
            res.ignorados += 1
            continue
        if apenas_at and u.legacy_id not in ids_atendimento:
            res.ignorados += 1
            continue

        if u.legacy_id in mapa:
            res.ja_existiam += 1
            v_usu_cobertos.add(u.legacy_id)
            continue

        email = _email_para_legado(config, u, dominio)

        if u.legacy_id == admin_legado_id:
            if admin_user:
                mapa[u.legacy_id] = admin_user
                v_usu_cobertos.add(u.legacy_id)
                res.vinculados_admin += 1
                res.plano.append(
                    {
                        'legacy_id': u.legacy_id,
                        'login': u.login,
                        'email': admin_user.email,
                        'acao': 'vincular_admin_existente',
                    },
                )
            continue

        existente = User.objects.filter(email__iexact=email).first()
        if existente:
            mapa[u.legacy_id] = existente
            v_usu_cobertos.add(u.legacy_id)
            res.ja_existiam += 1
            res.plano.append(
                {
                    'legacy_id': u.legacy_id,
                    'login': u.login,
                    'email': email,
                    'acao': 'usar_existente',
                    'status': existente.status,
                },
            )
            if not dry_run:
                MigracaoLegadoRef.objects.update_or_create(
                    tipo=TIPO_USUARIO,
                    legacy_id=u.legacy_id,
                    defaults={
                        'gabtech_id': existente.pk,
                        'meta': {'login': u.login, 'stts': u.stts},
                    },
                )
            continue

        res.elegiveis_criacao += 1
        status = User.Status.INATIVO if u.stts in stts_inativo else User.Status.ATIVO
        res.plano.append(
            {
                'legacy_id': u.legacy_id,
                'login': u.login,
                'email': email,
                'acao': 'criar',
                'status': status,
                'perfil': perfil_nome,
            },
        )
        v_usu_cobertos.add(u.legacy_id)

        if dry_run:
            continue

        if perfil is None or not senha:
            continue

        username = _username_disponivel(_slug_email_local(u.login).replace('.', '_'))
        user = User(
            username=username,
            email=email,
            perfil=perfil,
            status=status,
        )
        _aplicar_nome(user, u.login)
        _sincronizar_status_ativo(user)
        user.set_password(senha)
        user.save()
        MigracaoLegadoRef.objects.update_or_create(
            tipo=TIPO_USUARIO,
            legacy_id=u.legacy_id,
            defaults={'gabtech_id': user.pk, 'meta': {'login': u.login, 'stts': u.stts}},
        )
        mapa[u.legacy_id] = user
        res.criados += 1

    return mapa, v_usu_cobertos, res


def reatribuir_atendimentos_por_v_usu(
    mapa: dict[int, User],
    v_usu_cobertos: set[int],
    *,
    dry_run: bool,
) -> tuple[int, int, int, int]:
    total = 0
    atualizados = 0
    despachos = 0
    sem_mapa = 0

    refs = MigracaoLegadoRef.objects.filter(tipo=MigracaoLegadoRef.Tipo.ATENDIMENTO).only(
        'gabtech_id',
        'meta',
    )

    for ref in refs.iterator(chunk_size=500):
        v_usu = ref.meta.get('v_usu') if ref.meta else None
        if v_usu is None:
            continue
        try:
            v_int = int(v_usu)
        except (TypeError, ValueError):
            continue

        total += 1
        if v_int not in v_usu_cobertos:
            sem_mapa += 1
            continue

        user = mapa.get(v_int)

        if dry_run:
            if user is None:
                atualizados += 1
            elif not Atendimento.objects.filter(pk=ref.gabtech_id, responsavel_id=user.pk).exists():
                atualizados += 1
            continue

        if user is None:
            sem_mapa += 1
            continue

        mudou = Atendimento.objects.filter(pk=ref.gabtech_id).exclude(responsavel_id=user.pk).update(
            responsavel_id=user.pk,
        )
        if mudou:
            atualizados += mudou

        despachos += (
            Despacho.objects.filter(
                atendimento_id=ref.gabtech_id,
                conteudo__startswith=MARCADOR_DESPACHO_LEGADO,
            )
            .exclude(autor_id=user.pk)
            .update(autor_id=user.pk)
        )

    return total, atualizados, despachos, sem_mapa


def executar_provisionamento_usuarios_legado(
    config: MigracaoConfig,
    *,
    dry_run: bool = True,
    senha: str | None = None,
) -> ResultadoProvisionamentoUsuarios:
    if not dry_run and (not senha or not str(senha).strip()):
        res = ResultadoProvisionamentoUsuarios(dry_run=dry_run)
        res.erros.append('Informe --senha para --executar (senha inicial dos usuários legados).')
        return res

    sql_text = ler_sql(config.sql_path)
    usuarios = iter_usuarios(sql_text)
    ids_at = _ids_com_atendimentos(sql_text)

    from collections import Counter

    c: Counter[int] = Counter()
    for ref in MigracaoLegadoRef.objects.filter(tipo=MigracaoLegadoRef.Tipo.ATENDIMENTO).iterator(
        chunk_size=500,
    ):
        v = ref.meta.get('v_usu') if ref.meta else None
        if v is not None:
            try:
                c[int(v)] += 1
            except (TypeError, ValueError):
                pass

    sid = transaction.savepoint()
    mapa, v_usu_cobertos, res = _mapa_legado_para_user(
        config,
        usuarios,
        ids_atendimento=ids_at,
        dry_run=dry_run,
        senha=str(senha).strip() if senha else None,
    )
    res.por_v_usu = dict(c)

    if res.erros and not dry_run:
        transaction.savepoint_rollback(sid)
        return res

    total, att, desp, sem = reatribuir_atendimentos_por_v_usu(
        mapa,
        v_usu_cobertos,
        dry_run=dry_run,
    )
    res.atendimentos_reatribuir = total
    res.atendimentos_atualizados = att
    res.despachos_legado_atualizados = desp
    res.sem_usuario_mapeado = sem

    if dry_run:
        transaction.savepoint_rollback(sid)
    else:
        transaction.savepoint_commit(sid)

    return res


def resumo_distribuicao_responsaveis() -> list[dict[str, Any]]:
    return list(
        Atendimento.objects.values('responsavel__email', 'responsavel__first_name')
        .annotate(n=Count('id'))
        .order_by('-n'),
    )
