# 1. Kırpılmış Alpine YERİNE, tam uyumlu ve sağlam node:20-slim kullanıyoruz
FROM node:20-slim

WORKDIR /app

COPY package*.json ./

# 2. Sürüm çakışmalarını yoksayan ve hafızayı koruyan ZIRHLI kurulum komutu
RUN npm install --legacy-peer-deps --no-audit --no-fund

COPY . .

# 3. Vite projesini derliyoruz
RUN npm run build

EXPOSE 3000

CMD ["npx", "tsx", "server/index.ts"]
