# ✅ Checklist — Configuração GitHub Pages

## Antes de Começar

- [ ] Tenho conta no GitHub (https://github.com)
- [ ] Git está instalado no meu computador (`git --version`)
- [ ] Tenho acesso aos dois projetos:
  - [ ] `/home/diogo/Desktop/assiduidade_parlamento` (DEV)
  - [ ] `/home/diogo/Desktop/assiduidade_parlamento_github_pages` (PAGES)

---

## 📋 Passo 1: Criar Repositório GitHub

- [ ] 1.1 Ir a https://github.com/new
- [ ] 1.2 Nome do repositório: `assiduidade-parlamento-pages`
- [ ] 1.3 Descrição (opcional): "Transparência Parlamentar - Visualização de Assiduidade"
- [ ] 1.4 **Público** ou Privado (Pages funciona em ambos)
- [ ] 1.5 **NÃO marcar** "Add a README file"
- [ ] 1.6 **NÃO marcar** ".gitignore" ou "license"
- [ ] 1.7 Clicar "Create repository"
- [ ] 1.8 Copiar URL do repositório (ex: `https://github.com/testescript/assiduidade-parlamento-pages.git`)

---

## 📋 Passo 2: Inicializar Git Local

Abrir terminal:

```bash
cd /home/diogo/Desktop/assiduidade_parlamento_github_pages
```

- [ ] 2.1 Executar: `git init`
  - ✅ Deve aparecer: "Initialized empty Git repository"

- [ ] 2.2 Executar: `git add .`
  - ✅ Adiciona todos os ficheiros

- [ ] 2.3 Executar: `git commit -m "🎉 Initial commit - GitHub Pages version"`
  - ✅ Deve mostrar quantos ficheiros foram adicionados

- [ ] 2.4 Executar: `git branch -M main`
  - ✅ Renomeia branch para 'main'

---

## 📋 Passo 3: Conectar ao GitHub

- [ ] 3.1 Executar: `git remote add origin https://github.com/SEU_USER/assiduidade-parlamento-pages.git`
  - ⚠️ **SUBSTITUIR** `SEU_USER` pelo teu username GitHub!
  - Exemplo: `https://github.com/testescript/assiduidade-parlamento-pages.git`

- [ ] 3.2 Verificar: `git remote -v`
  - ✅ Deve mostrar o URL do repositório

- [ ] 3.3 Executar: `git push -u origin main`
  - Se pedir credenciais:
    - Username: teu username GitHub
    - Password: **Personal Access Token** (não é a password!)
      - Criar token em: https://github.com/settings/tokens
      - Scopes: `repo` (marcar tudo em repo)
  - ✅ Deve fazer upload de todos os ficheiros

---

## 📋 Passo 4: Ativar GitHub Pages

- [ ] 4.1 Ir ao repositório no GitHub
- [ ] 4.2 Clicar em **Settings** (tab superior)
- [ ] 4.3 No menu lateral esquerdo → **Pages**
- [ ] 4.4 Em "Build and deployment":
  - Source: **Deploy from a branch**
  - Branch: **main**
  - Folder: **/frontend** (ou /(root) se preferir)
  - [ ] 4.5 Clicar **Save**

- [ ] 4.6 Aguardar 1-2 minutos
- [ ] 4.7 Refrescar a página → deve aparecer:
  ```
  Your site is live at https://SEU_USER.github.io/assiduidade-parlamento-pages/
  ```

---

## 📋 Passo 5: Testar o Site

- [ ] 5.1 Abrir URL do GitHub Pages
  - Se escolheste `/frontend`: adiciona `public.html` ao URL
  - Ex: `https://testescript.github.io/assiduidade-parlamento-pages/public.html`

- [ ] 5.2 Verificar:
  - [ ] Página carrega sem erros
  - [ ] Gráficos aparecem
  - [ ] Estatísticas mostram dados corretos
  - [ ] Dark mode funciona (botão no topo)
  - [ ] Navegação entre páginas funciona
  - [ ] Abrir Console (F12) → **sem erros vermelhos**

---

## 📋 Passo 6: Primeira Atualização de Dados

- [ ] 6.1 Garantir que tens dados recentes no projeto DEV
  - Base de dados em: `/home/diogo/Desktop/assiduidade_parlamento/database/base.db`

- [ ] 6.2 Executar script de atualização:
  ```bash
  cd /home/diogo/Desktop/assiduidade_parlamento_github_pages
  ./atualizar_dados.sh
  ```

- [ ] 6.3 Verificar output:
  - ✅ "📦 Copiando base de dados atualizada..."
  - ✅ "📊 Exportando dados para JSON..."
  - ✅ "✅ Mudanças detectadas nos dados JSON"
  - ✅ "💾 Fazendo commit das alterações..."
  - ✅ "🚀 Enviando para GitHub..."
  - ✅ "✅ Atualização concluída com sucesso!"

- [ ] 6.4 Aguardar 2-3 minutos
- [ ] 6.5 Refrescar GitHub Pages (Ctrl+Shift+R)
- [ ] 6.6 Verificar que dados foram atualizados

---

## 📋 Configuração Opcional: Domínio Personalizado

Se quiseres usar um domínio próprio (ex: `assiduidade.exemplo.pt`):

- [ ] 7.1 Comprar domínio (ex: GoDaddy, Namecheap, etc.)
- [ ] 7.2 No fornecedor do domínio, adicionar registos DNS:
  ```
  Tipo: A
  Nome: @
  Valor: 185.199.108.153
  
  Tipo: A
  Nome: @
  Valor: 185.199.109.153
  
  Tipo: A
  Nome: @
  Valor: 185.199.110.153
  
  Tipo: A
  Nome: @
  Valor: 185.199.111.153
  
  Tipo: CNAME
  Nome: www
  Valor: SEU_USER.github.io
  ```

- [ ] 7.3 No GitHub → Settings → Pages → Custom domain
- [ ] 7.4 Inserir domínio: `assiduidade.exemplo.pt`
- [ ] 7.5 Marcar "Enforce HTTPS"
- [ ] 7.6 Aguardar propagação DNS (até 48h, normalmente 1-2h)

---

## 🔧 Troubleshooting

### ❌ Erro: "Permission denied (publickey)"
**Solução**: Usar HTTPS em vez de SSH
```bash
git remote remove origin
git remote add origin https://github.com/SEU_USER/assiduidade-parlamento-pages.git
```

### ❌ GitHub pede password mas não aceita
**Solução**: Criar Personal Access Token
1. https://github.com/settings/tokens
2. "Generate new token" → "Classic"
3. Scopes: marcar `repo`
4. Copiar token (guarda num lugar seguro!)
5. Usar token como password no `git push`

### ❌ Página 404 no GitHub Pages
**Soluções**:
- Aguardar mais 2-3 minutos
- Verificar se branch está correto (main)
- Verificar se folder está correto (/frontend)
- Fazer novo commit e push para forçar rebuild

### ❌ Gráficos não aparecem
**Verificar**:
1. Console do browser (F12) → ver erros
2. `config.js` → confirmar `mode: 'static'`
3. Verificar se ficheiros JSON existem em `frontend/data/`
4. Testar localmente:
   ```bash
   cd frontend
   python3 -m http.server 8000
   ```
   Abrir http://localhost:8000/public.html

---

## 📊 Workflow Futuro (Atualizar Dados)

Quando houver novos dados:

1. ✅ Carregar CSV no projeto DEV (http://localhost:5001)
2. ✅ Executar:
   ```bash
   cd /home/diogo/Desktop/assiduidade_parlamento_github_pages
   ./atualizar_dados.sh
   ```
3. ✅ Aguardar 2-3 minutos
4. ✅ GitHub Pages atualiza automaticamente!

---

## ✅ Verificação Final

- [ ] GitHub Pages está online
- [ ] Todas as páginas funcionam (public, analise, atividade, landing)
- [ ] Dados estão corretos
- [ ] Dark mode funciona
- [ ] Sem erros no console
- [ ] Script de atualização funciona
- [ ] Consigo atualizar dados facilmente

---

**🎉 Parabéns! Sistema GitHub Pages configurado com sucesso!**

---

## 📞 Ajuda

Se precisares de ajuda:
- **Documentação completa**: `README.md`
- **Comandos rápidos**: `GUIA_RAPIDO.md`
- **Resumo técnico**: `RESUMO_IMPLEMENTACAO.md`
- **GitHub Docs**: https://docs.github.com/pages

---

**Data**: 14/11/2025  
**Versão**: 1.0
