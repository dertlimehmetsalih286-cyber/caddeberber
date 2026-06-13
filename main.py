import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

# ==========================================
# 1. FIREBASE BAĞLANTISI
# ==========================================
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

# ==========================================
# 2. SMS GÖNDERME FONKSİYONU (TASLAK)
# ==========================================
def sms_gonder(ad_soyad, telefon, tarih, saat):
    # İleride buraya Netgsm veya Twilio kodları gelecek
    mesaj = f"Sayın {ad_soyad}, {tarih} tarihi saat {saat} için rehberlik randevunuz başarıyla oluşturulmuştur."
    print(f"SMS GÖNDERİLİYOR -> Tel: {telefon} | Mesaj: {mesaj}")
    return True

# ==========================================
# 3. ARAYÜZ VE TASARIM
# ==========================================
st.set_page_config(page_title="Randevu Al", page_icon="📅", layout="centered")

st.title("📅 Rehberlik Randevu Sistemi")
st.markdown("Aşağıdaki takvimden size uygun tarihi seçerek randevunuzu oluşturabilirsiniz. (En fazla 1 ay sonrası için randevu alınabilir).")
st.divider()

col1, col2 = st.columns([1.2, 1], gap="large")

with col1:
    st.subheader("1. Tarih ve Saat Seçimi")
    
    # SADECE 1 AYLIK RANDEVU LİMİTİ
    bugun = datetime.date.today()
    bir_ay_sonra = bugun + datetime.timedelta(days=30)
    
    secilen_tarih = st.date_input(
        "Randevu Tarihi Seçin", 
        min_value=bugun, 
        max_value=bir_ay_sonra # Bu komut 1 aydan sonrasını kilitler
    )
    secilen_tarih_str = secilen_tarih.strftime("%Y-%m-%d")

    # Sabit Saat Aralıklarımız
    tum_saatler = [
        "10:00 - 11:00", 
        "11:00 - 12:00", 
        "13:00 - 14:00", 
        "14:00 - 15:00", 
        "15:00 - 16:00"
    ]

    # Firebase'den o günkü dolu saatleri çekme
    dolu_saatler = []
    if db:
        randevular = db.collection("Randevular").where("tarih", "==", secilen_tarih_str).stream()
        for r in randevular:
            dolu_saatler.append(r.to_dict().get("saat"))

    # RENKLİ SAAT GÖSTERGESİ (Kırmızı/Yeşil)
    st.markdown("**Günlük Saat Durumu:**")
    saat_html = "<div style='display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px;'>"
    
    for saat in tum_saatler:
        if saat in dolu_saatler:
            # Kırmızı (Dolu)
            saat_html += f"<div style='background-color: #fee2e2; color: #991b1b; padding: 8px 12px; border-radius: 6px; border: 1px solid #f87171; font-size: 14px; font-weight: bold;'>🚫 {saat} (Dolu)</div>"
        else:
            # Yeşil (Müsait)
            saat_html += f"<div style='background-color: #dcfce7; color: #166534; padding: 8px 12px; border-radius: 6px; border: 1px solid #4ade80; font-size: 14px; font-weight: bold;'>✅ {saat}</div>"
    
    saat_html += "</div>"
    st.markdown(saat_html, unsafe_allow_html=True)

    # Dolu saatleri listeden çıkarma
    musait_saatler = [saat for saat in tum_saatler if saat not in dolu_saatler]

    if not musait_saatler:
        # EĞER GÜN TAMAMEN DOLUYSA
        st.error("🚨 BU GÜN İÇİN TÜM RANDEVULAR DOLMUŞTUR. Lütfen takvimden başka bir tarih seçiniz.")
        secilen_saat = None
    else:
        secilen_saat = st.selectbox("Lütfen Müsait Bir Saat Seçin", musait_saatler)

with col2:
    st.subheader("2. İletişim Bilgileri")
    ad_soyad = st.text_input("Adınız Soyadınız")
    telefon = st.text_input("Telefon Numaranız", placeholder="05XX XXX XX XX")
    
    st.write("") 
    st.write("") 
    randevu_btn = st.button("✅ Randevuyu Onayla", type="primary", use_container_width=True)

# ==========================================
# 4. KAYIT İŞLEMİ VE KONTROLLER
# ==========================================
if randevu_btn:
    if not secilen_saat:
        st.warning("⚠️ Lütfen geçerli ve müsait bir saat seçin.")
    elif not ad_soyad or not telefon:
        st.warning("⚠️ Lütfen ad, soyad ve telefon bilgilerinizi eksiksiz girin.")
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
                
                st.success(f"🎉 Harika! {secilen_tarih_str} tarihi, saat {secilen_saat} aralığına randevunuz başarıyla kaydedildi.")
                st.info("📱 Kayıtlı telefon numaranıza bilgilendirme SMS'i gönderilmiştir.")
                
            except Exception as e:
                st.error(f"Kayıt sırasında bir hata oluştu: {e}")
        else:
            st.error("Firebase bağlantısı yok. Lütfen ayarlarınızı kontrol edin.")
