from flask import Flask, render_template, request, jsonify, send_from_directory
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import os

app = Flask(__name__)

# ==========================================
# 1. GÜVENLİ FIREBASE BAĞLANTISI
# ==========================================
db = None
if not firebase_admin._apps:
    try:
        if os.path.exists("firebase-key.json"):
            firebase_admin.initialize_app(credentials.Certificate("firebase-key.json"))
        elif os.path.exists("firebase-key"):
            firebase_admin.initialize_app(credentials.Certificate("firebase-key"))
    except Exception as e:
        print(f"Firebase Baglanti Hatasi: {e}")

if firebase_admin._apps:
    try:
        db = firestore.client()
    except Exception as e:
        print(f"Firestore Client Hatasi: {e}")

# 1'er saatlik net çalışma şablonu
TUM_SAATLER = [
    "08:30 - 09:30", "09:30 - 10:30", "10:30 - 11:30", "11:30 - 12:30",
    "12:30 - 13:30", "13:30 - 14:30", "14:30 - 15:30", "15:30 - 16:30",
    "16:30 - 17:30", "17:30 - 18:30", "18:30 - 19:30", "19:30 - 20:30"
]

# Ana dizindeki logoyu HTML'e servis eden gizli rota
@app.route('/logo.jpg')
def logo():
    return send_from_directory(os.getcwd(), 'logo.jpg')

# ==========================================
# 2. SAYFA ROTALARI VE İŞLEMLERİ
# ==========================================
@app.route('/')
def index():
    bugun = datetime.date.today().strftime("%Y-%m-%d")
    return render_template('index.html', bugun=bugun)

# Seçilen tarihe göre dolu olmayan saatleri anlık döndüren robot rota
@app.route('/get-slots')
def get_slots():
    date_str = request.args.get('date')
    if not date_str:
        return jsonify([])
    
    dolu_saatler = []
    if db:
        try:
            randevular = db.collection("Randevular").where("tarih", "==", date_str).where("berber", "==", "Yusuf Kırçalı").stream()
            for r in randevular:
                dolu_saatler.append(r.to_dict().get("saat"))
        except Exception as e:
            print(f"Veri cekme hatasi: {e}")
            
    musait_saatler = [s for s in TUM_SAATLER if s not in dolu_saatler]
    return jsonify(musait_saatler)

# Randevu Kayıt Rotası
@app.route('/book', methods=['POST'])
def book():
    if not db:
        return jsonify({"status": "error", "message": "Veritabanı bağlantısı kapalı! Şifre dosyasını kontrol edin."})
    
    data = request.json
    ad_soyad = data.get('ad_soyad')
    telefon = data.get('telefon')
    tarih = data.get('tarih')
    saat = data.get('saat')
    
    if not ad_soyad or not telefon or not tarih or not saat:
        return jsonify({"status": "error", "message": "Lütfen alanları eksiksiz doldurun."})
        
    try:
        db.collection("Randevular").add({
            "berber": "Yusuf Kırçalı",
            "ad_soyad": ad_soyad,
            "telefon": telefon,
            "tarih": tarih,
            "saat": saat,
            "kayit_zamani": datetime.datetime.now()
        })
        # Patron Telefonuna SMS Bildirim Çıktısı
        print(f"SMS GÖNDERİLİYOR -> Tel: +905339740664 | Mesaj: YENİ RANDEVU: {ad_soyad}, {tarih} saat {saat} için randevu oluşturdu. Tel: {telefon}")
        return jsonify({"status": "success", "message": f"Randevunuz başarıyla oluşturuldu!"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Sistemsel hata oluştu: {e}"})

if __name__ == '__main__':
    app.run(debug=True)
