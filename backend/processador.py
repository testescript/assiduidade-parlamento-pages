import pandas as pd
from datetime import datetime

# Import absoluto
from utils import limpar_campo, normalizar_nome, validar_colunas, necessita_motivo, motivo_valido

def ler_csv_generoso(file_storage) -> pd.DataFrame:
    df = pd.read_csv(file_storage, sep="\t", quotechar='"', dtype=str)
    for col in df.columns:
        df[col] = df[col].apply(limpar_campo)
    return df

def validar_regra_230(df) -> dict:
    distintos = df["DEPUTADO"].nunique()
    return {
        "ok": distintos == 230,
        "mensagem": f"Encontrados {distintos} nomes distintos (esperado: 230).",
        "distintos": distintos
    }

def validar_motivos(df, include_amp: bool = False) -> dict:
    violacoes = []
    for idx, row in df.iterrows():
        status = limpar_campo(row["ASSIDUIDADE"])
        motivo = limpar_campo(row.get("MOTIVO", ""))

        if necessita_motivo(status, include_amp=include_amp):
            if motivo == "":
                violacoes.append({
                    "linha": idx + 2,
                    "deputado": row["DEPUTADO"],
                    "assiduidade": status,
                    "erro": "Motivo em falta"
                })
            elif not motivo_valido(motivo):
                violacoes.append({
                    "linha": idx + 2,
                    "deputado": row["DEPUTADO"],
                    "assiduidade": status,
                    "motivo": motivo,
                    "erro": "Motivo inválido (não consta da lista oficial)"
                })
    ok = len(violacoes) == 0
    return {
        "ok": ok,
        "mensagem": "Todos os motivos são válidos." if ok else f"Foram encontradas {len(violacoes)} violações.",
        "violacoes": violacoes
    }

def parse_data_portugues(data_str: str):
    return datetime.strptime(data_str, "%d-%m-%Y").date()

def extrair_metadados_sessao(df) -> dict:
    return {
        "id_legis_sessao": df["ID_LEGIS_SESSAO"].iloc[0],
        "legislatura": df["LEGISLATURA"].iloc[0],
        "numero": df["NUMERO"].iloc[0],
        "tipo": df["SESSAO"].iloc[0],
        "data": parse_data_portugues(df["DATA"].iloc[0])
    }

def preparar_registos_assiduidade(df) -> list[dict]:
    registos = []
    for _, row in df.iterrows():
        registos.append({
            "deputado_original": row["DEPUTADO"],
            "deputado_normalizado": normalizar_nome(row["DEPUTADO"]),
            "partido": row["PARTIDO"],
            "status": row["ASSIDUIDADE"],
            "motivo": row.get("MOTIVO", "")
        })
    return registos

def validar_e_preparar(file_storage) -> dict:
    try:
        df = ler_csv_generoso(file_storage)
    except Exception as e:
        return {"ok": False, "etapa": "leitura_csv", "mensagem": f"Erro ao ler o CSV: {e}"}

    faltantes = validar_colunas(df)
    if faltantes:
        return {"ok": False, "etapa": "validar_colunas", "mensagem": f"CSV inválido. Faltam colunas: {faltantes}"}

    r230 = validar_regra_230(df)
    if not r230["ok"]:
        return {"ok": False, "etapa": "validar_230", "mensagem": r230["mensagem"]}

    rm = validar_motivos(df, include_amp=False)
    if not rm["ok"]:
        return {"ok": False, "etapa": "validar_motivos", "mensagem": rm["mensagem"], "violacoes": rm["violacoes"]}

    try:
        metadados = extrair_metadados_sessao(df)
    except Exception as e:
        return {"ok": False, "etapa": "metadados", "mensagem": f"Erro a extrair metadados da sessão: {e}"}

    registos = preparar_registos_assiduidade(df)

    return {
        "ok": True,
        "mensagem": "CSV validado e preparado com sucesso.",
        "sessao": metadados,
        "resumo": {"total_linhas": len(df), "nomes_distintos": r230["distintos"]},
        "registos": registos
    }