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

# --- YENİ: GİZLİ YÖNETİCİ PANELİ (RANDEVULARI GÖRME EKRANI) ---
@app.route('/admin')
def admin():
    # Sayfa tasarımını doğrudan kodun içinde oluşturuyoruz
    html_icerik = """
    <html>
    <head>
        <meta charset="utf-8">
        <title>Randevu Listesi</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; background-color: #f4f4f9; }
            h1 { color: #333; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; background-color: #fff; }
            th, td { padding: 12px; text-align: left; border: 1px solid #ddd; }
            th { background-color: #4CAF50; color: white; }
            tr:nth-child(even) { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h1>📋 Yusuf Kırçalı - Randevu Listesi</h1>
        <table>
            <tr>
                <th>Berber</th>
                <th>Ad Soyad</th>
                <th>Telefon</th>
                <th>Tarih</th>
                <th>Saat</th>
                <th>Kayıt Zamanı</th>
            </tr>
    """
    
    # CSV dosyasındaki verileri satır satır tabloya ekle
    try:
        if os.path.exists(CSV_PATH):
            with open(CSV_PATH, mode="r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)  # Başlık satırını atla ki tabloda iki defa çıkmasın
                for row in reader:
                    if len(row) == 6: # Boş satırları engellemek için kontrol
                        html_icerik += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td></tr>"
    except Exception as e:
        html_icerik += f"<tr><td colspan='6'>Veriler okunurken hata oluştu: {e}</td></tr>"

    html_icerik += """
        </table>
    </body>
    </html>
    """
    return html_icerik

# --- DOLU SAATLERİ CSV'DEN ANINDA OKUYAN ROTA ---
@app.route('/get-booked-slots')
def get_booked_slots():
    try:
        date_str = request.args.get('date')
        if not date_str:
            return jsonify([])

        dolu_saatler = []
        if os.path.exists(CSV_PATH):
            with open(CSV_PATH, mode="r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["tarih"] == date_str and row["berber"] == "Yusuf Kırçalı":
                        dolu_saatler.append(row["saat"])

        return jsonify(dolu_saatler)
    except Exception as e:
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

        with open(CSV_PATH, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Yusuf Kırcalı", ad_soyad, telefon, tarih, saat, 
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])

        return jsonify({"status": "success", "message": "Randevunuz saniyeler içinde başarıyla oluşturuldu!"})

    except Exception as e:
        return jsonify({"status": "error", "message": f"Sistem Hatası: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
