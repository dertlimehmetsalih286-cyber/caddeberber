from flask import Flask, render_template, request, jsonify, send_from_directory
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import os
import traceback

app = Flask(__name__)

# =======================================================
# NÜKLEER SEÇENEK: DOSYA YOK, PANEL YOK, DİREKT GÖMÜLÜ ŞİFRE
# =======================================================
db = None
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    if not firebase_admin._apps:
        # Şifreyi direkt kodun içine gömdük. Dosya bozulması, satır kayması imkansız.
        firebase_sifre = {
          "type": "service_account",
          "project_id": "rehberlik-sistemi-2e6dd",
          "private_key_id": "07fcd1d653d36121c035cc6e517d7f95ccf1357b",
          "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCt10thfQ14Drd5\nXvMRGoGzfyfIF2RxLapdCV7en0FThaHcDD4Ym9X1Qu2cHgIMouiD2mM6uXSOMRcU\nk8d6G4t8F9wqs+pxSB/M4RcIfSWDR/2daNwmLP0VyyhlSeaACQa4004ZtBbR8lBe\nnVXHKLiqoj/7MjWDi+iMVkS9k4LhU2pylCLr7a309p3G1r5BQbTePmh3C916I6Sq\ntCZJaGuw5AcJY0X+bCFPLI8SOG7mBpT/FgwerTGsc53lUCbXH87SiwFw+dbsL3da\nDxgy8rQnDxWaH0gXvIDNsMGi1S92Ucsha7rlsHaZF/Z/3mmMv0GNDxh0Lj3VAqjH\nyfd3Y6RHAgMBAAECggEAJ+azQCimZ0ildz/CdcoKPCty85ve65VqNZmZg2q1YVja\nWnoa5KYcOYPHqx4+JS1dRiphvVBk/uAopon27sGUxgJqAAk0xhSia/G8SjADZLso\n7LDtWvvXiWGMn5cTR48K0nB5zC+IT18ZcGYXkrN3k37TRbJ0EwIReeixNXw+vb35\nZHbfJEt/zIfVWhphBaPogeLd6om+RRQsvV5OnLhBEuJkQdJFZZnx103hMdmyI7QC\n28c37JspjwKsBPePFITPUcBmWzRpHTJbrPgOg9edHZKwCsa7KjO0o2X05pmW88k7\n6N4Hxr1HLRY6pOHiPwXpzA8t76AzQeHsw7mrHTWL4QKBgQDW4UC2fSEs1cIeEN5X\nNrDn+RonqY4Eszdfo6QeWfC8xZXBeqfh2kZzFnYsLSOaJxGqdcVKSi3twfCYRjLd\nmKa5lIpOaAE4qRamU+KGyYvNmhJ11tX3ra1N7LrkKgtpDADa+U3sMzAVJc78XtYl\n503yiCtXzvQku9gYTIDRKHAUIQKBgQDPG5Z3R3vcYgAO+1EKfHIdFLxgOpgZ2841\nqu61jqKDguGSjcumCe7W7xY+I7yVAUrDwUMlv5R52mQzd4UHnpywNg0nr6u7YPtX\nvJC6+PV5LbIDY7KXW1lgWauvZLcP+Jzc0nAmEusn5XAbaB4sXdoPbh14fZJXNtfl\nD4sH4aorZwKBgQDBzP70l/6n1VLykvw1ZJpBXiX8x6vTCWBT3d9TkILTftEGY32u\n8ZLAke2bAkst6TbBqt55llW+LkC01ftiaR9WGWZ0ONGBLN/Eu7t/HZ/9m4wyw8TP\nUdEQiwY0asdHww+yb0+cTL59FFCOxWoXXXqr16xf0cPYraLEp5s3CWWsgQKBgESL\nQt8zP2EO5ioPLyEjUrkhNb87ZT+ZqcPFUL+x90NDO9i/KRlIzE1CT8A9H5rJFK94\n9Po3T7KMfwExm0uMSRtgqDXsRA/95vGArP3Ui5mRcAsDIgZJ62iiBNpFoPieNXw4\nAXn4ZO+NVe8cJHBWl2bn8MUB+j73HbjnzgHLxAAdAoGAMvoMOh5ZssW6bhMM8dpr\n5hfO8+89xhMixaNhsypH2f+NR/ZSBzPmQabRUYCd7UvvmfuEOFajgphcS13vlROk\nJOVwJbMCtKSZtA3fyeDc5kgejN4vj2+Pi3jeGvn4Bf/mNwx7mYhtpH8VptuSJ6DQ\ni92rnM3LY9Ge9471+xVSWak=\n-----END PRIVATE KEY-----\n",
          "client_email": "firebase-adminsdk-fbsvc@rehberlik-sistemi-2e6dd.iam.gserviceaccount.com",
          "client_id": "107647683305147145690",
          "auth_uri": "https://accounts.google.com/o/oauth2/auth",
          "token_uri": "https://oauth2.googleapis.com/token",
          "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
          "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40rehberlik-sistemi-2e6dd.iam.gserviceaccount.com",
          "universe_domain": "googleapis.com"
        }
        
        cred = credentials.Certificate(firebase_sifre)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("BAŞARILI: Gömülü şifre ile veritabanı kilitleri açıldı!")
    else:
        db = firestore.client()
except Exception as e:
    print(f"Firebase Başlatma Hatası: {e}")

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
            return jsonify({"status": "error", "message": "Veritabanı bağlantısı kurulamadı."})
        
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
