#!/bin/bash
# Script para atualizar dados do GitHub Pages
# Executa exportação JSON → commit → push

set -e  # Sair em caso de erro

echo "🔄 Iniciando atualização de dados para GitHub Pages..."

# Diretório do projeto GitHub Pages
GITHUB_PAGES_DIR="/home/diogo/Desktop/assiduidade_parlamento_github_pages"
cd "$GITHUB_PAGES_DIR"

# 1. Copiar base de dados atualizada do projeto de desenvolvimento
echo "📦 Copiando base de dados atualizada..."
cp /home/diogo/Desktop/assiduidade_parlamento/database/base.db database/base.db

# 2. Exportar dados para JSON
echo "📊 Exportando dados para JSON..."
python3 export_to_json.py

if [ $? -ne 0 ]; then
  echo "❌ Erro ao exportar dados!"
  exit 1
fi

# 3. Verificar se há mudanças
if ! git diff --quiet data/; then
  echo "✅ Mudanças detectadas nos dados JSON"
  
  # 4. Fazer commit das mudanças
  DATA_ATUAL=$(date '+%Y-%m-%d %H:%M:%S')
  echo "💾 Fazendo commit das alterações..."
  git add data/*.json
  git commit -m "📊 Atualização automática de dados - $DATA_ATUAL"
  
  # 5. Push para GitHub
  echo "🚀 Enviando para GitHub..."
  git push origin main
  
  echo ""
  echo "✅ Atualização concluída com sucesso!"
  echo "📅 Data: $DATA_ATUAL"
  echo "🌐 Os dados estarão disponíveis no GitHub Pages em alguns minutos."
else
  echo "ℹ️  Sem mudanças nos dados. Nada a atualizar."
fi
