from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, case
from datetime import datetime
# Imports absolutos (sem o ".")
from processador import validar_e_preparar
from processador_atividade import process_atividade, process_agenda
from models import (
    get_engine_and_session,
    Deputado,
    Sessao,
    Assiduidade,
    DeputadoAtividade,
    AgendaItem,
)

app = Flask(__name__)
CORS(app)


def parse_iso_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"ok": False, "mensagem": "Ficheiro não enviado."}), 400
    file = request.files["file"]
    
    # Verificar se o utilizador quer substituir uma sessão existente
    substituir = request.form.get("substituir", "false").lower() == "true"

    # Fluxo alternativo: permitir upload de JSON (Atividade/Agenda) pelo mesmo endpoint
    filename = getattr(file, "filename", "") or ""
    if filename.lower().endswith(".json"):
        try:
            from pathlib import Path
            import json
            uploads_dir = Path(__file__).resolve().parent.parent / "uploads"
            uploads_dir.mkdir(parents=True, exist_ok=True)
            destino = uploads_dir / filename
            file.save(str(destino))

            # Inspecionar para decidir o processador
            with destino.open() as fh:
                payload = json.load(fh)
            if isinstance(payload, list) and payload:
                item0 = payload[0]
                engine, SessionLocal = get_engine_and_session()
                s = SessionLocal()
                try:
                    if isinstance(item0, dict) and "AtividadeDeputadoList" in item0 and "Deputado" in item0:
                        process_atividade(destino, s)
                        s.commit()
                        total = len(payload)
                        return jsonify({
                            "ok": True,
                            "mensagem": f"Atividade carregada com sucesso ({total} deputados).",
                            "tipo": "atividade",
                            "ficheiro": filename
                        })
                    elif isinstance(item0, dict) and "EventStartDate" in item0 and "Title" in item0:
                        process_agenda(destino, s)
                        s.commit()
                        total = len(payload)
                        return jsonify({
                            "ok": True,
                            "mensagem": f"Agenda carregada com sucesso ({total} eventos).",
                            "tipo": "agenda",
                            "ficheiro": filename
                        })
                finally:
                    s.close()
            return jsonify({"ok": False, "mensagem": "JSON não reconhecido (esperado Atividade ou Agenda)."}), 400
        except Exception as e:
            return jsonify({"ok": False, "mensagem": f"Erro a processar JSON: {e}"}), 500

    resultado = validar_e_preparar(file)
    if not resultado["ok"]:
        return jsonify(resultado), 400

    sessao_meta = resultado["sessao"]
    registos = resultado["registos"]

    _, SessionLocal = get_engine_and_session()
    s = SessionLocal()
    try:
        # Verifica se a sessão já existe
        sessao_existente = s.query(Sessao).filter_by(id_legis_sessao=sessao_meta["id_legis_sessao"]).first()
        
        if sessao_existente and not substituir:
            # Retorna 409 indicando conflito e que precisa de confirmação
            return jsonify({
                "ok": False,
                "mensagem": f"Sessão {sessao_meta['id_legis_sessao']} já foi carregada anteriormente.",
                "sessao": sessao_meta,
                "requer_confirmacao": True
            }), 409
        
        if sessao_existente and substituir:
            # Apagar registos de assiduidade da sessão existente
            s.query(Assiduidade).filter_by(sessao_id=sessao_existente.id).delete()
            # Apagar a sessão
            s.delete(sessao_existente)
            s.flush()

        # Criar nova sessão (ou recriar se substituiu)
        sessao = Sessao(
            id_legis_sessao=sessao_meta["id_legis_sessao"],
            legislatura=sessao_meta["legislatura"],
            numero=str(sessao_meta["numero"]),
            tipo=sessao_meta["tipo"],
            data=sessao_meta["data"]
        )
        s.add(sessao)
        s.flush()

        inseridos = 0
        novos_deputados = 0
        duplicados = 0

        for r in registos:
            dep = s.query(Deputado).filter_by(nome_normalizado=r["deputado_normalizado"]).first()
            if not dep:
                dep = Deputado(
                    nome_normalizado=r["deputado_normalizado"],
                    nome_original_ultimo=r["deputado_original"],
                    partido_atual=r["partido"]
                )
                s.add(dep)
                s.flush()
                novos_deputados += 1
            else:
                dep.nome_original_ultimo = r["deputado_original"]
                dep.partido_atual = r["partido"]

            reg = Assiduidade(
                sessao_id=sessao.id,
                deputado_id=dep.id,
                partido=r["partido"],
                status=r["status"],
                motivo=r["motivo"]
            )
            s.add(reg)
            try:
                s.flush()
                inseridos += 1
            except IntegrityError:
                s.rollback()
                duplicados += 1

        s.commit()
        return jsonify({
            "ok": True,
            "mensagem": "Sessão substituída com sucesso." if substituir else "Sessão inserida com sucesso.",
            "sessao": sessao_meta,
            "inseridos": inseridos,
            "novos_deputados": novos_deputados,
            "duplicados_ignorados": duplicados,
            "resumo": resultado["resumo"],
            "substituiu": substituir
        })
    except Exception as e:
        s.rollback()
        return jsonify({"ok": False, "mensagem": f"Erro ao inserir na base: {e}"}), 500
    finally:
        s.close()

@app.route("/deputados", methods=["GET"])
def listar_deputados():
    _, SessionLocal = get_engine_and_session()
    s = SessionLocal()
    try:
        legislatura = request.args.get("legislatura")

        presencas_expr = func.sum(case((Assiduidade.status.like("Presença%"), 1), else_=0))
        faltas_just_expr = func.sum(case((Assiduidade.status.like("Falta Justificada%"), 1), else_=0))
        amp_expr = func.sum(case((Assiduidade.status.like("Ausência em Missão Parlamentar%"), 1), else_=0))
        faltas_quorum_expr = func.sum(case((Assiduidade.status.like("Falta ao Quórum de Votação%"), 1), else_=0))

        query = (
            s.query(
                Deputado.nome_original_ultimo.label("nome"),
                Deputado.partido_atual.label("partido"),
                presencas_expr.label("presencas"),
                faltas_just_expr.label("faltas_justificadas"),
                amp_expr.label("missao_parlamentar_amp"),
                faltas_quorum_expr.label("faltas_penalizadoras")
            )
            .join(Assiduidade, Assiduidade.deputado_id == Deputado.id)
        )

        if legislatura:
            query = query.join(Sessao, Sessao.id == Assiduidade.sessao_id).filter(Sessao.legislatura == legislatura)

        query = query.group_by(Deputado.id, Deputado.nome_original_ultimo, Deputado.partido_atual)

        dados = []
        for reg in query.all():
            presencas = reg.presencas or 0
            faltas_penalizadoras = reg.faltas_penalizadoras or 0
            denom = presencas + faltas_penalizadoras
            assiduidade_pct = (presencas / denom * 100) if denom else 0.0

            dados.append({
                "nome": reg.nome,
                "partido": reg.partido,
                "presencas": presencas,
                "faltas_justificadas": reg.faltas_justificadas or 0,
                "missao_parlamentar_amp": reg.missao_parlamentar_amp or 0,
                "faltas_penalizadoras": faltas_penalizadoras,
                "assiduidade_pct": round(assiduidade_pct, 2)
            })

        return jsonify({"ok": True, "deputados": dados})
    finally:
        s.close()


@app.route("/atividade/deputados", methods=["GET"])
def atividade_deputados():
    _, SessionLocal = get_engine_and_session()
    s = SessionLocal()
    try:
        legislatura = request.args.get("legislatura")
        tipo = request.args.get("tipo")
        partido = request.args.get("partido")

        query = s.query(DeputadoAtividade, Deputado).join(Deputado, DeputadoAtividade.deputado_id == Deputado.id)
        if legislatura:
            query = query.filter(DeputadoAtividade.legislatura == legislatura)
        if tipo:
            query = query.filter(DeputadoAtividade.tipo == tipo)
        if partido:
            query = query.filter(Deputado.partido_atual == partido)

        registros = query.order_by(DeputadoAtividade.total.desc()).all()
        dados = []
        for atividade, dep in registros:
            dados.append({
                "deputado": dep.nome_original_ultimo,
                "partido": dep.partido_atual,
                "tipo": atividade.tipo,
                "total": atividade.total,
                "legislatura": atividade.legislatura,
                "detalhes": atividade.detalhes or "",
                "ultima_data": atividade.ultima_data.isoformat() if atividade.ultima_data else None,
            })

        return jsonify({"ok": True, "registos": dados})
    finally:
        s.close()


@app.route("/atividade/agenda", methods=["GET"])
def atividade_agenda():
    _, SessionLocal = get_engine_and_session()
    s = SessionLocal()
    try:
        legislatura = request.args.get("legislatura")
        section = request.args.get("section")
        theme = request.args.get("theme")
        data_inicio = parse_iso_date(request.args.get("data_inicio"))
        data_fim = parse_iso_date(request.args.get("data_fim"))

        query = s.query(AgendaItem)
        if legislatura:
            query = query.filter(AgendaItem.leg_des == legislatura)
        if section:
            query = query.filter(AgendaItem.secao == section)
        if theme:
            query = query.filter(AgendaItem.tema == theme)
        if data_inicio:
            query = query.filter(AgendaItem.inicio >= data_inicio)
        if data_fim:
            query = query.filter(AgendaItem.inicio <= data_fim)

        items = query.order_by(AgendaItem.inicio.asc().nullslast()).limit(50).all()
        dados = []
        for item in items:
            dados.append({
                "titulo": item.titulo,
                "tema": item.tema,
                "secao": item.secao,
                "local": item.local,
                "legislatura": item.leg_des,
                "inicio": item.inicio.isoformat() if item.inicio else None,
                "fim": item.fim.isoformat() if item.fim else None,
                "link": item.link,
                "texto": item.texto,
            })

        return jsonify({"ok": True, "agenda": dados})
    finally:
        s.close()

@app.route("/deputados/filtrados", methods=["GET"])
def listar_deputados_filtrados():
    """Retorna estatísticas de deputados filtradas por legislatura/sessões"""
    _, SessionLocal = get_engine_and_session()
    s = SessionLocal()
    try:
        legislatura = request.args.get("legislatura", "")
        tipo_sessao = request.args.get("tipo") or request.args.get("tipo_sessao") or ""
        data_inicio = parse_iso_date(request.args.get("data_inicio"))
        data_fim = parse_iso_date(request.args.get("data_fim"))
        
        # Construir query base de sessões
        query_sessoes = s.query(Sessao)
        if legislatura:
            query_sessoes = query_sessoes.filter(Sessao.legislatura == legislatura)
        if data_inicio:
            query_sessoes = query_sessoes.filter(Sessao.data >= data_inicio)
        if data_fim:
            query_sessoes = query_sessoes.filter(Sessao.data <= data_fim)
        if tipo_sessao:
            query_sessoes = query_sessoes.filter(Sessao.tipo == tipo_sessao)
        
        sessoes_ids = [sess.id for sess in query_sessoes.all()]
        
        if not sessoes_ids:
            return jsonify({"ok": True, "deputados": []})
        
        dados = []
        for dep in s.query(Deputado).all():
            presencas = s.query(Assiduidade).filter(
                Assiduidade.deputado_id == dep.id,
                Assiduidade.sessao_id.in_(sessoes_ids),
                Assiduidade.status.like("Presença%")
            ).count()

            faltas_j = s.query(Assiduidade).filter(
                Assiduidade.deputado_id == dep.id,
                Assiduidade.sessao_id.in_(sessoes_ids),
                Assiduidade.status.like("Falta Justificada%")
            ).count()

            amp = s.query(Assiduidade).filter(
                Assiduidade.deputado_id == dep.id,
                Assiduidade.sessao_id.in_(sessoes_ids),
                Assiduidade.status.like("Ausência em Missão Parlamentar%")
            ).count()

            falta_quorum = s.query(Assiduidade).filter(
                Assiduidade.deputado_id == dep.id,
                Assiduidade.sessao_id.in_(sessoes_ids),
                Assiduidade.status.like("Falta ao Quórum de Votação%")
            ).count()

            # Só incluir deputados que tiveram alguma participação nas sessões filtradas
            total_participacoes = presencas + faltas_j + amp + falta_quorum
            if total_participacoes == 0:
                continue

            denom = presencas + falta_quorum
            assiduidade_pct = (presencas / denom * 100) if denom else 0.0

            dados.append({
                "nome": dep.nome_original_ultimo,
                "partido": dep.partido_atual,
                "presencas": presencas,
                "faltas_justificadas": faltas_j,
                "missao_parlamentar_amp": amp,
                "faltas_penalizadoras": falta_quorum,
                "assiduidade_pct": round(assiduidade_pct, 2)
            })
        
        return jsonify({"ok": True, "deputados": dados})
    finally:
        s.close()

@app.route("/sessoes", methods=["GET"])
def listar_sessoes():
    _, SessionLocal = get_engine_and_session()
    s = SessionLocal()
    try:
        dados = [{
            "id_legis_sessao": x.id_legis_sessao,
            "legislatura": x.legislatura,
            "numero": x.numero,
            "tipo": x.tipo,
            "data": x.data.isoformat()
        } for x in s.query(Sessao).order_by(Sessao.data.desc()).all()]
        return jsonify({"ok": True, "sessoes": dados})
    finally:
        s.close()

@app.route("/deputados/<nome>/detalhes", methods=["GET"])
def detalhes_deputado(nome):
    """Retorna detalhes sessão-a-sessão de um deputado específico"""
    _, SessionLocal = get_engine_and_session()
    s = SessionLocal()
    try:
        # Buscar deputado (case-insensitive, parcial)
        dep = s.query(Deputado).filter(
            Deputado.nome_original_ultimo.ilike(f"%{nome}%")
        ).first()
        
        if not dep:
            return jsonify({"ok": False, "mensagem": "Deputado não encontrado"}), 404
        
        # Buscar todas as assiduidades deste deputado com info da sessão
        registos = s.query(Assiduidade, Sessao).join(
            Sessao, Assiduidade.sessao_id == Sessao.id
        ).filter(
            Assiduidade.deputado_id == dep.id
        ).order_by(Sessao.data.desc()).all()
        
        detalhes = [{
            "data": sess.data.isoformat(),
            "id_legis_sessao": sess.id_legis_sessao,
            "tipo": sess.tipo,
            "legislatura": sess.legislatura,
            "numero": sess.numero,
            "status": ass.status,
            "motivo": ass.motivo or "",
            "partido": ass.partido
        } for ass, sess in registos]
        
        return jsonify({
            "ok": True,
            "deputado": {
                "nome": dep.nome_original_ultimo,
                "partido": dep.partido_atual
            },
            "total_sessoes": len(detalhes),
            "detalhes": detalhes
        })
    finally:
        s.close()

@app.route("/estatisticas/sessoes", methods=["GET"])
def estatisticas_sessoes():
    _, SessionLocal = get_engine_and_session()
    s = SessionLocal()
    try:
        legislatura = request.args.get("legislatura")
        tipo_sessao = request.args.get("tipo") or request.args.get("tipo_sessao")
        data_inicio = parse_iso_date(request.args.get("data_inicio"))
        data_fim = parse_iso_date(request.args.get("data_fim"))

        query = s.query(Sessao)
        if legislatura:
            query = query.filter(Sessao.legislatura == legislatura)
        if data_inicio:
            query = query.filter(Sessao.data >= data_inicio)
        if data_fim:
            query = query.filter(Sessao.data <= data_fim)
        if tipo_sessao:
            query = query.filter(Sessao.tipo == tipo_sessao)

        sessoes = query.order_by(Sessao.data.asc()).all()
        dados = []
        for sess in sessoes:
            total_registos = s.query(Assiduidade).filter(Assiduidade.sessao_id == sess.id).count()

            presencas = s.query(func.count(Assiduidade.id)).filter(
                Assiduidade.sessao_id == sess.id,
                Assiduidade.status.like("Presença%")
            ).scalar() or 0

            falta_quorum = s.query(func.count(Assiduidade.id)).filter(
                Assiduidade.sessao_id == sess.id,
                Assiduidade.status.like("Falta ao Quórum de Votação%")
            ).scalar() or 0

            faltas_j = s.query(func.count(Assiduidade.id)).filter(
                Assiduidade.sessao_id == sess.id,
                Assiduidade.status.like("Falta Justificada%")
            ).scalar() or 0

            amp = s.query(func.count(Assiduidade.id)).filter(
                Assiduidade.sessao_id == sess.id,
                Assiduidade.status.like("Ausência em Missão Parlamentar%")
            ).scalar() or 0

            denom = presencas + falta_quorum
            assiduidade_pct = (presencas / denom * 100) if denom else 0.0

            dados.append({
                "id_legis_sessao": sess.id_legis_sessao,
                "legislatura": sess.legislatura,
                "numero": sess.numero,
                "data": sess.data.isoformat(),
                "tipo": sess.tipo,
                "presencas": presencas,
                "faltas_quorum": falta_quorum,
                "faltas_justificadas": faltas_j,
                "amp": amp,
                "total_registos": total_registos,
                "assiduidade_pct": round(assiduidade_pct, 2)
            })
        return jsonify({"ok": True, "sessoes": dados})
    finally:
        s.close()

@app.route("/substituicoes", methods=["GET"])
def listar_substituicoes():
    """Lista deputados que saíram e entraram por partido ao longo das sessões"""
    _, SessionLocal = get_engine_and_session()
    s = SessionLocal()
    try:
        # Buscar todas as sessões ordenadas por data
        sessoes = s.query(Sessao).order_by(Sessao.data.asc()).all()
        
        # Dicionário para rastrear deputados por partido em cada sessão
        historico_partidos = {}
        
        for sessao in sessoes:
            # Buscar todos os deputados presentes nesta sessão
            registos = s.query(Assiduidade, Deputado).join(
                Deputado, Assiduidade.deputado_id == Deputado.id
            ).filter(
                Assiduidade.sessao_id == sessao.id
            ).all()
            
            # Agrupar por partido
            deputados_por_partido = {}
            for ass, dep in registos:
                partido = ass.partido or dep.partido_atual or "Sem Partido"
                if partido not in deputados_por_partido:
                    deputados_por_partido[partido] = set()
                deputados_por_partido[partido].add(dep.nome_original_ultimo)
            
            # Atualizar histórico
            for partido, deputados in deputados_por_partido.items():
                if partido not in historico_partidos:
                    historico_partidos[partido] = {}
                
                for deputado in deputados:
                    if deputado not in historico_partidos[partido]:
                        historico_partidos[partido][deputado] = {
                            "primeira_sessao": sessao.id_legis_sessao,
                            "primeira_data": sessao.data.isoformat(),
                            "ultima_sessao": sessao.id_legis_sessao,
                            "ultima_data": sessao.data.isoformat()
                        }
                    else:
                        # Atualizar última sessão
                        historico_partidos[partido][deputado]["ultima_sessao"] = sessao.id_legis_sessao
                        historico_partidos[partido][deputado]["ultima_data"] = sessao.data.isoformat()
        
        # Agrupar saídas e entradas por partido
        movimentos_por_partido = {}
        
        for partido, deputados_hist in historico_partidos.items():
            saidas = []
            entradas = []
            
            for nome, info in deputados_hist.items():
                # Se primeira != última sessão, o deputado teve um período de atividade
                # Se primeira == última, apareceu em apenas uma sessão
                
                # Considerar "saída" se não está na última sessão conhecida do sistema
                # Considerar "entrada" se não estava na primeira sessão conhecida
                
                # Para simplificar: listar todos com suas datas de início e fim
                deputado_info = {
                    "nome": nome,
                    "primeira_sessao": info["primeira_sessao"],
                    "primeira_data": info["primeira_data"],
                    "ultima_sessao": info["ultima_sessao"],
                    "ultima_data": info["ultima_data"]
                }
                
                # Verificar se foi a última sessão de todas
                ultima_sessao_sistema = sessoes[-1].id_legis_sessao if sessoes else None
                
                if info["ultima_sessao"] != ultima_sessao_sistema:
                    saidas.append(deputado_info)
                
                if info["primeira_sessao"] != sessoes[0].id_legis_sessao if sessoes else False:
                    entradas.append(deputado_info)
            
            if saidas or entradas:
                movimentos_por_partido[partido] = {
                    "saidas": saidas,
                    "entradas": entradas
                }
        
        return jsonify({
            "ok": True, 
            "movimentos": movimentos_por_partido,
            "total_partidos": len(movimentos_por_partido)
        })
    finally:
        s.close()

@app.route("/estatisticas/analise-avancada", methods=["GET"])
def analise_avancada():
    """Retorna estatísticas avançadas: faltas por dia da semana, piores sessões, custo estimado"""
    _, SessionLocal = get_engine_and_session()
    s = SessionLocal()
    
    # Parâmetro configurável para custo diário
    custo_dia = float(request.args.get("custo_dia", 200))
    
    try:
        # 1. Buscar todas as sessões com estatísticas
        sessoes = s.query(Sessao).order_by(Sessao.data.asc()).all()
        
        # 2. Analisar faltas por dia da semana
        faltas_por_dia_semana = {
            0: {"dia": "Segunda", "faltas": 0, "sessoes": 0},
            1: {"dia": "Terça", "faltas": 0, "sessoes": 0},
            2: {"dia": "Quarta", "faltas": 0, "sessoes": 0},
            3: {"dia": "Quinta", "faltas": 0, "sessoes": 0},
            4: {"dia": "Sexta", "faltas": 0, "sessoes": 0},
            5: {"dia": "Sábado", "faltas": 0, "sessoes": 0},
            6: {"dia": "Domingo", "faltas": 0, "sessoes": 0}
        }
        
        piores_sessoes = []
        total_faltas_penalizadoras = 0
        
        for sess in sessoes:
            # Dia da semana (0=segunda, 6=domingo)
            dia_semana = sess.data.weekday()
            
            # Contar faltas penalizadoras nesta sessão
            faltas_quorum = s.query(func.count(Assiduidade.id)).filter(
                Assiduidade.sessao_id == sess.id,
                Assiduidade.status.like("Falta ao Quórum de Votação%")
            ).scalar()
            
            total_faltas_penalizadoras += faltas_quorum
            faltas_por_dia_semana[dia_semana]["faltas"] += faltas_quorum
            faltas_por_dia_semana[dia_semana]["sessoes"] += 1
            
            # Calcular assiduidade desta sessão para ranking de piores
            presencas = s.query(func.count(Assiduidade.id)).filter(
                Assiduidade.sessao_id == sess.id,
                Assiduidade.status.like("Presença%")
            ).scalar()
            
            total_registos = s.query(Assiduidade).filter(Assiduidade.sessao_id == sess.id).count()
            
            denom = presencas + faltas_quorum
            assiduidade_pct = (presencas / denom * 100) if denom else 0.0
            
            piores_sessoes.append({
                "id_legis_sessao": sess.id_legis_sessao,
                "data": sess.data.isoformat(),
                "tipo": sess.tipo,
                "assiduidade_pct": round(assiduidade_pct, 2),
                "faltas_quorum": faltas_quorum,
                "presencas": presencas,
                "total_registos": total_registos,
                "dia_semana": ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"][dia_semana]
            })
        
        # Ordenar piores sessões por menor assiduidade
        piores_sessoes.sort(key=lambda x: x["assiduidade_pct"])
        top_10_piores = piores_sessoes[:10]
        
        # Calcular custo estimado
        custo_estimado = total_faltas_penalizadoras * custo_dia
        
        # Converter dict de faltas por dia em lista
        faltas_dia_lista = [
            {
                "dia": info["dia"],
                "faltas": info["faltas"],
                "sessoes": info["sessoes"],
                "media_por_sessao": round(info["faltas"] / info["sessoes"], 2) if info["sessoes"] > 0 else 0
            }
            for dia, info in sorted(faltas_por_dia_semana.items())
        ]
        
        return jsonify({
            "ok": True,
            "faltas_por_dia_semana": faltas_dia_lista,
            "top_10_piores_sessoes": top_10_piores,
            "custo_estimado": {
                "total_faltas_penalizadoras": total_faltas_penalizadoras,
                "custo_por_dia": custo_dia,
                "custo_total": round(custo_estimado, 2),
                "disclaimer": "Estimativa baseada no salário base de deputado (€4.595,81/mês, 14 meses). Não inclui subsídios adicionais."
            }
        })
    finally:
        s.close()

@app.route("/atividade/estatisticas", methods=["GET"])
def atividade_estatisticas():
    """Retorna estatísticas agregadas de atividade parlamentar"""
    _, SessionLocal = get_engine_and_session()
    s = SessionLocal()
    try:
        legislatura = request.args.get("legislatura")
        
        query = s.query(DeputadoAtividade, Deputado).join(
            Deputado, DeputadoAtividade.deputado_id == Deputado.id
        )
        if legislatura:
            query = query.filter(DeputadoAtividade.legislatura == legislatura)
        
        registros = query.all()
        
        # Agregações
        total_por_partido = {}
        total_por_tipo = {}
        partido_mais_ativo = None
        max_atividades = 0
        
        for atividade, dep in registros:
            # Por partido
            if dep.partido_atual:
                if dep.partido_atual not in total_por_partido:
                    total_por_partido[dep.partido_atual] = 0
                total_por_partido[dep.partido_atual] += atividade.total
                
                if total_por_partido[dep.partido_atual] > max_atividades:
                    max_atividades = total_por_partido[dep.partido_atual]
                    partido_mais_ativo = dep.partido_atual
            
            # Por tipo
            if atividade.tipo not in total_por_tipo:
                total_por_tipo[atividade.tipo] = 0
            total_por_tipo[atividade.tipo] += atividade.total
        
        # Cálculos
        total_atividades = sum(total_por_tipo.values())
        deputados_unicos = len(set(dep.id for _, dep in registros))
        iniciativas = total_por_tipo.get("Iniciativas", 0)
        
        # Taxa de participação (deputados com atividade / total de deputados)
        total_deputados = s.query(func.count(Deputado.id)).scalar()
        taxa_participacao = (deputados_unicos / total_deputados * 100) if total_deputados else 0
        
        return jsonify({
            "ok": True,
            "partido_mais_ativo": partido_mais_ativo or "-",
            "iniciativas_legislativas": iniciativas,
            "taxa_participacao": round(taxa_participacao, 1),
            "total_atividades": total_atividades,
            "deputados_ativos": deputados_unicos,
            "tipos_atividade": len(total_por_tipo)
        })
    finally:
        s.close()

if __name__ == "__main__":
    app.run(debug=True, port=5001, host="0.0.0.0")

