README.md final (conteúdo limpo, pronto a colar)
🇵🇹 Assiduidade Parlamentar
Projeto público de transparência que mostra a assiduidade dos deputados portugueses em sessões parlamentares. O objetivo é tornar os dados acessíveis, visuais e compreensíveis para todos os cidadãos.

Inclui:

Back‑office → upload de ficheiros CSV oficiais.

Frontend público → gráficos e estatísticas interativas.

Landing page → explicação inicial e missão do projeto.

Estrutura de pastas
Código
assiduidade_parlamento/
├── backend/        # Código Flask (API)
# 🇵🇹 Assiduidade Parlamentar — Documentação

Projeto público de transparência que mostra a assiduidade dos deputados portugueses e cruza com actividade parlamentar e agenda. O objetivo é tornar os dados acessíveis, visuais e compreensíveis para todos os cidadãos.

## Funcionalidades

- Assiduidade: presença, faltas justificadas, missões parlamentares e faltas penalizadoras.
- Actividade Parlamentar: iniciativas, intervenções, requerimentos, comissões, etc. (a partir de JSON oficial).
- Agenda Parlamentar: eventos/itens da agenda com datas, temas e ligações.
- Upload unificado: `POST /upload` aceita CSV e também JSON de Actividade/Agenda.
- Páginas públicas: resumo, análise interactiva e vista de actividade.
- Back‑office separado: interface administrativa para uploads (não exposto na navegação pública).

## Estrutura de pastas

```text
assiduidade_parlamento/
├── backend/
│   ├── app.py                  # Flask API (rotas)
│   ├── models.py               # ORM (SQLite) e engine/session
│   ├── processador.py          # Validação e normalização de CSV
│   ├── processador_atividade.py # Ingestão de Actividade e Agenda (JSON)
│   └── utils.py                # Helpers e validadores
├── database/
│   └── base.db                 # SQLite (criado automaticamente)
├── frontend/
│   ├── landing.html            # Landing pública
│   ├── public.html             # Resumo público (gráficos básicos)
│   ├── analise.html            # Análise interactiva avançada
│   ├── atividade.html          # Actividade + Agenda (gráficos e lista)
│   └── index.html              # Back‑office (uploads; não linkado publicamente)
├── uploads/                    # CSV/JSON carregados
├── requirements.txt
└── run_project.sh              # Arranque rápido (backend + servidor estático)
```

## Arranque rápido (dev)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
./run_project.sh
```

- Backend: `http://127.0.0.1:5001`
- Frontend: `http://127.0.0.1:8000`
	- Landing: `/landing.html`
	- Resumo: `/public.html`
	- Análise: `/analise.html`
	- Actividade: `/atividade.html`
	- Back‑office: `/index.html` (não linkado e deve ser protegido em produção)

## API (principais rotas)

- `POST /upload` (multipart `file`)
	- CSV de assiduidade: valida e insere sessão; suporta substituição segura (409 → confirmação).
	- JSON Actividade: detecta estrutura e ingere por deputado/tipo/legislatura.
	- JSON Agenda: detecta estrutura e ingere itens com datas/tema/secção.
- `GET /deputados`
- `GET /sessoes`
- `GET /estatisticas/sessoes`
- `GET /deputados/filtrados?legislatura=&tipo=&data_inicio=&data_fim=`
- `GET /deputados/<nome>/detalhes`
- `GET /atividade/deputados?legislatura=&tipo=&partido=`
- `GET /atividade/agenda?legislatura=&section=&theme=&data_inicio=&data_fim=`

## Modelos (SQLite)

- `Deputado`, `Sessao`, `Assiduidade` (com unicidade `sessao_id` + `deputado_id`).
- `DeputadoAtividade` (agregados por deputado/tipo/legislatura).
- `AgendaItem` (eventos com início/fim, tema, secção, link, etc.).

## Segurança e separação

- O back‑office (`index.html`) não aparece na navegação pública.
- Em produção, proteger `index.html` com autenticação (ex.: auth básica Nginx) e/ou servir noutro host/porta.
- Opcional: adicionar `<meta name="robots" content="noindex,nofollow">` apenas no back‑office.

## Deploy (exemplo resumido)

Backend com Gunicorn + Nginx:

```bash
pip install gunicorn
cd backend
gunicorn -w 4 -b 127.0.0.1:8000 app:app
```

Nginx (trecho simplificado):

```nginx
server {
	listen 80;
	server_name exemplo.com;
	location /api { proxy_pass http://127.0.0.1:8000; }
	location / { root /var/www/assiduidade/frontend; index landing.html; }
}
```

Proteger back‑office (Nginx):

```nginx
location = /index.html {
	root /var/www/assiduidade/frontend;
	auth_basic "Área restrita — Back-office";
	auth_basic_user_file /etc/nginx/.htpasswd;
}
```

## Notas

- Ficheiros carregados ficam em `uploads/`.
- Base de dados em `database/base.db` (caminho absoluto resolvido pelo backend).
- Para limpar dados: apagar `database/base.db` e reiniciar o backend.

Contribuições e melhorias são bem‑vindas. 🙌
```

### Arranque rápido (dev)
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
./run_project.sh
```
- Backend: `http://127.0.0.1:5001`
- Frontend: `http://127.0.0.1:8000`
	- Landing: `/landing.html`
	- Resumo: `/public.html`
	- Análise: `/analise.html`
	- Actividade: `/atividade.html`
	- Back‑office: `/index.html` (não linkado e deve ser protegido em produção)

### API (principais rotas)
- `POST /upload` (multipart `file`)
	- CSV de assiduidade: valida e insere sessão; suporta substituição segura (409 → confirmação).
	- JSON Actividade: detecta estrutura e ingere por deputado/tipo/legislatura.
	- JSON Agenda: detecta estrutura e ingere itens com datas/tema/secção.
- `GET /deputados`
- `GET /sessoes`
- `GET /estatisticas/sessoes`
- `GET /deputados/filtrados?legislatura=&tipo=&data_inicio=&data_fim=`
- `GET /deputados/<nome>/detalhes`
- `GET /atividade/deputados?legislatura=&tipo=&partido=`
- `GET /atividade/agenda?legislatura=&section=&theme=&data_inicio=&data_fim=`

### Modelos (SQLite)
- `Deputado`, `Sessao`, `Assiduidade` (com unicidade `sessao_id` + `deputado_id`).
- `DeputadoAtividade` (agregados por deputado/tipo/legislatura).
- `AgendaItem` (eventos com início/fim, tema, secção, link, etc.).

### Segurança e separação
- O back‑office (`index.html`) não aparece na navegação pública.
- Em produção, proteger `index.html` com autenticação (ex.: auth básica Nginx) e/ou servir noutro host/porta.
- Opcional: adicionar `<meta name="robots" content="noindex,nofollow">` apenas no back‑office.

### Deploy (exemplo resumido)
Backend com Gunicorn + Nginx:
```
pip install gunicorn
cd backend
gunicorn -w 4 -b 127.0.0.1:8000 app:app
```
Nginx (trecho simplificado):
```
server {
	listen 80;
	server_name exemplo.com;
	location /api { proxy_pass http://127.0.0.1:8000; }
	location / { root /var/www/assiduidade/frontend; index landing.html; }
}
```
Proteger back‑office (Nginx):
```
location = /index.html {
	root /var/www/assiduidade/frontend;
	auth_basic "Área restrita — Back-office";
	auth_basic_user_file /etc/nginx/.htpasswd;
}
```

### Notas
- Ficheiros carregados ficam em `uploads/`.
- Base de dados em `database/base.db` (caminho absoluto resolvido pelo backend).
- Para limpar dados: apagar `database/base.db` e reiniciar o backend.

Contribuições e melhorias são bem‑vindas. 🙌