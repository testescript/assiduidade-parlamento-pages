# 🚀 Guia Rápido — GitHub Pages

## Configuração Inicial (Fazer UMA vez)

### 1. Inicializar Git
```bash
cd /home/diogo/Desktop/assiduidade_parlamento_github_pages
git init
git add .
git commit -m "🎉 Initial commit - GitHub Pages version"
```

### 2. Criar Repositório no GitHub
1. Ir a https://github.com/new
2. Nome: `assiduidade-parlamento-pages` (ou outro)
3. **NÃO** marcar "Add README"
4. Clicar "Create repository"

### 3. Conectar e Fazer Push
```bash
git remote add origin https://github.com/testescript/assiduidade-parlamento-pages.git
git branch -M main
git push -u origin main
```

### 4. Ativar GitHub Pages
1. No GitHub, ir ao repositório → **Settings** → **Pages**
2. **Source**: Deploy from a branch
3. **Branch**: main → **Folder**: /frontend
4. Clicar **Save**

✅ Aguardar 1-2 minutos. Site estará em:
```
https://testescript.github.io/assiduidade-parlamento-pages/public.html
```

---

## Atualizar Dados (Sempre que houver novos dados)

### Modo Automático ⚡
```bash
cd /home/diogo/Desktop/assiduidade_parlamento_github_pages
./atualizar_dados.sh
```

**O que faz:**
1. ✅ Copia BD do projeto de desenvolvimento
2. ✅ Exporta dados para JSON
3. ✅ Faz commit
4. ✅ Push para GitHub
5. ✅ GitHub Pages atualiza automaticamente

### Modo Manual (se preferir)
```bash
# 1. Copiar BD atualizada
cp ../assiduidade_parlamento/database/base.db database/base.db

# 2. Exportar JSON
python3 export_to_json.py

# 3. Ver mudanças
git status

# 4. Commit e push
git add frontend/data/*.json
git commit -m "📊 Atualização $(date '+%d/%m/%Y')"
git push
```

---

## Testar Localmente ANTES de Publicar

```bash
cd frontend
python3 -m http.server 8000
```

Abrir no browser: http://localhost:8000/public.html

**Verificar:**
- ✅ Gráficos aparecem
- ✅ Dados corretos
- ✅ Dark mode funciona
- ✅ Sem erros no console (F12)

Se estiver tudo OK → `git push`

---

## Estrutura de Ficheiros Importante

```
assiduidade_parlamento_github_pages/
├── frontend/
│   ├── config.js          ← MODE: 'static' (NÃO alterar!)
│   ├── data/              ← JSONs gerados por export_to_json.py
│   ├── public.html        ← Página principal
│   ├── analise.html
│   ├── atividade.html
│   └── landing.html
├── export_to_json.py      ← Exporta BD → JSON
├── atualizar_dados.sh     ← Script automático
└── database/base.db       ← Cópia da BD (atualizada pelo script)
```

---

## Diferenças entre Projetos

| Ficheiro | Projeto DEV | Projeto GitHub Pages |
|----------|-------------|---------------------|
| `config.js` | `mode: 'api'` | `mode: 'static'` |
| Backend | ✅ Roda Flask | ❌ Sem backend |
| Upload CSV | ✅ Funcional | ❌ Desativado |
| Dados | 🔴 SQLite dinâmico | 📄 JSON estático |

⚠️ **IMPORTANTE**: Nunca copiar `config.js` do DEV para GitHub Pages! 
São configurações diferentes.

---

## Comandos Git Úteis

```bash
# Ver status
git status

# Ver últimos commits
git log --oneline -5

# Ver diferenças antes de commit
git diff frontend/data/

# Reverter última alteração (antes de push)
git reset --soft HEAD~1

# Forçar push (cuidado!)
git push --force

# Ver repositórios remotos
git remote -v
```

---

## Troubleshooting

### ❌ Erro: "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/testescript/assiduidade-parlamento-pages.git
```

### ❌ Página não atualiza no GitHub Pages
1. Aguardar 2-5 minutos
2. Fazer refresh forçado (Ctrl+Shift+R)
3. Limpar cache do browser
4. Verificar em aba anónima

### ❌ Gráficos não aparecem
1. Verificar console (F12) → Erros?
2. Confirmar `config.js` → `mode: 'static'`
3. Confirmar ficheiros JSON existem em `frontend/data/`
4. Testar localmente com `python3 -m http.server 8000`

### ❌ "Export failed"
```bash
# Verificar se BD existe
ls -lh database/base.db

# Copiar manualmente
cp ../assiduidade_parlamento/database/base.db database/base.db

# Tentar novamente
python3 export_to_json.py
```

---

## URLs Importantes

- **Projeto DEV**: http://localhost:5001
- **Teste local GitHub Pages**: http://localhost:8000/public.html
- **GitHub Pages online**: https://testescript.github.io/assiduidade-parlamento-pages/public.html
- **Repositório DEV**: https://github.com/testescript/assiduidade-parlamento
- **Repositório Pages**: https://github.com/testescript/assiduidade-parlamento-pages

---

**Última atualização**: 14/01/2025
