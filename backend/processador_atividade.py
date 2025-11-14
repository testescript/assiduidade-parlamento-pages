import json
from datetime import datetime
from pathlib import Path

from models import (
    AgendaItem,
    Deputado,
    DeputadoAtividade,
    get_engine_and_session,
)
from utils import normalizar_nome

ACTIVITY_MAPPING = {
    "Ini": "Iniciativas",
    "Intev": "Intervenções",
    "Req": "Requerimentos",
    "Audicoes": "Audições",
    "Audiencias": "Audiências",
    "ActP": "Atos Parlamentares",
    "Cms": "Comissões",
}


def parse_date(date_str: str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%d/%m/%Y").date()
    except ValueError:
        return None


def build_datetime(date_str: str, time_str: str):
    if not date_str:
        return None
    date_part = parse_date(date_str)
    if not date_part:
        return None
    if not time_str:
        return datetime.combine(date_part, datetime.min.time())
    try:
        time_part = datetime.strptime(time_str, "%H:%M:%S").time()
        return datetime.combine(date_part, time_part)
    except ValueError:
        return datetime.combine(date_part, datetime.min.time())


def _get_or_create_deputado(session, nome_normalizado: str, nome_original: str, partido: str | None):
    deputado = session.query(Deputado).filter_by(nome_normalizado=nome_normalizado).first()
    if deputado:
        deputado.partido_atual = partido or deputado.partido_atual
        deputado.nome_original_ultimo = nome_original or deputado.nome_original_ultimo
        return deputado
    deputado = Deputado(
        nome_normalizado=nome_normalizado,
        nome_original_ultimo=nome_original,
        partido_atual=partido,
    )
    session.add(deputado)
    session.flush()
    return deputado


def _detalhes_limit(lista: list) -> str:
    if not lista:
        return ""
    nomes = []
    for item in lista[:3]:
        if isinstance(item, dict):
            titulo = item.get("IniTi") or item.get("IntSu") or item.get("ActTpdesc") or item.get("Titulo")
            if titulo:
                nomes.append(titulo)
    return "; ".join([s for s in nomes if s])


def process_atividade(path: Path, session):
    payload = json.loads(path.read_text())
    for entry in payload:
        deputado_meta = entry.get("Deputado") or {}
        nome = deputado_meta.get("DepNomeParlamentar") or deputado_meta.get("DepNomeCompleto")
        if not nome:
            continue
        nome_norm = normalizar_nome(nome)
        if not nome_norm:
            continue
        partido = None
        gp = deputado_meta.get("DepGP")
        if isinstance(gp, list) and gp:
            partido = gp[0].get("GpSigla")
        legislatura = deputado_meta.get("LegDes")
        deputado = _get_or_create_deputado(session, nome_norm, nome, partido)

        atividades = entry.get("AtividadeDeputadoList") or []
        for atividade in atividades:
            for campo, tipo in ACTIVITY_MAPPING.items():
                itens = atividade.get(campo)
                if itens is None:
                    continue
                if isinstance(itens, list):
                    total = len(itens)
                elif isinstance(itens, dict):
                    total = 1
                else:
                    continue
                registro = (
                    session.query(DeputadoAtividade)
                    .filter_by(deputado_id=deputado.id, tipo=tipo, legislatura=legislatura)
                    .first()
                )
                if registro is None:
                    registro = DeputadoAtividade(
                        deputado_id=deputado.id,
                        tipo=tipo,
                        legislatura=legislatura,
                        total=total,
                        detalhes=_detalhes_limit(itens),
                    )
                    session.add(registro)
                else:
                    registro.total = total
                    registro.detalhes = _detalhes_limit(itens)


def process_agenda(path: Path, session):
    payload = json.loads(path.read_text())
    for entry in payload:
        externo_id = entry.get("Id")
        if externo_id is None:
            continue
        agenda = session.query(AgendaItem).filter_by(externo_id=externo_id).first()
        if agenda is None:
            agenda = AgendaItem(externo_id=externo_id)
            session.add(agenda)
        agenda.titulo = entry.get("Title") or agenda.titulo
        agenda.tema = entry.get("Theme")
        agenda.secao = entry.get("Section")
        agenda.local = entry.get("Local")
        agenda.organizacao = entry.get("OrgDes")
        agenda.leg_des = entry.get("LegDes")
        agenda.parlamentar_group = str(entry.get("ParlamentGroup")) if entry.get("ParlamentGroup") is not None else None
        agenda.link = entry.get("Link")
        agenda.texto = entry.get("InternetText")
        agenda.inicio = build_datetime(entry.get("EventStartDate"), entry.get("EventStartTime"))
        agenda.fim = build_datetime(entry.get("EventEndDate"), entry.get("EventEndTime"))


def main():
    engine, SessionLocal = get_engine_and_session()
    session = SessionLocal()
    try:
        atividade_path = Path("uploads/AtividadeDeputadoXVII.json")
        if atividade_path.exists():
            process_atividade(atividade_path, session)
        agenda_path = Path("uploads/AgendaParlamentar.json")
        if agenda_path.exists():
            process_agenda(agenda_path, session)
        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    main()
