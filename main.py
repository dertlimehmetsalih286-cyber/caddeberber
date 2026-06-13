import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

# --- 1. FIREBASE BAĞLANTISI ---
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("firebase-key.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        pass

try:
    db = firestore.client()
except:
    db = None

# --- 2. SMS GÖNDERME FONKSİYONU (TASLAK) ---
def sms_gonder(ad_soyad, telefon, tarih, saat):
    # İleride buraya Twilio veya Netgsm API kodlarını entegre edeceğiz.
    # Şimdilik sadece ekrana gönderildiğine dair bilgi basıyoruz.
    mesaj = f"Sayın {ad_soyad}, {tarih} tarihi saat {saat} için rehberlik randevunuz başarıyla oluşturulmuştur."
    print(f"SMS GÖNDERİLİYOR -> Tel: {telefon} | Mesaj: {mesaj}")
    return True

# --- 3. ARAYÜZ VE SİSTEM ---
st.set_page_config(page_title="Randevu Al Sistemi", page_icon="📅")

st.title("📅 Randevu Al")
st.markdown("Rehberlik görüşmeleri için size en uygun tarih ve saati seçin.")
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Tarih ve Saat Seçimi")
    # Bugün ve sonrası için tarih seçici
    secilen_tarih = st.date_input("Randevu Tarihi", min_value=datetime.date.today())
    secilen_tarih_str = secilen_tarih.strftime("%Y-%m-%d")

    # Sabit Saat Aralıklarımız
    tum_saatler = [
        "10:00 - 11:00", 
        "11:00 - 12:00", 
        "13:00 - 14:00", 
        "14:00 - 15:00", 
        "15:00 - 16:00"
    ]

    # Firebase'den o günkü dolu saatleri kontrol etme
    dolu_saatler = []
    if db:
        randevular = db.collection("Randevular").where("tarih", "==", secilen_tarih_str).stream()
        for r in randevular:
            dolu_saatler.append(r.to_dict().get("saat"))

    # Dolu saatleri seçeneklerden çıkarma
    musait_saatler = [saat for saat in tum_saatler if saat not in dolu_saatler]

    if not musait_saatler:
        st.error("Bu tarihte boş randevu saati kalmamıştır. Lütfen başka bir gün seçin.")
        secilen_saat = None
    else:
        secilen_saat = st.selectbox("Müsait Saatler", musait_saatler)

with col2:
    st.subheader("2. İletişim Bilgileri")
    ad_soyad = st.text_input("Adınız Soyadınız")
    telefon = st.text_input("Telefon Numaranız", placeholder="05XX XXX XX XX")
    
    st.write("") # Boşluk
    randevu_btn = st.button("✅ Randevuyu Onayla ve SMS Gönder", type="primary", use_container_width=True)

# --- 4. KAYIT İŞLEMİ ---
if randevu_btn:
    if not secilen_saat:
        st.warning("Lütfen müsait bir saat seçin.")
    elif not ad_soyad or not telefon:
        st.warning("Lütfen ad, soyad ve telefon bilgilerinizi eksiksiz girin.")
    else:
        if db:
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
                
                st.success(f"Harika! {secilen_tarih_str} tarihi, saat {secilen_saat} aralığına randevunuz kaydedildi.")
                st.info("Kayıtlı telefon numaranıza bilgilendirme SMS'i gönderilmiştir.")
                
            except Exception as e:
                st.error(f"Kayıt sırasında bir hata oluştu: {e}")
        else:
            st.error("Firebase bağlantısı yok. Lütfen firebase-key.json dosyasını kontrol edin.")

