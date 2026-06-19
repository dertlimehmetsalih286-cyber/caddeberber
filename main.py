import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import os
import base64
st.set_page_config(page_title="Cadde Erkek Kuaförü", page_icon="✂️", layout="centered")
def arka_plan_ayarla():
    try:
        with open("logo.jpg", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        css = f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .stApp::before {{
            content: "";
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background-color: rgba(30, 20, 15, 0.85);
            z-index: -1;
        }}
        #MainMenu {{visibility: hidden;}} header {{visibility: hidden;}}
        .block-container {{padding-top: 2rem; max-width: 600px;}}
        p, label, h1, h2, h3, h4, h5, h6 {{color: #F5DEB3 !important; text-align: center;}}
        div[data-baseweb="input"] > div > input {{ font-size: 1.2rem !important; padding: 12px !important; text-align: center; }}
        div[data-baseweb="select"] > div {{ font-size: 1.2rem !important; padding: 8px !important; text-align: center; }}
        .stButton > button {{background-color: #8D6E63 !important; color: white !important; border-radius: 8px; border: none; padding: 15px 20px; font-size: 1.2rem; font-weight: bold; width: 100%; margin-top: 20px;}}
        .stButton > button:hover {{background-color: #6D4C41 !important;}}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    except Exception as e:
        st.markdown("<style>.stApp { background-color: #3E2723; color: #F5DEB3; } p, label, h1 { color: #F5DEB3 !important; text-align: center;}</style>", unsafe_allow_html=True)

arka_plan_ayarla()
FIREBASE_AKTIF = False
if not firebase_admin._apps:
    try:
        if os.path.exists("firebase-key.json"):
            cred = credentials.Certificate("firebase-key.json")
            firebase_admin.initialize_app(cred)
            FIREBASE_AKTIF = True
    except:
        pass
else:
    FIREBASE_AKTIF = True

try:
    db = firestore.client() if FIREBASE_AKTIF else None
except:
    db = None
def sms_gonder(musteri_ad_soyad, musteri_telefon, tarih, saat, berber):
    sistem_telefonu = "+905339740664"
    mesaj = f"YENİ RANDEVU: {musteri_ad_soyad}, {tarih} saat {saat} için {berber} ile randevu oluşturdu. Müşteri Tel: {musteri_telefon}"
    print(f"SMS GÖNDERİLİYOR -> Tel: {sistem_telefonu} | Mesaj: {mesaj}")
    return True
st.markdown("<h1>✂️ Yusuf Kırçalı</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 1.2rem; margin-bottom: 30px;'>Cadde Erkek Kuaförü Randevu Sistemi</p>", unsafe_allow_html=True)

berber_adi = "Yusuf Kırcalı"
bugun = datetime.date.today()
bir_ay_sonra = bugun + datetime.timedelta(days=30)

# Form elemanları
secilen_tarih = st.date_input("📅 Tarih Seçin", min_value=bugun, max_value=bir_ay_sonra)
secilen_tarih_str = secilen_tarih.strftime("%Y-%m-%d")

tum_saatler = [
    "08:30 - 09:30", "09:30 - 10:30", "10:30 - 11:30", "11:30 - 12:30",
    "12:30 - 13:30", "13:30 - 14:30", "14:30 - 15:30", "15:30 - 16:30",
    "16:30 - 17:30", "17:30 - 18:30", "18:30 - 19:30", "19:30 - 20:30"
]

dolu_saatler = []
if FIREBASE_AKTIF and db:
    try:
        randevular = db.collection("Randevular").where("tarih", "==", secilen_tarih_str).where("berber", "==", berber_adi).stream()
        for r in randevular:
            dolu_saatler.append(r.to_dict().get("saat"))
    except:
        pass

musait_saatler = [saat for saat in tum_saatler if saat not in dolu_saatler]

st.write("")
if len(musait_saatler) == 0:
    st.error("🚨 Bu tarih doludur. Lütfen takvimden başka bir gün seçin.")
    secilen_saat = None
else:
    secilen_saat = st.selectbox("⏰ Saat Seçin", musait_saatler)

st.write("")
ad_soyad = st.text_input("👤 Ad Soyad", placeholder="Örn: Ahmet Yılmaz")
telefon = st.text_input("📞 Telefon Numarası", placeholder="05XX XXX XX XX")

randevu_btn = st.button("Randevu Oluştur")

if randevu_btn:
    if not secilen_saat:
        st.warning("⚠️ Lütfen geçerli bir saat seçin.")
    elif not ad_soyad or not telefon:
        st.warning("⚠️ Lütfen ad, soyad ve telefon bilgilerinizi eksiksiz girin.")
    else:
        if FIREBASE_AKTIF and db:
            try:
                yeni_randevu = {
                    "berber": berber_adi,
                    "ad_soyad": ad_soyad,
                    "telefon": telefon,
                    "tarih": secilen_tarih_str,
                    "saat": secilen_saat,
                    "kayit_zamani": datetime.datetime.now()
                }
                db.collection("Randevular").add(yeni_randevu)
                sms_gonder(ad_soyad, telefon, secilen_tarih_str, secilen_saat, berber_adi)
                st.success(f"🎉 Harika! {secilen_tarih_str} tarihi, saat {secilen_saat} aralığına randevunuz başarıyla oluşturuldu.")
            except Exception as e:
                st.error(f"Kayıt sırasında bir hata oluştu: {e}")
        else:
            st.error("❌ Veritabanı bağlantısı kapalı. Şifre dosyasını kontrol edin.")
