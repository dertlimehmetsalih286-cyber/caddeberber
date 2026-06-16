import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import os

# ==========================================
# 0. SAYFA AYARLARI VE KAHVERENGİ TASARIM
# ==========================================
st.set_page_config(page_title="Cadde Erkek Kuaförü", page_icon="✂️", layout="centered")

st.markdown("""
    <style>
    /* Ana Arka Plan Rengi (Kahverengi) */
    [data-testid="stAppViewContainer"] {
        background-color: #3E2723; /* Koyu lüks kahve */
        color: #F5DEB3; /* Yazı rengi: Açık krem/buğday */
    }
    [data-testid="stHeader"] {
        background-color: transparent;
    }
    
    /* Üst menüleri gizle */
    #MainMenu {visibility: hidden;} header {visibility: hidden;}
    .block-container {padding-top: 2rem;}
    
    /* Ana Başlık (Slogan) Tasarımı */
    .ana-baslik {text-align: center; color: #EFEBE9; font-size: 2.8rem; font-weight: 900; letter-spacing: 2px; margin-bottom: 40px; margin-top: 10px;}
    
    /* Berber Kartı */
    .berber-kart {border: 1px solid #5D4037; border-radius: 12px; padding: 20px; background-color: #4E342E; margin-bottom: 15px;}
    .berber-isim {font-size: 1.3rem; font-weight: 700; color: #FFFFFF; margin-bottom: 2px; text-align: center;}
    .berber-unvan {font-size: 0.9rem; color: #D7CCC8; font-weight: 600; margin-bottom: 15px; text-align: center;}
    .puan-etiket {font-size: 0.8rem; background: #3E2723; color: #FFD700; padding: 2px 8px; border-radius: 10px;}
    
    /* Buton Tasarımları (Logodaki bronz/bakır rengi) */
    .stButton > button {background-color: #8D6E63 !important; color: white !important; border-radius: 8px; border: none; padding: 10px 20px; font-weight: bold;}
    .stButton > button:hover {background-color: #6D4C41 !important;}
    
    /* Geri Dön Butonu */
    .btn-geri > button {background-color: transparent !important; color: #D7CCC8 !important; border: 1px solid #8D6E63;}
    
    /* Randevu Bilgi Kutusu */
    .form-kutusu {background-color: #4E342E; padding: 25px; border-radius: 12px; border: 1px solid #5D4037;}
    
    /* Form içindeki metinleri açık renk yap */
    p, h1, h2, h3, h4, h5, h6, label {color: #EFEBE9 !important;}
    </style>
""", unsafe_allow_html=True)


# ==========================================
# 1. ESNEK VERİTABANI BAĞLANTISI
# ==========================================
FIREBASE_AKTIF = False
HATA_DETAYI = ""

if not firebase_admin._apps:
    try:
        if os.path.exists("firebase-key.json"):
            cred = credentials.Certificate("firebase-key.json")
            firebase_admin.initialize_app(cred)
            FIREBASE_AKTIF = True
        elif os.path.exists("firebase-key"):
            cred = credentials.Certificate("firebase-key")
            firebase_admin.initialize_app(cred)
            FIREBASE_AKTIF = True
        else:
            HATA_DETAYI = "Şifre dosyası bulunamadı."
    except Exception as e:
        HATA_DETAYI = f"Okuma hatası: {e}"
else:
    FIREBASE_AKTIF = True

try:
    if FIREBASE_AKTIF:
        db = firestore.client()
except:
    db = None
    FIREBASE_AKTIF = False

# ==========================================
# 2. MESAJ GÖNDERME İŞLEMİ
# ==========================================
def sms_gonder(ad_soyad, telefon, tarih, saat, berber):
    mesaj = f"Sayın {ad_soyad}, {tarih} tarihi saat {saat} için {berber} ile randevunuz başarıyla oluşturulmuştur. Cadde Erkek Kuaförü."
    print(f"SMS GÖNDERİLİYOR -> Tel: {telefon} | Mesaj: {mesaj}")
    return True

# ==========================================
# 3. SAYFA GEÇİŞ MANTIĞI
# ==========================================
if 'sayfa' not in st.session_state:
    st.session_state.sayfa = 'ana_sayfa'
if 'secilen_berber' not in st.session_state:
    st.session_state.secilen_berber = None

def sayfaya_git(hedef_sayfa, berber_ismi=None):
    st.session_state.sayfa = hedef_sayfa
    st.session_state.secilen_berber = berber_ismi


# ==========================================
# 4. ARAYÜZ: ANA SAYFA
# ==========================================
if st.session_state.sayfa == 'ana_sayfa':
    
    if not FIREBASE_AKTIF:
        st.error(f"🔴 SİSTEM HATASI: {HATA_DETAYI}. Lütfen şifre dosyasını sisteme yükleyin.")

    # Logoyu Merkeze Ekleme
    sol_bosluk, orta_alan, sag_bosluk = st.columns([1, 1.5, 1])
    with orta_alan:
        try:
            st.image("logo.jpg", use_container_width=True)
        except:
            st.warning("⚠️ 'logo.jpg' dosyası bulunamadı. Lütfen resmi menüden yükleyin.")

    # Ana Slogan
    st.markdown("<div class='ana-baslik'>DEĞİŞİM KAFADA BAŞLAR</div>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center;'>✂️ Uzman Kadromuz</h3>", unsafe_allow_html=True)
    
    # Tek Berber Kartını Ortalamak İçin Sütun Mantığı
    bos1, orta_sutun, bos2 = st.columns([1, 2, 1])
    
    with orta_sutun:
        st.markdown("""
            <div class='berber-kart'>
                <div class='berber-isim'>👤 Yusuf Kırçali <span class='puan-etiket'>★ 4.9</span></div>
                <div class='berber-unvan'>Saç & Sakal Uzmanı</div>
            </div>
        """, unsafe_allow_html=True)
        st.button("📅 Randevu Al", key="btn_yusuf", on_click=sayfaya_git, args=('randevu_sayfasi', 'Yusuf Kırçali'), use_container_width=True)


# ==========================================
# 5. ARAYÜZ: RANDEVU ALMA SAYFASI
# ==========================================
elif st.session_state.sayfa == 'randevu_sayfasi':
    
    berber_adi = st.session_state.secilen_berber
    
    st.markdown("<div class='btn-geri'>", unsafe_allow_html=True)
    st.button("← Geri Dön", on_click=sayfaya_git, args=('ana_sayfa', None))
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown(f"<h2>👤 {berber_adi}</h2><p style='color:#BCAAA4;'>Seçili Uzman</p>", unsafe_allow_html=True)
    st.divider()
    
    col_sol, col_sag = st.columns([1, 1.5], gap="large")
    
    with col_sol:
        st.markdown("#### 📅 Tarih ve Saat Seçin")
        
        bugun = datetime.date.today()
        bir_ay_sonra = bugun + datetime.timedelta(days=30)
        
        secilen_tarih = st.date_input("Takvim", min_value=bugun, max_value=bir_ay_sonra, label_visibility="collapsed")
        secilen_tarih_str = secilen_tarih.strftime("%Y-%m-%d")

        tum_saatler = ["10:00 - 11:00", "11:00 - 12:00", "13:00 - 14:00", "14:00 - 15:00", "15:00 - 16:00", "16:00 - 17:00", "17:00 - 18:00"]
        
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
            st.error(f"🚨 {berber_adi} için bu tarih doludur.")
            secilen_saat = None
        else:
            secilen_saat = st.selectbox("Saat Seçin", musait_saatler)

    with col_sag:
        st.markdown("<div class='form-kutusu'>", unsafe_allow_html=True)
        st.markdown("#### Randevu Bilgileri")
        st.markdown("<p style='font-size:14px; color:#BCAAA4; margin-bottom:20px;'>Lütfen bilgilerinizi eksiksiz girin.</p>", unsafe_allow_html=True)
        
        ad_soyad = st.text_input("Ad Soyad", placeholder="Örn: Ahmet Yılmaz")
        telefon = st.text_input("Telefon", placeholder="05XX XXX XX XX")
        notlar = st.text_area("Not (İsteğe bağlı)", placeholder="Örn: Sadece saç tıraşı olacak...")
        
        st.write("")
        randevu_btn = st.button("Randevuyu Onayla", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if randevu_btn:
        if not FIREBASE_AKTIF:
            st.error("❌ Veritabanı bağlantısı kapalı. Şifre dosyasını kontrol edin.")
        elif not secilen_saat:
            st.warning("⚠️ Lütfen geçerli bir saat seçin.")
        elif not ad_soyad or not telefon:
            st.warning("⚠️ Lütfen ad, soyad ve telefon bilgilerinizi girin.")
        else:
            try:
                yeni_randevu = {
                    "berber": berber_adi,
                    "ad_soyad": ad_soyad,
                    "telefon": telefon,
                    "notlar": notlar,
                    "tarih": secilen_tarih_str,
                    "saat": secilen_saat,
                    "kayit_zamani": datetime.datetime.now()
                }
                db.collection("Randevular").add(yeni_randevu)
                sms_gonder(ad_soyad, telefon, secilen_tarih_str, secilen_saat, berber_adi)
                
                st.success(f"🎉 Randevunuz {berber_adi} için {secilen_tarih_str} saat {secilen_saat} aralığına başarıyla onaylandı!")
            except Exception as e:
                st.error(f"Kayıt sırasında bir hata oluştu: {e}")
