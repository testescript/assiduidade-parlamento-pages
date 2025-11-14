#!/bin/bash
# Script para levantar o sistema Assiduidade Parlamentar em ambiente local

# Ativar ambiente virtual
source venv/bin/activate

# Matar processos antigos nas portas 5001 (backend) e 8000 (frontend)
fuser -k 5001/tcp 2>/dev/null
fuser -k 8000/tcp 2>/dev/null

echo "🚀 A arrancar o backend Flask..."
cd backend
python app.py &
BACKEND_PID=$!
cd ..

echo "🌐 A arrancar o frontend (servidor estático)..."
cd frontend
python -m http.server 8000 &
FRONTEND_PID=$!
cd ..

echo "✅ Sistema levantado:"
echo "   Backend → http://127.0.0.1:5001"
echo "   Frontend → http://127.0.0.1:8000/public.html"
echo "   Landing → http://127.0.0.1:8000/landing.html"
echo "   Back-office → http://127.0.0.1:8000/index.html"

# Função para parar tudo ao sair
cleanup() {
  echo "🛑 A encerrar processos..."
  kill $BACKEND_PID 2>/dev/null
  kill $FRONTEND_PID 2>/dev/null
  deactivate
}
trap cleanup EXIT

# Mantém o script ativo até Ctrl+C
wait
