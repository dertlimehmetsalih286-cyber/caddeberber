from flask import Flask, render_template, request, jsonify, send_from_directory
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import os

app = Flask(__name__)

# --- GÜVENLİ FIREBASE BAĞLANTISI ---
db = None
try:
    if not firebase_admin._apps:
        if os.path.exists("firebase-key.json"):
            firebase_admin.initialize_app(credentials.Certificate("firebase-key.json"))
        elif os.path.exists("firebase-key"):
            firebase_admin.initialize_app(credentials.Certificate("firebase-key"))
    if firebase_admin._apps:
        db = firestore.client()
except Exception as e:
    print(f"Firebase Hatası: {e}")

TUM_SAATLER = [
    "08:30 - 09:30", "09:30 - 10:30", "10:30 - 11:30", "11:30 - 12:30",
    "12:30 - 13:30", "13:30 - 14:30", "14:30 - 15:30", "15:30 - 16:30",
    "16:30 - 17:30", "17:30 - 18:30", "18:30 - 19:30", "19:30 - 20:30"
]

@app.route('/logo.jpg')
def logo():
    return send_from_directory(os.getcwd(), 'logo.jpg')

@app.route('/')
def index():
    bugun = datetime.date.today().strftime("%Y-%m-%d")
    return render_template('index.html', bugun=bugun)

# --- ZIRHLI SAAT HESAPLAMA ROTASI ---
@app.route('/get-slots')
def get_slots():
    try:
        date_str = request.args.get('date')
        if not date_str:
            return jsonify(TUM_SAATLER)

        dolu_saatler = []
        if db:
            randevular = db.collection("Randevular").where("tarih", "==", date_str).where("berber", "==", "Yusuf Kırçalı").stream()
            for r in randevular:
                dolu_saatler.append(r.to_dict().get("saat", ""))

        musait_saatler = [s for s in TUM_SAATLER if s not in dolu_saatler]
        return jsonify(musait_saatler)
    except Exception as e:
        # Sistem hata verse bile çökmeyecek, tüm saatleri açık gösterecek
        print(f"Saat hesaplama hatasi: {e}")
        return jsonify(TUM_SAATLER)

# --- ZIRHLI KAYIT ROTASI ---
@app.route('/book', methods=['POST'])
def book():
    try:
        if not db:
            return jsonify({"status": "error", "message": "Veritabanı bağlantısı kapalı! Lütfen şifre dosyanızı (firebase-key.json) kontrol edin."})
        
        data = request.json
        ad_soyad = data.get('ad_soyad')
        telefon = data.get('telefon')
        tarih = data.get('tarih')
        saat = data.get('saat')
        
        if not ad_soyad or not telefon or not tarih or not saat:
            return jsonify({"status": "error", "message": "Lütfen bilgileri eksiksiz doldurun."})
            
        db.collection("Randevular").add({
            "berber": "Yusuf Kırçalı",
            "ad_soyad": ad_soyad,
            "telefon": telefon,
            "tarih": tarih,
            "saat": saat,
            "kayit_zamani": datetime.datetime.now()
        })
        
        # Patron Numarasına SMS Çıktısı
        print(f"SMS GÖNDERİLİYOR -> Tel: +905339740664 | Mesaj: YENİ RANDEVU: {ad_soyad}, {tarih} saat {saat} için randevu oluşturdu.")
        
        return jsonify({"status": "success", "message": "Randevunuz başarıyla oluşturuldu!"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Sistemsel bir hata oluştu: {e}"})

if __name__ == '__main__':
    app.run(debug=True)
