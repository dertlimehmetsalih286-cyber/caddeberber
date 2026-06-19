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

# Senin verdiğin tablo linki tam olarak buraya eklendi!
TABLO_LINKI = "https://docs.google.com/spreadsheets/d/1C9zWOAzoiYm8rTpuToZoKzy5lsiee3eWrjREpA_hwv4/edit"

# Gönderdiğin o kusursuz çalışan şifre dosyası
firebase_sifre = {
  "type": "service_account",
  "project_id": "berber-21d8c",
  "private_key_id": "92e58e6fa72dba1966cb00d6c7f50daa638eedfc",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDi5ZH2GUWgnPoY\nY6fhpu4Zzl6hwcRqFOOqItkQtU+JGo35Vm0QaJ2Sstb3VLezBkOdLnH0h2bfdq2N\nnxiw6ejLuYEMXi3vlad3ZBFG9IlL/mKcAxCdr68iZWbVm+C8EVJQ7Aotm+DVEXUV\nVDfHm1SzGVuQ/bRlVwS2zQ/NguXGOJ8kdMaqaGi9y2cNd/MREpt0tm0LQYFTA/rh\nGBTGFwobXn5QmGwOsFjlH4JA23mLQzCv26nqGwBXQyCX3eqw722F4FvQchYeNT2g\nWPNptfwiIE4X78PjtTvmM4S+Qu1ZZy/1FZ3alhDwAhcyFp2kd2j9wobYrWGY6/Sd\nSx7gJZyXAgMBAAECggEABmWIDeYWGAcU54C3u1BxDS0yO2EyrMLvmcMairJx2y2l\nq84+v0p6I46cwz0SLx8RsB0esIQfGrtGMH3rVkfh4wxukbvkYG+M2K+euEXG/et4\nBp0kTmDx926tM+YNgEyeUEW3RVd/QsJ+CIUaGKuz+zCcOKQ0yvHL4jnTV9N4fHQP\nZHFcPddRC97ZYM/rnKSFzk0aEOUhWuthUhhJEM9XWzlMv8Dz68VK6a+eJwxJAjs2\n7xJ3926DnvoBlyAZ9xdsMjHaPSHSgLwGWtxomnFwCTfHdVOTQalto2R5fo7PmO5o\ngrfBZXepVNfrEGoCX2ysCsisqrDtPFqTjF5fhHqdEQKBgQD8SLOBwHHFkteddEs2\noXeN1x0deiYeaRr/XS+9bxrFB+UPnWrAm+CIimR7d0ZYtJE3yeJ0hpa1qxsoJVIS\nZub0ILPAbVbB5UPOEm3NpZVCsgsoYqogJvPCqq6IEecGtNnWdeas6Z9+Vx7vqXOA\neqBGdcvg2ZG2uLcnMZXILP9NYwKBgQDmPSPiGBTUt8wZAuieGMtR8v2+BprTP++Z\nmYWVGIXAexSQ3GYw6xQOWSkelSWb3LSU/GRPAhJOdNcHiDQ8YnLf7QKJPPeTfntJ\n6PvndpXEboA9/x5uFR3LekxjSPFbH2y6Kksiw3r6nLRj1/cjLBQso1qnFQBMbGXP\nZVh3D0zkPQKBgAIAcawt4rk2mQ9exNoCHfi6JDj/px3Gp7gu/Rn7r7KwhVjCXv54\nPifXMUTphV1e0Wgn6ewSxU9btDN1WFldB6gYOlTkiTOwpgEUlFp1XeHRl9USM1dd\n98ErqYba3YJoHPJerR3iHKnb9xrftVLnpi3o8V0vXMCeZpWhBxc3hC8RAoGAMtEx\n11hbWKwMl0SmFScB0V+hk8yfZZsKBkv1SPg1pUtFOcf7ojZwoc4aHk7rEyC+ltey\nSCH76mctgtMUPHO6SSRl1+al+l8DVUfgObFZ0xZUpdpmXAO7JMskixFxfBxOgjSN\nium8fg4SXqsvOAsllMilXJVtEHEoc4M56GVvIj0CgYBQ+2dbTbwwK0XN8Ds9JXN3\nrv7ATw/zrX0PI+Ix3nGfYy1eYCwenKcIlAwhVV4+0oetZc3f+yEpMpRfY7JIl8YA\nRo16XyA2FWR88SBi2xLN5re/RhoOyKIG0KXNCiOY5IiIHpks9rB+1wJ47ICt4+Uo\nzU36ZNDQakz8ulsp8Igbhg==\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@berber-21d8c.iam.gserviceaccount.com",
  "client_id": "107713882295228539995",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40berber-21d8c.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
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
