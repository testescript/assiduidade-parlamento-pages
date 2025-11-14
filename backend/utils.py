import unicodedata
import re
import math

COLS_ESPERADAS = [
    "LEGISLATURA", "DATA", "NUMERO", "SESSAO", "ID_LEGIS_SESSAO",
    "DEPUTADO", "PARTIDO", "ASSIDUIDADE", "MOTIVO"
]

# Lista oficial normalizada (sem acentos, minúsculas)
MOTIVOS_VALIDOS = {
    "doenca",
    "casamento",
    "maternidade e paternidade",
    "luto",
    "forca maior",
    "missao parlamentar",
    "trabalho parlamentar",
    "trabalho politico",
    "participacao em atividades parlamentares",
    "dificuldades de transporte",
    "razao de consciencia",
    "assistencia a familia",
    "motivo justificado",
    # Evita duplicações semânticas como "trabalho parlamentar" se já tens "missao ou trabalho parlamentar"
}

def _is_nan_like(valor) -> bool:
    """Deteta NaN do pandas e literais 'nan'/'NaN' como vazio."""
    if valor is None:
        return True
    # math.nan ou numpy.nan
    try:
        if isinstance(valor, float) and math.isnan(valor):
            return True
    except Exception:
        pass
    # strings 'nan'/'NaN' ou semelhantes
    if isinstance(valor, str) and valor.strip().lower() in {"nan", "na", "none", ""}:
        return True
    return False

def limpar_campo(valor: str) -> str:
    """Limpa aspas, espaços e trata NaN como vazio."""
    if _is_nan_like(valor):
        return ""
    if not isinstance(valor, str):
        valor = str(valor)
    valor = valor.strip()
    # remover aspas duplas envolventes
    if len(valor) >= 2 and valor[0] == '"' and valor[-1] == '"':
        valor = valor[1:-1]
    # normalizar espaços internos
    valor = re.sub(r"\s+", " ", valor)
    return valor

def normalizar_nome(nome: str) -> str:
    """Remove acentos e coloca em minúsculas para comparação estável."""
    nome = limpar_campo(nome)
    if nome == "":
        return ""
    nome = unicodedata.normalize("NFKD", nome).encode("ASCII", "ignore").decode("utf-8")
    nome = " ".join(nome.split()).lower()
    return nome

def validar_colunas(df) -> list[str]:
    return [c for c in COLS_ESPERADAS if c not in df.columns]

def estados_que_exigem_motivo(include_amp: bool = False) -> list[str]:
    """
    Estados que exigem MOTIVO preenchido.
    - Falta Justificada (FJ) exige motivo (da lista oficial).
    - Falta ao Quórum de Votação NÃO exige motivo (é falta penalizadora, não justificada).
    - AMP: por padrão NÃO exige motivo (include_amp=False).
    """
    exigem = [
        "Falta Justificada (FJ)",
        # "Falta ao Quórum de Votação",  # <- removido: não exige motivo
        "Ausência em Missão Parlamentar (AMP)"
    ]
    if not include_amp:
        exigem = [e for e in exigem if "AMP" not in e]
    return exigem

def necessita_motivo(status: str, include_amp: bool = False) -> bool:
    """Determina se o status exige MOTIVO."""
    status = limpar_campo(status)
    if status.startswith("Presença"):
        return False
    return status in estados_que_exigem_motivo(include_amp)

def motivo_valido(motivo: str) -> bool:
    """Verifica se o MOTIVO pertence à lista oficial (normalizado)."""
    motivo_norm = normalizar_nome(motivo)
    if motivo_norm == "":
        return False
    for m in MOTIVOS_VALIDOS:
        if motivo_norm.startswith(m):
            return True
    return False
