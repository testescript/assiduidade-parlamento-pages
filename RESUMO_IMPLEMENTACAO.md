# ✅ Sistema Dual Completo — Dev + GitHub Pages

## 📦 O que foi criado

### 1. **Projeto de Desenvolvimento** (assiduidade_parlamento)
- ✅ Backend Flask + SQLite (modo completo)
- ✅ Upload de CSV funcional
- ✅ `config.js` com `mode: 'api'`
- ✅ Todos os HTMLs usam `fetchData()` para acesso abstrato aos dados
- 🎯 **Uso**: Desenvolvimento local, carregar dados, testar funcionalidades

### 2. **Projeto GitHub Pages** (assiduidade_parlamento_github_pages)
- ✅ Versão estática sem backend
- ✅ Dados em JSON pré-exportados (pasta `frontend/data/`)
- ✅ `config.js` com `mode: 'static'`
- ✅ Script de atualização automática (`atualizar_dados.sh`)
- ✅ Documentação completa (README.md + GUIA_RAPIDO.md)
- 🎯 **Uso**: Hospedagem pública gratuita no GitHub Pages

---

## 🔄 Arquitetura de Configuração Dual

```
┌─────────────────────────────────────────────────────────────┐
│  DESENVOLVIMENTO (assiduidade_parlamento)                   │
├─────────────────────────────────────────────────────────────┤
│  config.js → mode: 'api'                                    │
│  fetchData('/deputados') → http://127.0.0.1:5001/deputados  │
│  Backend Flask → SQLite → Resposta JSON                     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  PRODUÇÃO (assiduidade_parlamento_github_pages)             │
├─────────────────────────────────────────────────────────────┤
│  config.js → mode: 'static'                                 │
│  fetchData('/deputados') → frontend/data/deputados.json     │
│  Sem backend → Dados pré-exportados → GitHub Pages serve    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Ficheiros Modificados

### HTMLs (ambos os projetos)
Todos agora importam `config.js` e usam `fetchData()`:

1. **public.html**
   - ✅ Import `<script src="config.js"></script>`
   - ✅ Substituído `fetch(API + ...)` por `fetchData(...)`
   - ✅ Funciona em modo API e static

2. **analise.html**
   - ✅ Import `config.js`
   - ✅ 5 endpoints substituídos por `fetchData()`
   - ✅ Mantém funcionalidade completa

3. **atividade.html**
   - ✅ Import `config.js`
   - ✅ 4 endpoints substituídos
   - ✅ Gráficos e filtros funcionam em ambos os modos

4. **index.html** (back-office)
   - ✅ Import `config.js`
   - ✅ Upload usa `CONFIG.apiUrl` (só funciona em modo API)
   - ✅ Leituras usam `fetchData()`

5. **landing.html**
   - ✅ Sem alterações (não usa dados da API)

---

## 🆕 Ficheiros Criados

### Projeto GitHub Pages

1. **export_to_json.py** (6.2 KB)
   - Exporta 6 ficheiros JSON da BD SQLite
   - Total exportado: ~833 KB
   ```
   deputados.json         333 KB
   atividades.json        491 KB
   agenda.json              9 KB
   sessoes.json            <1 KB
   estatisticas_sessoes.json <1 KB
   substituicoes.json      <1 KB
   ```

2. **atualizar_dados.sh** (1.4 KB)
   - Script automático de atualização
   - Copia BD → Exporta JSON → Commit → Push
   - Executável: `chmod +x`

3. **config.js** (duas versões!)
   - **DEV**: `mode: 'api'` → usa Flask
   - **GitHub Pages**: `mode: 'static'` → usa JSON

4. **README.md** (6.8 KB)
   - Documentação completa do sistema
   - Workflow de atualização
   - Troubleshooting

5. **GUIA_RAPIDO.md** (4.5 KB)
   - Instruções passo-a-passo
   - Comandos prontos a copiar
   - Troubleshooting comum

---

## 🚀 Como Usar

### Desenvolvimento Local (Projeto Original)

```bash
cd /home/diogo/Desktop/assiduidade_parlamento
./run_project.sh
```

- Backend: http://127.0.0.1:5001
- Frontend: http://127.0.0.1:8000
- Upload CSV: ✅ Funcional
- Modo: `api` (acede ao Flask)

### Publicar no GitHub Pages

#### PRIMEIRA VEZ (configuração inicial)

```bash
cd /home/diogo/Desktop/assiduidade_parlamento_github_pages
git init
git add .
git commit -m "🎉 Initial commit"
git remote add origin https://github.com/testescript/assiduidade-parlamento-pages.git
git push -u origin main
```

No GitHub:
1. Ir a **Settings** → **Pages**
2. Branch: `main` → Folder: `/frontend`
3. Save

Aguardar 2 minutos → Site online!

#### SEMPRE (atualizar dados)

```bash
cd /home/diogo/Desktop/assiduidade_parlamento_github_pages
./atualizar_dados.sh
```

Pronto! GitHub Pages atualiza automaticamente.

---

## 📊 Fluxo de Trabalho Completo

```
1. DESENVOLVIMENTO
   ├─ Upload CSV novo no projeto DEV
   ├─ Backend processa → SQLite
   └─ Testar: http://localhost:5001

2. EXPORTAÇÃO
   ├─ cd assiduidade_parlamento_github_pages
   ├─ ./atualizar_dados.sh
   │   ├─ Copia base.db do projeto DEV
   │   ├─ Exporta JSON (export_to_json.py)
   │   ├─ git commit
   │   └─ git push
   └─ ✅ Dados atualizados

3. PUBLICAÇÃO
   ├─ GitHub recebe push
   ├─ GitHub Pages faz deploy automático
   └─ ✅ Site online em ~2 minutos
```

---

## 🔧 Estrutura de Pastas

```
Desktop/
├── assiduidade_parlamento/              ← DESENVOLVIMENTO
│   ├── backend/
│   │   ├── app.py
│   │   ├── models.py
│   │   └── processador.py
│   ├── database/
│   │   └── base.db                      ← BD principal (sempre atualizada)
│   ├── frontend/
│   │   ├── config.js                    ← mode: 'api'
│   │   ├── public.html
│   │   ├── analise.html
│   │   ├── atividade.html
│   │   ├── index.html
│   │   └── landing.html
│   └── run_project.sh
│
└── assiduidade_parlamento_github_pages/ ← GITHUB PAGES
    ├── frontend/
    │   ├── config.js                    ← mode: 'static'
    │   ├── data/                        ← JSON exportados
    │   │   ├── deputados.json
    │   │   ├── atividades.json
    │   │   └── ...
    │   ├── public.html
    │   ├── analise.html
    │   ├── atividade.html
    │   └── landing.html
    ├── database/
    │   └── base.db                      ← Cópia (atualizada por script)
    ├── export_to_json.py
    ├── atualizar_dados.sh
    ├── README.md
    └── GUIA_RAPIDO.md
```

---

## ✨ Vantagens desta Arquitetura

### ✅ Desenvolvimento
- Backend completo com upload CSV
- Testes em tempo real
- Base de dados dinâmica
- Sem custos de hosting durante desenvolvimento

### ✅ Produção (GitHub Pages)
- **100% gratuito** (GitHub Pages free tier)
- **Rápido** (CDN global do GitHub)
- **Seguro** (sem backend exposto, HTTPS automático)
- **Controlo total** (atualização manual quando quiser)
- **Sem manutenção** (sem servidor para gerir)

### ✅ Manutenção
- Dois projetos separados e independentes
- `config.js` diferente em cada um (não se misturam!)
- Script automático para atualização
- Documentação completa

---

## 🎯 Próximos Passos

1. ✅ **FEITO**: Sistema dual criado e funcional
2. ⏭️ **PRÓXIMO**: Inicializar git e fazer push inicial
3. ⏭️ **DEPOIS**: Ativar GitHub Pages nas definições
4. ⏭️ **FUTURO**: Configurar domínio personalizado (opcional)

---

## 📚 Documentação

- **README.md**: Documentação técnica completa
- **GUIA_RAPIDO.md**: Comandos prontos e troubleshooting
- **Este ficheiro**: Resumo do que foi implementado

---

**Data de criação**: 14/11/2025  
**Versão**: 1.0  
**Status**: ✅ Pronto para uso
