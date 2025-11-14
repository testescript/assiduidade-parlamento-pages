# Assiduidade Parlamentar — GitHub Pages

🌐 Versão estática do sistema de Assiduidade Parlamentar, hospedada gratuitamente no GitHub Pages.

## 📋 Sobre esta versão

Esta é uma versão **somente leitura** do projeto que funciona com dados JSON pré-exportados. Os dados são atualizados manualmente pelo administrador através de um processo controlado.

### Diferenças em relação à versão completa

| Característica | Versão GitHub Pages | Versão Desenvolvimento |
|---------------|---------------------|------------------------|
| **Backend** | ❌ Não (dados estáticos JSON) | ✅ API Flask + SQLite |
| **Upload CSV** | ❌ Não disponível | ✅ Disponível |
| **Visualizações** | ✅ Todas funcionais | ✅ Todas funcionais |
| **Atualização** | 🔒 Apenas administrador | ✅ Qualquer utilizador autorizado |
| **Custo** | 💰 Gratuito | 💰 Requer servidor |
| **Velocidade** | ⚡ Muito rápido (CDN) | 🐌 Depende do servidor |

## 🏗️ Estrutura do Projeto

```
assiduidade_parlamento_github_pages/
├── frontend/
│   ├── config.js              # Configuração de modo (API/static)
│   ├── data/                  # 📊 Dados JSON exportados
│   │   ├── deputados.json
│   │   ├── sessoes.json
│   │   ├── estatisticas_sessoes.json
│   │   ├── atividades.json
│   │   ├── agenda.json
│   │   └── substituicoes.json
│   ├── public.html            # Página de resumo público
│   ├── analise.html           # Análise interativa avançada
│   ├── atividade.html         # Actividade parlamentar
│   ├── landing.html           # Página inicial
│   └── index.html             # Dashboard administrativo (sem upload)
├── database/
│   └── base.db                # Cópia da BD (só para exportação)
├── export_to_json.py          # Script de exportação
├── atualizar_dados.sh         # Script de atualização automática
└── README.md                  # Este ficheiro

```

## 🔧 Como Funciona

### Sistema de Configuração Dual

O ficheiro `config.js` permite alternar entre dois modos:

```javascript
const CONFIG = {
  mode: 'static',  // 'api' para dev local, 'static' para GitHub Pages
  apiUrl: 'http://127.0.0.1:5001',
  dataPath: 'data'
};
```

- **Modo `api`**: Faz pedidos HTTP para o backend Flask (desenvolvimento local)
- **Modo `static`**: Carrega ficheiros JSON da pasta `data/` (GitHub Pages)

### Função `fetchData()`

Todos os HTMLs usam a função `fetchData()` que abstrai a origem dos dados:

```javascript
// Em vez de:
fetch(`${API}/deputados`)

// Usa-se:
fetchData('/deputados')
// → Carrega data/deputados.json automaticamente em modo static
```

## 📊 Atualizar Dados (Administrador)

### Opção 1: Script Automático (Recomendado)

```bash
cd /home/diogo/Desktop/assiduidade_parlamento_github_pages
./atualizar_dados.sh
```

O script faz automaticamente:
1. ✅ Copia a base de dados atualizada do projeto de desenvolvimento
2. ✅ Exporta todos os dados para JSON
3. ✅ Faz commit das alterações
4. ✅ Push para GitHub (GitHub Pages atualiza automaticamente)

### Opção 2: Processo Manual

```bash
# 1. Copiar BD atualizada
cp ../assiduidade_parlamento/database/base.db database/base.db

# 2. Exportar dados
python3 export_to_json.py

# 3. Commit e push
git add frontend/data/*.json
git commit -m "📊 Atualização de dados - $(date '+%Y-%m-%d')"
git push origin main
```

## 🚀 Configuração Inicial GitHub Pages

### 1. Criar Repositório no GitHub

```bash
cd /home/diogo/Desktop/assiduidade_parlamento_github_pages
git init
git add .
git commit -m "🎉 Initial commit - GitHub Pages version"
```

No GitHub:
1. Criar novo repositório (ex: `assiduidade-parlamento-pages`)
2. **Não** inicializar com README/LICENSE/.gitignore

```bash
git remote add origin https://github.com/testescript/assiduidade-parlamento-pages.git
git branch -M main
git push -u origin main
```

### 2. Ativar GitHub Pages

No repositório GitHub:
1. Ir a **Settings** → **Pages**
2. **Source**: Deploy from a branch
3. **Branch**: `main` / `/(root)` ou `/frontend`
4. Guardar

Aguardar 1-2 minutos. O site estará em:
```
https://testescript.github.io/assiduidade-parlamento-pages/
```

### 3. Ajustar Paths (se necessário)

Se usar `/frontend` como raiz no GitHub Pages:
- URL: `https://testescript.github.io/assiduidade-parlamento-pages/public.html`

Se preferir raiz do repositório:
- Mover conteúdo de `frontend/` para raiz
- Ajustar `config.js` → `dataPath: 'data'`

## 🔄 Workflow Completo

### Desenvolvimento → Produção

1. **Desenvolvimento**: Upload CSV no projeto principal
2. **Backend**: Processa e guarda em SQLite
3. **Exportação**: `./atualizar_dados.sh` exporta para JSON
4. **Git**: Commit + Push para GitHub
5. **GitHub Pages**: Deploy automático
6. **Público**: Visualiza dados atualizados

### Cadência de Atualização

- **Desenvolvimento**: Upload CSV sempre que há nova sessão
- **Produção (GitHub Pages)**: Atualização manual pelo administrador (diária/semanal/mensal conforme necessário)

## 📁 Ficheiros JSON Gerados

| Ficheiro | Tamanho Típico | Conteúdo |
|----------|----------------|----------|
| `deputados.json` | ~330 KB | Todos os deputados com métricas de assiduidade |
| `atividades.json` | ~490 KB | Registos de actividade parlamentar |
| `agenda.json` | ~9 KB | Últimos 100 eventos da agenda |
| `sessoes.json` | <1 KB | Lista de sessões parlamentares |
| `estatisticas_sessoes.json` | <1 KB | Agregados de assiduidade por sessão |
| `substituicoes.json` | <1 KB | Registos de substituições (vazio atualmente) |

**Total**: ~833 KB

## 🛠️ Manutenção

### Verificar se dados estão atualizados

```bash
ls -lh frontend/data/*.json
# Verificar datas de modificação
```

### Testar localmente antes de fazer push

```bash
cd frontend
python3 -m http.server 8000
# Abrir http://localhost:8000/public.html
```

Verificar:
- ✅ Gráficos carregam
- ✅ Estatísticas corretas
- ✅ Dark mode funciona
- ✅ Sem erros na consola do browser

### Reverter atualização (se necessário)

```bash
git log --oneline  # Ver commits
git revert <commit_hash>
git push origin main
```

## 🔐 Segurança

- ✅ Sem backend exposto (apenas ficheiros estáticos)
- ✅ Sem base de dados acessível
- ✅ GitHub Pages serve sobre HTTPS
- ⚠️ Dados JSON são públicos (não incluir informação sensível)

## 📞 Suporte

Para problemas ou dúvidas:
1. Verificar logs do GitHub Actions (se configurado)
2. Testar exportação local: `python3 export_to_json.py`
3. Verificar `config.js` → `mode: 'static'`
4. Confirmar que GitHub Pages está ativo nas definições do repositório

---

**Versão**: 1.0  
**Última atualização**: 2025-01-14  
**Repositório desenvolvimento**: https://github.com/testescript/assiduidade-parlamento
