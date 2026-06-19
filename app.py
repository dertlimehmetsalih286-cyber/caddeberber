from flask import Flask, render_template, request, jsonify, send_from_directory
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import os

app = Flask(__name__)

# ==========================================
# GÜVENLİ FIREBASE BAĞLANTISI VE OTOMATİK YOL BULUCU
# ==========================================
db = None
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(BASE_DIR, "firebase-key.json")

try:
    if not firebase_admin._apps:
        if os.path.exists(KEY_PATH):
            firebase_admin.initialize_app(credentials.Certificate(KEY_PATH))
        else:
            print(f"KRİTİK HATA: {KEY_PATH} dosyası sunucuda bulunamadı!")
            
    if firebase_admin._apps:
        db = firestore.client()
except Exception as e:
    print(f"Firebase Bağlantı Hatası: {e}")

# Saat Şablonu
TUM_SAATLER = [
    "08:30 - 09:30", "09:30 - 10:30", "10:30 - 11:30", "11:30 - 12:30",
    "12:30 - 13:30", "13:30 - 14:30", "14:30 - 15:30", "15:30 - 16:30",
    "16:30 - 17:30", "17:30 - 18:30", "18:30 - 19:30", "19:30 - 20:30"
]

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
    except Exception as e:
        return jsonify([])

@app.route('/book', methods=['POST'])
def book():
    try:
        if not db:
            return jsonify({"status": "error", "message": "Veritabanı bağlantısı kapalı! Lütfen firebase-key.json dosyasının GitHub'da olduğundan emin olun."})
        
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
        
        print(f"SMS GÖNDERİLİYOR -> Tel: +905339740664 | Mesaj: YENİ RANDEVU: {ad_soyad}, {tarih} saat {saat} için randevu oluşturdu.")
        return jsonify({"status": "success", "message": "Randevunuz başarıyla oluşturuldu!"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Sistemsel bir hata oluştu: {e}"})

if __name__ == '__main__':
    app.run(debug=True)
