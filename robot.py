import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import os

# ==========================================
# 1. VERİTABANI BAĞLANTISI
# ==========================================
if not firebase_admin._apps:
    if os.path.exists("firebase-key.json"):
        cred = credentials.Certificate("firebase-key.json")
        firebase_admin.initialize_app(cred)
    elif os.path.exists("firebase-key"):
        cred = credentials.Certificate("firebase-key")
        firebase_admin.initialize_app(cred)

db = firestore.client()

# ==========================================
# 2. TARİH HESAPLAMA (YARININ TARİHİ)
# ==========================================
bugun = datetime.date.today()
yarin = bugun + datetime.timedelta(days=1)
yarin_str = yarin.strftime("%Y-%m-%d")

# ==========================================
# 3. VERİLERİ ÇEKME VE SIRALAMA
# ==========================================
berber_adi = "Yusuf Kırçalı"
randevular_ref = db.collection("Randevular")\
                   .where("tarih", "==", yarin_str)\
                   .where("berber", "==", berber_adi)\
                   .stream()

yarin_listesi = []
for r in randevular_ref:
    yarin_listesi.append(r.to_dict())

# Saatlere göre sırala
yarin_listesi.sort(key=lambda x: x.get("saat", ""))

# ==========================================
# 4. TOPLU SMS METNİ OLUŞTURMA
# ==========================================
patron_numara = "+905339740664"

if len(yarin_listesi) == 0:
    mesaj = f"Yusuf Hocam Selam, {yarin_str} (Yarın) günü için henüz hiçbir randevu kaydı bulunmamaktadır."
else:
    mesaj = f"Yusuf Hocam Selam! {yarin_str} (Yarın) Randevu Programın:\n\n"
    for r in yarin_listesi:
        mesaj += f"⏰ {r.get('saat')}\n👤 {r.get('ad_soyad')}\n📞 {r.get('telefon')}\n"
        mesaj += "-------------------\n"

# ==========================================
# 5. SMS GÖNDERME KOMUTU
# ==========================================
print(f"ROBOT ÇALIŞTI -> Tel: {patron_numara}\nMesaj:\n{mesaj}")
