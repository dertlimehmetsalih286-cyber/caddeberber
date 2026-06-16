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
        background-color: #3E2723;
        color: #F5DEB3;
    }
    [data-testid="stHeader"] {
        background-color: transparent;
    }
    
    /* Üst menüleri gizle */
    #MainMenu {visibility: hidden;} header {visibility: hidden;}
    .block-container {padding-top: 2rem;}
    
    /* Ana Başlık (Slogan) Tasarımı */
    .ana-baslik {text-align: center; color: #EFEBE9; font-size: 2.8rem; font-weight: 900; letter-spacing: 2px; margin-bottom: 30px; margin-top: 10px;}
    
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
# 2. MESAJ GÖNDERME İŞLEMİ (SABİT NUMARA İLE)
# ==========================================
def sms_gonder(musteri_ad_soyad, musteri_telefon, tarih, saat, berber):
    sistem_telefonu = "+905339740664"
    mesaj = f"YENİ RANDEVU: {musteri_ad_soyad}, {tarih} saat {saat} için {berber} ile randevu oluşturdu. Müşteri Tel: {musteri_telefon}"
    print(f"SMS GÖNDERİLİYOR -> Tel: {sistem_telefonu} | Mesaj: {mesaj}")
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

    sol_bosluk, orta_alan, sag_bosluk = st.columns([1, 1.5, 1])
    with orta_alan:
        try:
            st.image("logo.jpg", use_container_width=True)
        except:
            pass 

    st.markdown("<div class='ana-baslik'>DEĞİŞİM KAFADA BAŞLAR</div>", unsafe_allow_html=True)
    
    bos1, orta_sutun, bos2 = st.columns([1, 2, 1])
    with orta_sutun:
        st.markdown("""
            <div class='berber-kart'>
                <div class='berber-isim'>👤 Yusuf Kırçalı <span class='puan-etiket'>★ 4.9</span></div>
                <div class='berber-unvan'>Saç & Sakal Uzmanı</div>
            </div>
        """, unsafe_allow_html=True)
        st.button("📅 Randevu Al", key="btn_yusuf", on_click=sayfaya_git, args=('randevu_sayfasi', 'Yusuf Kırçalı'), use_container_width=True)


# ==========================================
# 5. ARAYÜZ: RANDEVU ALMA SAYFASI
# ==========================================
elif st.session_state.sayfa == 'randevu_sayfasi':
    
    berber_adi = st.session_state.secilen_berber
    
    st.markdown("<div class='btn-geri'>", unsafe_allow_html=True)
    st.button("← Geri Dön", on_click=sayfaya_git, args=('ana_sayfa', None))
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown(f"<h2>👤 {berber_adi}</h2><p style='color:#BCAAA4; font-size: 16px; margin-top: -15px;'>Berberi</p>", unsafe_allow_html=True)
    st.divider()
    
    # --- AKILLI TARİH SEÇİM MANTIĞI (OTOMATİK SONRAKİ GÜNE ATMA) ---
    bugun = datetime.date.today()
    bir_ay_sonra = bugun + datetime.timedelta(days=30)
    tum_saatler = ["10:00 - 11:00", "11:00 - 12:00", "13:00 - 14:00", "14:00 - 15:00", "15:00 - 16:00", "16:00 - 17:00", "17:00 - 18:00"]
    
    varsayilan_tarih = bugun
    
    if FIREBASE_AKTIF and db:
        try:
            # Önümüzdeki 30 günün randevularını çekip hangi günlerin dolu olduğunu hesaplayalım
            randevular_ref = db.collection("Randevular").where("tarih", ">=", bugun.strftime("%Y-%m-%d")).where("berber", "==", berber_adi).stream()
            tarih_sayaclari = {}
            for r in randevular_ref:
                t_str = r.to_dict().get("tarih")
                if t_str:
                    tarih_sayaclari[t_str] = tarih_sayaclari.get(t_str, 0) + 1
            
            # Bugünden başlayarak ilk boş günü bulup varsayılan tarih yapıyoruz
            for i in range(31):
                kontrol_tarih = bugun + datetime.timedelta(days=i)
                kontrol_tarih_str = kontrol_tarih.strftime("%Y-%m-%d")
                if tarih_sayaclari.get(kontrol_tarih_str, 0) < len(tum_saatler):
                    varsayilan_tarih = kontrol_tarih
                    break
        except:
            pass

    # İki Sütunlu Yapı
    col_sol, col_sag = st.columns([1, 1.5], gap="large")
    
    with col_sol:
        st.markdown("#### 📅 Tarih Seçin")
        
        # Takvim varsayılan olarak en yakın boş günde açılır
        secilen_tarih = st.date_input("Takvim", min_value=bugun, max_value=bir_ay_sonra, value=varsayilan_tarih, label_visibility="collapsed")
        secilen_tarih_str = secilen_tarih.strftime("%Y-%m-%d")

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
            st.error(f"🚨 {berber_adi} için bu tarih tamamen doludur. Lütfen başka bir gün seçin.")
            secilen_saat = None
        else:
            secilen_saat = st.selectbox("Saat Seçin", musait_saatler)

    with col_sag:
        st.markdown("<div class='form-kutusu'>", unsafe_allow_html=True)
        st.markdown("#### Randevu Bilgileri")
        st.markdown("<p style='font-size:14px; color:#BCAAA4; margin-bottom:20px;'>Lütfen takvimden bir tarih ve saat seçin.</p>", unsafe_allow_html=True)
        
        ad_soyad = st.text_input("Ad Soyad", placeholder="Örn: Ahmet Yılmaz")
        telefon = st.text_input("Telefon", placeholder="05XX XXX XX XX")
        notlar = st.text_area("Not (isteğe bağlı)", placeholder="Randevu ile ilgili eklemek istedikleriniz...")
        
        st.write("")
        randevu_btn = st.button("Randevu Oluştur", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if randevu_btn:
        if not FIREBASE_AKTIF:
            st.error("❌ Veritabanı bağlantısı kapalı. Şifre dosyasını kontrol edin.")
        elif not secilen_saat:
            st.warning("⚠️ Seçtiğiniz tarih doludur, kayıt yapılamaz. Lütfen müsait bir tarih seçin.")
        elif not ad_soyad or not telephone:
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
                st.success(f"🎉 Randevunuz {berber_adi} için {secilen_tarih_str} saat {secilen_saat} aralığına başarıyla oluşturuldu!")
            except Exception as e:
                st.error(f"Kayıt sırasında bir hata oluştu: {e}")
