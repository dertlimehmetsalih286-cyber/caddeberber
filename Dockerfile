# 1. Temel imaj olarak hızlı ve hafif bir Node.js versiyonu (Alpine) kullanıyoruz
FROM node:20-alpine

# 2. Konteyner içindeki çalışma klasörümüzü ayarlıyoruz
WORKDIR /app

# 3. Sadece paket dosyalarını kopyalayıp bağımlılıkları kuruyoruz (Önbelleği verimli kullanmak için)
COPY package*.json ./
RUN npm install

# 4. Projedeki tüm kodları (src, server vb.) konteynere kopyalıyoruz
COPY . .

# 5. Vite (Frontend) projesini derliyoruz (dist klasörünü oluşturur)
RUN npm run build

# 6. Sistemin dışarıya açılacağı portu belirtiyoruz
EXPOSE 3000

# 7. Backend sunucusunu ayağa kaldıran ana komut
CMD ["npx", "tsx", "server/index.ts"]
