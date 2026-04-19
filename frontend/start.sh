#!/bin/sh

echo "🚀 Iniciando CloudCost IQ Dashboard..."
echo "🔍 Inspecionando variaveis..."

env | grep BACK || echo "Nenhuma variavel BACK encontrada"

# Define fallback se BACKEND_URL estiver vazia
export BACKEND_URL=${BACKEND_URL:-http://127.0.0.1}

echo "⚙️ Gerando configuracao do Nginx..."
envsubst '${PORT} ${BACKEND_URL}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

echo "✅ Configuracao gerada! Iniciando Nginx..."
exec nginx -g 'daemon off;'
