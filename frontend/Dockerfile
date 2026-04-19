FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf.template
EXPOSE 3000

# Comando para depuração e substituição de variáveis
CMD ["/bin/sh", "-c", "echo '🔍 Inspecionando variáveis...' && env | grep BACK || echo '❌ Nenhuma variável BACK encontrada' && export BACKEND_URL=${BACKEND_URL:-http://127.0.0.1} && envsubst '${PORT} ${BACKEND_URL}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf && echo '✅ Configuração gerada!' && exec nginx -g 'daemon off;'"]



