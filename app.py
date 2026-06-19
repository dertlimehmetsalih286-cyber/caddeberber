from flask import Flask, render_template, request, jsonify, send_from_directory
import datetime
import os
import gspread
from google.oauth2.service_account import Credentials
import traceback

app = Flask(__name__)

# =======================================================
# YIKILMAZ KASA: GOOGLE E-TABLOLAR BAĞLANTISI
# =======================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. BURAYA KOPYALADIĞIN O E-TABLONUN TAM LİNKİNİ YAPIŞTIR:
TABLO_LINKI = "https://docs.google.com/spreadsheets/d/1C9zWOAzoiYm8rTpuToZoKzy5lsiee3eWrjREpA_hwv4/edit?gid=0#gid=0"

# 2. BURAYA O ÇALIŞAN GÖMÜLÜ ŞİFRENİ YAPIŞTIR (Önceki app.py kodunda kullandığın şifrenin aynısı)
firebase_sifre = {
  # SÜSLÜ PARANTEZ İÇİNDEKİ HER ŞEYİ KENDİ ŞİFRENLE DEĞİŞTİR
  "type": "service_account",
  "project_id": "berber-21d8c",
  # ... (şifrenin devamı) ...
}

gc = None
sheet = None

try:
    kapsam = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    kimlik = Credentials.from_service_account_info(firebase_sifre, scopes=kapsam)
    gc = gspread.authorize(kimlik)
    
    # Verdiğin linkteki tablonun 1. Sayfasına bağlanır
    sheet = gc.open_by_url(TABLO_LINKI).sheet1
    print("BAŞARILI: Google E-Tablolar'a Zırhlı Bağlantı Kuruldu!")
except Exception as e:
    print(f"E-Tablo Bağlantı Hatası: {e}")

# =======================================================

@app.route('/logo.jpg')
def logo():
    return send_from_directory(BASE_DIR, 'logo.jpg')

@app.route('/')
def index():
    bugun = datetime.date.today().strftime("%Y-%m-%d")
    return render_template('index.html', bugun=bugun)

@app.route('/get-booked-slots')
def get_booked_slots():
    try:
        date_str = request.args.get('date')
        if not date_str or not sheet:
            return jsonify([])

        # Tüm Excel'i oku ve sadece istenen tarihteki dolu saatleri ayıkla
        tum_kayitlar = sheet.get_all_records()
        dolu_saatler = []
        
        for satir in tum_kayitlar:
            if str(satir.get("Tarih")) == str(date_str) and satir.get("Berber") == "Yusuf Kırcalı":
                dolu_saatler.append(str(satir.get("Saat")))

        return jsonify(dolu_saatler)
    except Exception as e:
        print(f"Okuma Hatası: {e}")
        return jsonify([])

@app.route('/book', methods=['POST'])
def book():
    try:
        if not sheet:
            return jsonify({"status": "error", "message": "Tablo bağlantısı kurulamadı!"})

        data = request.json
        ad_soyad = data.get('ad_soyad')
        telefon = data.get('telefon')
        tarih = data.get('tarih')
        saat = data.get('saat')

        if not ad_soyad or not telefon or not tarih or not saat:
            return jsonify({"status": "error", "message": "Lütfen bilgileri eksiksiz doldurun."})

        kayit_zamani = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Veriyi anında Excel tablosunun en alt satırına ekler
        yeni_satir = ["Yusuf Kırcalı", ad_soyad, telefon, tarih, saat, kayit_zamani]
        sheet.append_row(yeni_satir)

        return jsonify({"status": "success", "message": "Randevunuz kalıcı olarak oluşturuldu!"})

    except Exception as e:
        hata_kodu = traceback.format_exc()
        print(hata_kodu)
        return jsonify({"status": "error", "message": "Sistem Hatası oluştu."})

if __name__ == '__main__':
    app.run(debug=True)
