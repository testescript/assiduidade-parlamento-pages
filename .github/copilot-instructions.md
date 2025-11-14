# Instruções do Copilot — Assiduidade Parlamentar

Stack pequena e focada:
- Backend: API Flask + SQLAlchemy (BD SQLite)
- Frontend: HTML/JS estático (Chart.js) a chamar a API
- Fluxo de dados: upload CSV → validar/normalizar → persistir → servir estatísticas

## Estrutura do repositório (paths importantes)
- `backend/` app Flask: `app.py` (rotas), `processador.py` (validação CSV), `utils.py` (helpers), `models.py` (ORM + init BD)
- `database/base.db` ficheiro SQLite (criado automaticamente por `models.py`)
- `frontend/` páginas estáticas: `index.html` (back‑office upload), `public.html` (gráficos), `landing.html`
- `uploads/` CSVs (se usados)
- `run_project.sh` arranque local do backend (5001) + servidor estático (8000)

## Execução/Dev
- Criar venv e instalar: `pip install -r requirements.txt`
- Arranque rápido: `./run_project.sh` (mata 5001/8000, sobe Flask + servidor estático)
- Manual: `cd backend && python app.py` (API em `http://127.0.0.1:5001`) e `cd frontend && python -m http.server 8000`
- CORS ativo globalmente; o frontend espera a API em `http://127.0.0.1:5001`

## Padrões e contratos do backend
- Imports absolutos dentro de `backend` (sem `.`):
  - `from processador import validar_e_preparar`
  - `from models import get_engine_and_session, Deputado, Sessao, Assiduidade`
- Caminho da BD é relativo a `backend/`: `sqlite:///../database/base.db` — atenção ao diretório de trabalho.
- Padrão de sessão: `engine, SessionLocal = get_engine_and_session(); s = SessionLocal(); try: ... s.commit() ... finally: s.close()`
- Idempotência: `Assiduidade` tem `UniqueConstraint(sessao_id, deputado_id)`; `/upload` devolve 409 se a sessão já existir (`id_legis_sessao`).
- Semântica dos estados (afeta métricas/validação):
  - Assiduidade % = Presenças / (Presenças + Falta ao Quórum) × 100
  - AMP (“Ausência em Missão Parlamentar”) não penaliza por omissão
  - “Falta Justificada (FJ)” exige `MOTIVO` válido (ver `utils.MOTIVOS_VALIDOS`)

## CSV (separado por tabulações)
- Leitura: `pd.read_csv(..., sep="\t", quotechar='"', dtype=str)`
- Colunas obrigatórias (`utils.COLS_ESPERADAS`):
  `LEGISLATURA, DATA, NUMERO, SESSAO, ID_LEGIS_SESSAO, DEPUTADO, PARTIDO, ASSIDUIDADE, MOTIVO`
- Limpeza/normalização (`utils.py`):
  - `limpar_campo`: trim, remove aspas, colapsa espaços, trata NaN/"nan" como vazio
  - `normalizar_nome`: remove acentos e põe minúsculas (deduplicar `Deputado`)
  - `necessita_motivo`/`motivo_valido`: obriga motivo para FJ (AMP opcional por omissão)
- Datas no CSV: `dd-mm-YYYY` (`processador.parse_data_portugues`)

## API (contratos)
- `POST /upload` (campo multipart `file`)
  - 200: `{ ok, mensagem, sessao, resumo, inseridos, novos_deputados, duplicados_ignorados }`
  - 400: erros de validação com `etapa`, `mensagem`, opcional `violacoes`
  - 409: sessão já carregada
- `GET /deputados` → `{ ok, deputados: [{ nome, partido, presencas, faltas_justificadas, missao_parlamentar_amp, faltas_penalizadoras, assiduidade_pct }] }`
- `GET /sessoes` → `{ ok, sessoes: [{ id_legis_sessao, legislatura, numero, tipo, data }] }`
- `GET /estatisticas/sessoes` → agregados por sessão com `assiduidade_pct`

## Frontend
- `frontend/index.html` envia CSV para `/upload` e depois refaz `/deputados`, `/sessoes`, `/estatisticas/sessoes`
- `public.html` mostra top‑20, médias por partido e série temporal com Chart.js
- Base da API definida inline: `const API = "http://127.0.0.1:5001"`

## Extensões seguras
- Reutilizar `get_engine_and_session()` e o padrão try/commit/finally; garantir `s.close()`
- Manter estilo de imports absolutos em `backend/`
- Preservar as regras de validação e a fórmula de assiduidade salvo alteração intencional de semântica pública
- Ao adicionar estados/motivos, atualizar `utils.MOTIVOS_VALIDOS` e validadores
- Se mudar portas/local da BD, sincronizar `frontend/*.html`, `run_project.sh` e `models.py`
