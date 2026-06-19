from flask import Flask, render_template, request, jsonify, send_from_directory
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import os
import traceback
import json

app = Flask(__name__)

# --- OTOMATİK DOSYA OKUYUCU VE MÜHÜR TAMİRCİSİ ---
db = None
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(BASE_DIR, "firebase-key.json")

try:
    if not firebase_admin._apps:
        if os.path.exists(KEY_PATH):
            with open(KEY_PATH, "r", encoding="utf-8") as f:
                sifre_dosyasi = json.load(f)
            
            # Eğer GitHub dosyayı bozup satır atlamaları \n yazısına çevirdiyse, bunu düzelt:
            if "\\n" in sifre_dosyasi.get("private_key", ""):
                sifre_dosyasi["private_key"] = sifre_dosyasi["private_key"].replace("\\n", "\n")
                
            cred = credentials.Certificate(sifre_dosyasi)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            print("BAŞARILI: Doğru dosya bulundu ve kilit açıldı!")
        else:
            print("KRİTİK HATA: firebase-key.json dosyası bulunamadı!")
    else:
        db = firestore.client()
except Exception as e:
    print(f"Firebase Hatası: {e}")

# -------------------------------------------------

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
        if not date_str or not db:
            return jsonify([])

        dolu_saatler = []
        randevular = db.collection("Randevular").where("tarih", "==", date_str).where("berber", "==", "Yusuf Kırçalı").stream()
        for r in randevular:
            dolu_saatler.append(r.to_dict().get("saat", ""))
        return jsonify(dolu_saatler)
    except:
        return jsonify([])

@app.route('/book', methods=['POST'])
def book():
    try:
        if not db:
            return jsonify({"status": "error", "message": "Veritabanı bağlantısı kurulamadı. firebase-key.json dosyasını kontrol edin."})
        
        data = request.json
        db.collection("Randevular").add({
            "berber": "Yusuf Kırçalı",
            "ad_soyad": data.get('ad_soyad'),
            "telefon": data.get('telefon'),
            "tarih": data.get('tarih'),
            "saat": data.get('saat'),
            "kayit_zamani": datetime.datetime.now()
        })
        
        return jsonify({"status": "success", "message": "Randevunuz başarıyla oluşturuldu!"})
    
    except Exception as e:
        hata_kodu = traceback.format_exc()
        print(hata_kodu)
        return jsonify({"status": "error", "message": f"Sistem Hatası: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
