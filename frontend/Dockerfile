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
CMD ["/bin/sh", "-c", "echo '⚙️ Gerando configuração do Nginx...' && export BACKEND_URL=${BACKEND_URL:-https://api.fallback.com} && envsubst '${PORT} ${BACKEND_URL}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf && echo '✅ Configuração gerada:' && cat /etc/nginx/conf.d/default.conf && exec nginx -g 'daemon off;'"]


