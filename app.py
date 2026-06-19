from flask import Flask, render_template, request, jsonify, send_from_directory
import datetime
import os
import csv

app = Flask(__name__)

# --- ŞİMŞEK HIZINDA YEREL CSV VERİTABANI AYARI ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "randevular.csv")

# Eğer randevular.csv dosyası sunucuda yoksa, başlıklarıyla birlikte otomatik oluştur
if not os.path.exists(CSV_PATH):
    with open(CSV_PATH, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["berber", "ad_soyad", "telefon", "tarih", "saat", "kayit_zamani"])

@app.route('/logo.jpg')
def logo():
    return send_from_directory(BASE_DIR, 'logo.jpg')

@app.route('/')
def index():
    bugun = datetime.date.today().strftime("%Y-%m-%d")
    return render_template('index.html', bugun=bugun)

# --- DOLU SAATLERİ CSV'DEN ANINDA OKUYAN ROTA ---
@app.route('/get-booked-slots')
def get_booked_slots():
    try:
        date_str = request.args.get('date')
        if not date_str:
            return jsonify([])

        dolu_saatler = []
        
        # CSV dosyasını satır satır oku, seçilen tarihteki dolu saatleri listeye ekle
        if os.path.exists(CSV_PATH):
            with open(CSV_PATH, mode="r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["tarih"] == date_str and row["berber"] == "Yusuf Kırçalı":
                        dolu_saatler.append(row["saat"])

        return jsonify(dolu_saatler)
    except Exception as e:
        print(f"CSV Okuma Hatası: {e}")
        return jsonify([])

# --- RANDEVUYU CSV'YE ANINDA YAZAN ROTA ---
@app.route('/book', methods=['POST'])
def book():
    try:
        data = request.json
        ad_soyad = data.get('ad_soyad')
        telefon = data.get('telefon')
        tarih = data.get('tarih')
        saat = data.get('saat')

        if not ad_soyad or not telefon or not tarih or not saat:
            return jsonify({"status": "error", "message": "Lütfen bilgileri eksiksiz doldurun."})

        # Veriyi dışarıya göndermeden, yerel CSV dosyasına saniyesinde ekliyoruz
        with open(CSV_PATH, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Yusuf Kırçalı",
                ad_soyad,
                telefon,
                tarih,
                saat,
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])

        print(f"YENİ RANDEVU BAŞARILI (CSV): {ad_soyad} | {tarih} | {saat}")
        return jsonify({"status": "success", "message": "Randevunuz saniyeler içinde başarıyla oluşturuldu!"})

    except Exception as e:
        return jsonify({"status": "error", "message": f"Sistem Hatası: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
