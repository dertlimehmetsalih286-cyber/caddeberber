import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import os
import base64

# ==========================================
# 0. SAYFA AYARLARI VE ARKA PLAN
# ==========================================
st.set_page_config(page_title="Cadde Erkek Kuaförü", page_icon="✂️", layout="centered")

if os.path.exists("logo.jpg"):
    try:
        with open("logo.jpg", "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <style>
            .stApp {{
                background-image: url("data:image/jpeg;base64,{img_data}");
                background-size: cover; background-position: center; background-attachment: fixed;
            }}
            .stApp::before {{
                content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                background-color: rgba(30, 20, 15, 0.85); z-index: -1;
            }}
            #MainMenu, header {{visibility: hidden;}}
            .block-container {{padding-top: 2rem; max-width: 600px;}}
            p, label, h1, h4 {{color: #F5DEB3 !important; text-align: center;}}
            div[data-baseweb="input"] > div > input {{ font-size: 1.2rem !important; padding: 12px !important; text-align: center; }}
            div[data-baseweb="select"] > div {{ font-size: 1.2rem !important; padding: 8px !important; text-align: center; }}
            .stButton > button {{background-color: #8D6E63 !important; color: white !important; border-radius: 8px; border: none; padding: 15px 20px; font-size: 1.2rem; font-weight: bold; width: 100%; margin-top: 20px;}}
            </style>
        """, unsafe_allow_html=True)
    except:
        pass

# ==========================================
# 1. GÜVENLİ VERİTABANI BAĞLANTISI
# ==========================================
db = None
if not firebase_admin._apps:
    try:
        if os.path.exists("firebase-key.json"):
            firebase_admin.initialize_app(credentials.Certificate("firebase-key.json"))
        elif os.path.exists("firebase-key"):
            firebase_admin.initialize_app(credentials.Certificate("firebase-key"))
    except:
        pass

if firebase_admin._apps:
    try:
        db = firestore.client()
    except:
        pass

# ==========================================
# 2. EKRAN BİLEŞENLERİ (ZORUNLU SIRALAMA)
# ==========================================
st.markdown("<h1>✂️ Yusuf Kırçalı</h1>", unsafe_allow_html=True)
st.markdown("<h4>Cadde Erkek Kuaförü Randevu Sistemi</h4>", unsafe_allow_html=True)
st.write("")

# PENCERE 1: TARİH
bugun = datetime.date.today()
bir_ay_sonra = bugun + datetime.timedelta(days=30)
secilen_tarih = st.date_input("📅 Tarih Seçin", value=bugun, min_value=bugun, max_value=bir_ay_sonra)
tarih_str = secilen_tarih.strftime("%Y-%m-%d")

# Saat Şablonu
tum_saatler = [
    "08:30 - 09:30", "09:30 - 10:30", "10:30 - 11:30", "11:30 - 12:30",
    "12:30 - 13:30", "13:30 - 14:30", "14:30 - 15:30", "15:30 - 16:30",
    "16:30 - 17:30", "17:30 - 18:30", "18:30 - 19:30", "19:30 - 20:30"
]

dolu_saatler = []
if db:
    try:
        randevular = db.collection("Randevular").where("tarih", "==", tarih_str).where("berber", "==", "Yusuf Kırçalı").stream()
        for r in randevular:
            dolu_saatler.append(r.to_dict().get("saat"))
    except:
        pass

musait_saatler = [s for s in tum_saatler if s not in dolu_saatler]
if not musait_saatler:
    musait_saatler = ["⚠️ Bu Tarih Dolu!"]

# PENCERE 2: SAAT
st.write("")
secilen_saat = st.selectbox("⏰ Saat Seçin", musait_saatler)

# PENCERE 3: AD SOYAD VE TELEFON
st.write("")
ad_soyad = st.text_input("👤 Ad Soyad", placeholder="Örn: Ahmet Yılmaz")
telefon = st.text_input("📞 Telefon Numarası", placeholder="05XX XXX XX XX")

# ONAY BUTONU
randevu_btn = st.button("Randevu Oluştur")

# ==========================================
# 3. KAYIT TETİKLEYİCİSİ
# ==========================================
if randevu_btn:
    if secilen_saat == "⚠️ Bu Tarih Dolu!":
        st.error("🚨 Seçtiğiniz gün tamamen doludur. Lütfen başka bir gün seçin.")
    elif not ad_soyad or not telefon:
        st.warning("⚠️ Lütfen ad, soyad ve telefon bilgilerinizi eksiksiz girin.")
    elif not db:
        st.error("❌ Veritabanı bağlantısı şu an kapalı. Lütfen şifre dosyanızı kontrol edin.")
    else:
        try:
            db.collection("Randevular").add({
                "berber": "Yusuf Kırçalı",
                "ad_soyad": ad_soyad,
                "telefon": telefon,
                "tarih": tarih_str,
                "saat": secilen_saat,
                "kayit_zamani": datetime.datetime.now()
            })
            # Arka Plan SMS Gönderim Bildirimi
            print(f"SMS GÖNDERİLİYOR -> Tel: +905339740664 | Mesaj: YENİ RANDEVU: {ad_soyad}, {tarih_str} saat {secilen_saat} için randevu oluşturdu.")
            st.success(f"🎉 Harika! Randevunuz {tarih_str} günü saat {secilen_saat} aralığına başarıyla oluşturuldu.")
        except Exception as e:
            st.error(f"Kayıt işlenirken hata oluştu: {e}")
