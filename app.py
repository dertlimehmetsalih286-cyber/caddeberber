from flask import Flask, render_template, request, jsonify, send_from_directory
import datetime
import os
import gspread
from google.oauth2.service_account import Credentials
import traceback
import json

app = Flask(__name__)

# =======================================================
# YIKILMAZ KASA: GOOGLE E-TABLOLAR BAĞLANTISI
# =======================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. BURAYA KOPYALADIĞIN O E-TABLONUN TAM LİNKİNİ YAPIŞTIR:
TABLO_LINKI = "https://docs.google.com/spreadsheets/d/1C9zWOAzoiYm8rTpuToZoKzy5lsiee3eWrjREpA_hwv4/edit?gid=0#gid=0"

# 2. ŞİFRENİ AŞAĞIDAKİ ÜÇ TIRNAK ARASINA OLDUĞU GİBİ YAPIŞTIR (Boşluk kayma hatası vermez)
sifre_metni = """
-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDcNQc28uh2vkEn\n5cuQ7uim13b4ZcRmiku4uc/GZ01Tz1yoJzqK2UjZfuevQid/4N9BKtxcz6kY8RTO\nlBeljU8YR+T9c/DGt2cREqBoiYPPhkIsIulOb8P8+z9EdPwUMW68tGz5xMOEaqKJ\ncKs+o3XkzGr5+1YmgoKVC6xwqIvSbyYKHeZr2bCTNf5f7pv5OmNdNA8eSWOYxUYT\nyQJjowX/1Vq0FQF6knQpyVDEcnt7F+LeeHcvg33U5+GpbmJsZOWb+cL8dd2fr7Bl\n+AQ9ppR8xmWpzqr++7EUjMdsPz/Vi1bMl86jG/I/37WEEzlThNojmEPbceTUCbRo\nMHhiln8HAgMBAAECggEARrzAGw4vz8kxC/x9BotAcCwB2yxxyVC+n1INJRpVFEml\n5ZxoaWcASGHEUh/JqYIWpYv7qtLIaqsy+GNJL1Sz5kReEm72lxceRDU8Eyitj3H8\n+smiMaCkkDUzby23NlNk07iP0zI6bmSE3uqzD9WZjwx9ht0OoSNGiFNuKuhxtgCG\n2eRn8P1u0vopbwYSjp/xfir3RJwbLtRbB59yk9HpPfvYK2H0MJqM9mwIi9WqKJEF\n8+082qogCy3Z8ucN1JUDGqY73hGSr4CpDpU0vxp51iW4+XO7Z6Aq7rHRB8Gc4nGr\nZcO8aI6fOlbFm+m7KlM8pe0Ej5tYMKnz+rhV2LZdnQKBgQD0AL6Pv63V+EqwmpWk\nJPj2NyQ6OSE3XBhPbt1a5gfPGl6CcoypTaUzS3pLeemYcXvccst58EnVGG25SMdA\nnTEDjzo7exGT/rtHtSxivJIu186sZ+VLfRZVtfe0YwdqJ7M01PiCoTQXzcjUK5FF\nUWVSUz7EPdVkndsQN8hdYyKc3QKBgQDnCMRyDuzAYICYGNtV1Id3i1Au+238f1GH\nCIF4VKOfVA8fnub5J+0R96HQHFR3AS4qJcPgjnRXU7BiT6ctiT9nBK0D8SAVsS8o\n3ZDNcN4aYMwtTIfq+qghVlEHqMyTNJCp7H6BUdoKxTD7hJ7Io4G94CZMdOs1mnh+\nbIKVTabLMwKBgBZ1OxTf/5ACGl3G3J8PCBshWCRDvdrqjxJAkf8bzPwy4SAAixHK\nI7pk6AyqW+W8DDpuFmxSwXjrlq3HFQ/NaAV72VBAM437lCE1e7Baytmk41Da/y/D\ng5q/9NyVgMk0fjoOoBDl5XWLa0CcAfLvWvQI1W4agtmP7enAOKDfzv/BAoGBAL8N\n7QY1eWuNYkplI9zSqEQfnOt9WPMZhp4YVpjfxX+Yz/jiOzeH4PCey92B0AepnjeU\ni2tD4snkl1R1clahzSCwKTO9Tz8hC1LMB1cdI07FBZPgWfXj2u3Wp6Oh36tMKOWc\ngPEIczu83kjg3z4kmMIgfwtzFJ97YnGJ4mL9mBUpAoGAGu9MN/jy48sbM04a1EDe\nPF/kVO4UMRfY+Ciw1hnbwlrgd8KrJG5lLFkjoqp/0iRGGHf67Q3lj2CF1vlheQcU\nMlGIvP83F4Cp2JqYc8pkKxWWK3AdpWeSw7c92c48TaQA4i35xscq/9eZG4YmWXmr\ne4Zcl5GPpc9bKTONuB7N/8c=\n-----END PRIVATE KEY-----\n
"""

gc = None
sheet = None

try:
    # Metin olarak aldığımız şifreyi güvenle sisteme tanıtıyoruz
    firebase_sifre = json.loads(sifre_metni)
    
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
        
        yeni_satir = ["Yusuf Kırcalı", ad_soyad, telefon, tarih, saat, kayit_zamani]
        sheet.append_row(yeni_satir)

        return jsonify({"status": "success", "message": "Randevunuz kalıcı olarak oluşturuldu!"})

    except Exception as e:
        hata_kodu = traceback.format_exc()
        print(hata_kodu)
        return jsonify({"status": "error", "message": "Sistem Hatası oluştu."})

if __name__ == '__main__':
    app.run(debug=True)
