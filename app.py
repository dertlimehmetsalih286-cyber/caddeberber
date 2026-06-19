from flask import Flask, render_template, request, jsonify, send_from_directory
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import os
import traceback

app = Flask(__name__)

# =======================================================
# HATA YAPMAYAN OTOMATİK DOSYA BULUCU VE VERİTABANI
# =======================================================
db = None
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    if not firebase_admin._apps:
        # Klasördeki tüm .json uzantılı dosyaları tara
        json_dosyalari = [f for f in os.listdir(BASE_DIR) if f.endswith('.json')]
        basarili_baglanti = False
        
        for dosya in json_dosyalari:
            try:
                tam_yol = os.path.join(BASE_DIR, dosya)
                cred = credentials.Certificate(tam_yol)
                firebase_admin.initialize_app(cred)
                db = firestore.client()
                basarili_baglanti = True
                print(f"BAŞARILI: {dosya} isimli orjinal şifreyle giriş yapıldı!")
                break  # Doğru dosyayı bulunca döngüyü bitir
            except Exception as e:
                continue # Bu dosya şifre değilse diğerine geç
                
        if not basarili_baglanti:
            print("KRİTİK HATA: Çalışan bir Firebase şifre dosyası bulunamadı!")
    else:
        db = firestore.client()
except Exception as e:
    print(f"Genel Başlatma Hatası: {e}")

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
            return jsonify({"status": "error", "message": "Veritabanına bağlanılamadı. Orjinal şifre dosyasının yüklendiğinden emin olun."})
        
        data = request.json
        db.collection("Randevular").add({
            "berber": "Yusuf Kırçalı",
            "ad_soyad": data.get('ad_soyad'),
            "telefon": data.get('telefon'),
            "tarih": data.get('tarih'),
            "saat": data.get('saat'),
            "kayit_zamani": datetime.datetime.now()
        })
        
        print(f"YENİ RANDEVU: {data.get('ad_soyad')} | {data.get('tarih')} | {data.get('saat')}")
        return jsonify({"status": "success", "message": "Randevunuz başarıyla oluşturuldu!"})
    
    except Exception as e:
        hata_kodu = traceback.format_exc()
        print(hata_kodu)
        return jsonify({"status": "error", "message": f"Sistem Hatası: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
