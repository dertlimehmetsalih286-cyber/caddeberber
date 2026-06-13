import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import os

# ==========================================
# 1. ESNEK FIREBASE BAĞLANTISI (Hata Önleyici)
# ==========================================
FIREBASE_AKTIF = False
if not firebase_admin._apps:
    try:
        # Hem uzantılı hem uzantısız dosyayı kontrol eder
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
    else:
        db = None
except:
    db = None
    FIREBASE_AKTIF = False

# ==========================================
# 2. SMS GÖNDERME FONKSİYONU
# ==========================================
def sms_gonder(ad_soyad, telefon, tarih, saat):
    mesaj = f"Sayın {ad_soyad}, {tarih} tarihi saat {saat} için rehberlik randevunuz başarıyla oluşturulmuştur."
    print(f"SMS GÖNDERİLİYOR -> Tel: {telefon} | Mesaj: {mesaj}")
    return True

# ==========================================
# 3. İLK VE SADE ARAYÜZE DÖNÜŞ
# ==========================================
st.set_page_config(page_title="Randevu Al", page_icon="📅")

st.title("📅 Randevu Al")
st.markdown("Rehberlik görüşmeleri için size en uygun tarih ve saati seçin. *(En fazla 1 ay sonrası için randevu alınabilir)*.")
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Tarih ve Saat Seçimi")
    
    # Sadece 1 aylık randevu limiti
    bugun = datetime.date.today()
    bir_ay_sonra = bugun + datetime.timedelta(days=30)
    
    secilen_tarih = st.date_input("Randevu Tarihi", min_value=bugun, max_value=bir_ay_sonra)
    secilen_tarih_str = secilen_tarih.strftime("%Y-%m-%d")

    tum_saatler = [
        "10:00 - 11:00", 
        "11:00 - 12:00", 
        "13:00 - 14:00", 
        "14:00 - 15:00", 
        "15:00 - 16:00"
    ]

    # Firebase'den o günkü dolu saatleri kontrol etme
    dolu_saatler = []
    if FIREBASE_AKTIF and db:
        try:
            randevular = db.collection("Randevular").where("tarih", "==", secilen_tarih_str).stream()
            for r in randevular:
                dolu_saatler.append(r.to_dict().get("saat"))
        except:
            pass

    musait_saatler = [saat for saat in tum_saatler if saat not in dolu_saatler]

    # EĞER GÜN TAMAMEN DOLUYSA KIRMIZI UYARI VER
    if len(musait_saatler) == 0:
        st.error("🚨 Bu tarih tamamen doludur (Kırmızı Gün). Lütfen takvimden başka bir gün seçin.")
        secilen_saat = None
    else:
        # Eski temiz seçici kutu (Selectbox) geri geldi
        secilen_saat = st.selectbox("Müsait Saatler", musait_saatler)

with col2:
    st.subheader("2. İletişim Bilgileri")
    ad_soyad = st.text_input("Adınız Soyadınız")
    telefon = st.text_input("Telefon Numaranız", placeholder="05XX XXX XX XX")
    
    st.write("") 
    st.write("") 
    randevu_btn = st.button("Randevuyu Onayla", type="primary", use_container_width=True)

# ==========================================
# 4. KAYIT İŞLEMİ
# ==========================================
if randevu_btn:
    if not FIREBASE_AKTIF:
        st.error("❌ Veritabanı bağlantısı kurulamadı. Lütfen şifre dosyanızı kontrol edin.")
    elif not secilen_saat:
        st.warning("⚠️ Lütfen geçerli ve müsait bir saat seçin.")
    elif not ad_soyad or not telefon:
        st.warning("⚠️ Lütfen ad, soyad ve telefon bilgilerinizi eksiksiz girin.")
    else:
        try:
            # Veritabanına Kaydet
            yeni_randevu = {
                "ad_soyad": ad_soyad,
                "telefon": telefon,
                "tarih": secilen_tarih_str,
                "saat": secilen_saat,
                "kayit_zamani": datetime.datetime.now()
            }
            db.collection("Randevular").add(yeni_randevu)
            
            # Başarılı olursa SMS fonksiyonunu tetikle
            sms_gonder(ad_soyad, telefon, secilen_tarih_str, secilen_saat)
            
            st.success(f"🎉 Harika! {secilen_tarih_str} tarihi, saat {secilen_saat} aralığına randevunuz başarıyla kaydedildi.")
        except Exception as e:
            st.error(f"Kayıt sırasında bir hata oluştu: {e}")
