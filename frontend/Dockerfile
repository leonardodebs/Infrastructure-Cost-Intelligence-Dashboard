FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/conf.d/default.conf.template
COPY start.sh /app/start.sh
RUN tr -d '\r' < /app/start.sh > /app/start.sh.tmp && mv /app/start.sh.tmp /app/start.sh && chmod +x /app/start.sh

EXPOSE 3000
CMD ["/app/start.sh"]






