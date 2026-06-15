import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import os

# ==========================================
# 0. SAYFA AYARLARI VE ÖZEL TASARIM (CSS)
# ==========================================
st.set_page_config(page_title="Randevu Sistemi", page_icon="📅", layout="centered")

# Fotoğraflardaki tasarımı Streamlit'e uyarlamak için özel CSS
st.markdown("""
    <style>
    /* Üst menü ve gereksiz Streamlit boşluklarını gizle */
    #MainMenu {visibility: hidden;} header {visibility: hidden;}
    .block-container {padding-top: 2rem;}
    
    /* Ana Başlık Tasarımı */
    .hero-title {text-align: center; color: #2E3E4F; font-size: 3.5rem; font-weight: 800; line-height: 1.1; margin-bottom: 10px;}
    .hero-title span {color: #386A7A;}
    .hero-subtitle {text-align: center; color: #6C7A89; font-size: 1.1rem; font-weight: 400; margin-bottom: 40px;}
    
    /* Berber Kartları */
    .berber-card {border: 1px solid #EAECEF; border-radius: 12px; padding: 20px; background-color: white; margin-bottom: 15px;}
    .berber-name {font-size: 1.2rem; font-weight: 700; color: #2E3E4F; margin-bottom: 2px;}
    .berber-title {font-size: 0.9rem; color: #386A7A; font-weight: 600; margin-bottom: 15px;}
    
    /* Buton Tasarımları (Koyu Turkuaz) */
    .stButton > button {background-color: #386A7A !important; color: white !important; border-radius: 8px; border: none; padding: 10px 20px; font-weight: 600;}
    .stButton > button:hover {background-color: #2D5663 !important;}
    
    /* Geri Dön Butonu */
    .btn-back > button {background-color: transparent !important; color: #6C7A89 !important; border: 1px solid #EAECEF; font-weight: normal;}
    </style>
""", unsafe_allow_html=True)


# ==========================================
# 1. ESNEK FIREBASE BAĞLANTISI
# ==========================================
FIREBASE_AKTIF = False
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
    except:
        pass

try:
    if FIREBASE_AKTIF:
        db = firestore.client()
except:
    db = None
    FIREBASE_AKTIF = False

# ==========================================
# 2. SMS GÖNDERME FONKSİYONU
# ==========================================
def sms_gonder(ad_soyad, telefon, tarih, saat, berber):
    mesaj = f"Sayın {ad_soyad}, {tarih} tarihi saat {saat} için {berber} ile berber randevunuz başarıyla oluşturulmuştur."
    print(f"SMS GÖNDERİLİYOR -> Tel: {telefon} | Mesaj: {mesaj}")
    return True

# ==========================================
# 3. SAYFA YÖNLENDİRME (ROUTING) MANTIĞI
# ==========================================
# Uygulama ilk açıldığında hangi sayfada olacağımızı ve seçilen berberi hafızada tutuyoruz
if 'sayfa' not in st.session_state:
    st.session_state.sayfa = 'ana_sayfa'
if 'secilen_berber' not in st.session_state:
    st.session_state.secilen_berber = None

def sayfaya_git(hedef_sayfa, berber_ismi=None):
    st.session_state.sayfa = hedef_sayfa
    st.session_state.secilen_berber = berber_ismi


# ==========================================
# 4. ARAYÜZ: ANA SAYFA (Fotoğraf 1)
# ==========================================
if st.session_state.sayfa == 'ana_sayfa':
    
    # Hero Section
    st.markdown("<p style='text-align:center;'><span style='background-color:#EBF1F4; color:#386A7A; padding:4px 12px; border-radius:20px; font-size:12px; font-weight:600;'>Profesyonel Berberi</span></p>", unsafe_allow_html=True)
    st.markdown("<div class='hero-title'>Tarzınız için<br><span>doğru berber</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-subtitle'>Deneyimli berberlerimizle size özel bir stil deneyimi yaşayın. Hemen randevunu alın.</div>", unsafe_allow_html=True)
    
    st.markdown("### Berberlerimiz")
    
    # Berber Kartları (İki Sütun)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='berber-card'><div class='berber-name'>👤 Yusuf Kılıç <span style='float:right; font-size:0.8rem; background:#EBF1F4; padding:2px 8px; border-radius:10px;'>★ 4.9</span></div><div class='berber-title'>Berberi</div></div>", unsafe_allow_html=True)
        # Butona basıldığında sayfayı değiştir ve Yusuf'u seç
        st.button("📅 Randevu Al", key="btn_yusuf", on_click=sayfaya_git, args=('randevu_sayfasi', 'Yusuf Kılıç'), use_container_width=True)

    with col2:
        st.markdown("<div class='berber-card'><div class='berber-name'>👤 Kamil Kılıç <span style='float:right; font-size:0.8rem; background:#EBF1F4; padding:2px 8px; border-radius:10px;'>★ 4.9</span></div><div class='berber-title'>Berberi</div></div>", unsafe_allow_html=True)
        # Butona basıldığında sayfayı değiştir ve Kamil'i seç
        st.button("📅 Randevu Al", key="btn_kamil", on_click=sayfaya_git, args=('randevu_sayfasi', 'Kamil Kılıç'), use_container_width=True)


# ==========================================
# 5. ARAYÜZ: RANDEVU SAYFASI (Fotoğraf 2)
# ==========================================
elif st.session_state.sayfa == 'randevu_sayfasi':
    
    berber_adi = st.session_state.secilen_berber
    
    # Geri Dön Butonu
    st.markdown("<div class='btn-back'>", unsafe_allow_html=True)
    st.button("← Geri Dön", on_click=sayfaya_git, args=('ana_sayfa', None))
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Seçili Berber Başlığı
    st.markdown(f"<h2>👤 {berber_adi}</h2><p style='color:#6C7A89;'>Berberi</p>", unsafe_allow_html=True)
    st.divider()
    
    col_sol, col_sag = st.columns([1, 1.5], gap="large")
    
    with col_sol:
        st.markdown("#### 📅 Tarih ve Saat Seçin")
        
        bugun = datetime.date.today()
        bir_ay_sonra = bugun + datetime.timedelta(days=30)
        
        secilen_tarih = st.date_input("Takvim", min_value=bugun, max_value=bir_ay_sonra, label_visibility="collapsed")
        secilen_tarih_str = secilen_tarih.strftime("%Y-%m-%d")

        # Çalışma Saat Aralıkları
        tum_saatler = ["10:00 - 11:00", "11:00 - 12:00", "13:00 - 14:00", "14:00 - 15:00", "15:00 - 16:00"]
        
        # SADECE SEÇİLEN BERBERİN o günkü dolu saatlerini çekiyoruz
        dolu_saatler = []
        if FIREBASE_AKTIF and db:
            try:
                # Sorguya berber_adi filtresi de eklendi!
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
        st.markdown("<div style='background-color:#F8F9FA; padding:25px; border-radius:12px; border:1px solid #EAECEF;'>", unsafe_allow_html=True)
        st.markdown("#### Randevu Bilgileri")
        st.markdown("<p style='font-size:14px; color:#6C7A89; margin-bottom:20px;'>Lütfen bilgilerinizi eksiksiz girin.</p>", unsafe_allow_html=True)
        
        ad_soyad = st.text_input("Ad Soyad", placeholder="Örn: Ahmet Yılmaz")
        telefon = st.text_input("Telefon", placeholder="05XX XXX XX XX")
        notlar = st.text_area("Not (İsteğe bağlı)", placeholder="Randevu ile ilgili eklemek istedikleriniz...")
        
        st.write("")
        randevu_btn = st.button("Randevu Oluştur", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # --- KAYIT İŞLEMİ ---
    if randevu_btn:
        if not FIREBASE_AKTIF:
            st.error("❌ Veritabanı bağlantısı kapalıyken kayıt yapılamaz.")
        elif not secilen_saat:
            st.warning("⚠️ Lütfen geçerli bir saat seçin.")
        elif not ad_soyad or not telefon:
            st.warning("⚠️ Lütfen ad, soyad ve telefon bilgilerinizi girin.")
        else:
            try:
                # Veritabanına Kaydet (Berber Adı ve Notlar eklendi)
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
                
                st.success(f"🎉 Randevunuz {berber_adi} için {secilen_tarih_str} saat {secilen_saat} aralığına oluşturuldu!")
            except Exception as e:
                st.error(f"Kayıt sırasında bir hata oluştu: {e}")
