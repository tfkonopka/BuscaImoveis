#!/bin/bash

# Script para iniciar o Visualizador ITBI localmente
# Uso: ./iniciar.sh

echo "🚀 Iniciando Visualizador ITBI..."
echo "================================"

# Detectar sistema operacional
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="Linux"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    OS="Windows"
else
    OS="Desconhecido"
fi

echo "🖥️  Sistema: $OS"

# Procurar porta disponível
PORT=8888
while lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; do
    PORT=$((PORT + 1))
done

echo "🌐 Porta: $PORT"

# Iniciar servidor
echo "💾 Iniciando servidor local..."
python3 -m http.server $PORT > /tmp/itbi_server.log 2>&1 &
SERVER_PID=$!

# Aguardar servidor iniciar
sleep 2

# Verificar se servidor iniciou com sucesso
if kill -0 $SERVER_PID 2>/dev/null; then
    echo "✅ Servidor rodando (PID: $SERVER_PID)"
    echo ""
    echo "📂 Abrindo no navegador..."
    echo "🔗 http://localhost:$PORT/itbi_visualizer.html"
    echo ""

    # Abrir navegador automaticamente
    if command -v xdg-open &> /dev/null; then
        xdg-open "http://localhost:$PORT/itbi_visualizer.html"
    elif command -v open &> /dev/null; then
        open "http://localhost:$PORT/itbi_visualizer.html"
    elif command -v start &> /dev/null; then
        start "http://localhost:$PORT/itbi_visualizer.html"
    else
        echo "⚠️  Abra manualmente no navegador:"
        echo "   http://localhost:$PORT/itbi_visualizer.html"
    fi

    echo ""
    echo "📊 Dicas:"
    echo "  - Pressione Ctrl+C para parar o servidor"
    echo "  - O servidor salva em: /tmp/itbi_server.log"
    echo "  - Abra http://localhost:$PORT no navegador"
    echo ""
    echo "⏹️  Para parar: kill $SERVER_PID"
    echo ""

    # Manter servidor rodando
    wait $SERVER_PID
else
    echo "❌ Erro ao iniciar servidor"
    exit 1
fi
