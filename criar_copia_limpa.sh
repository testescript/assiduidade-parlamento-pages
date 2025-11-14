#!/bin/bash

# Script para criar cópia limpa do projeto (sem arquivos temporários)

ORIGEM="/home/diogo/Desktop/assiduidade_parlamento"
DESTINO="/home/diogo/Desktop/assiduidade_parlamento_github_pages"

echo "🚀 Criando cópia limpa do projeto..."
echo "📂 Origem: $ORIGEM"
echo "📂 Destino: $DESTINO"

# Criar diretório de destino
mkdir -p "$DESTINO"

# Copiar usando rsync (exclui arquivos temporários e git)
rsync -av --progress \
  --exclude='.git' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='*.pyo' \
  --exclude='*.pyd' \
  --exclude='.Python' \
  --exclude='venv/' \
  --exclude='env/' \
  --exclude='ENV/' \
  --exclude='*.egg-info' \
  --exclude='.eggs/' \
  --exclude='database/*.db' \
  --exclude='database/*.db-journal' \
  --exclude='database/*.db-wal' \
  --exclude='database/*.db-shm' \
  --exclude='uploads/*' \
  --exclude='.vscode/' \
  --exclude='.idea/' \
  --exclude='*.swp' \
  --exclude='*.swo' \
  --exclude='*~' \
  --exclude='.DS_Store' \
  --exclude='*.log' \
  --exclude='.env' \
  --exclude='.cache/' \
  --exclude='*.tmp' \
  "$ORIGEM/" "$DESTINO/"

echo ""
echo "✅ Cópia criada com sucesso!"
echo ""
echo "📊 Estrutura copiada:"
du -sh "$DESTINO"
echo ""
echo "🎯 Próximos passos:"
echo "1. cd $DESTINO"
echo "2. Vamos configurar para GitHub Pages"
