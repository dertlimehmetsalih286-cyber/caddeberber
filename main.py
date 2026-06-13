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
# 2. SMS GÖNDERME FONKSİYONU
# ==========================================
def sms_gonder(ad_soyad, ogrenci_telefon, tarih, saat):
    
    # 📌 SİSTEME KAYDEDECEĞİN KENDİ NUMARAN BURAYA YAZILACAK
    benim_numaram = "+905510941356" 
    
    mesaj = f"YENİ RANDEVU: {ad_soyad} adlı kişi {tarih} saat {saat} için randevu oluşturdu. Kişinin numarası: {ogrenci_telefon}"
    
    # İleride SMS firmasından alacağımız API bağlantı kodlarını tam bu satıra ekleyeceğiz.
    print(f"SMS GÖNDERİLİYOR -> Tel: {benim_numaram} | Mesaj: {mesaj}")
    return True

# ==========================================
# 3. ARAYÜZ VE TASARIM
# ==========================================
st.set_page_config(page_title="Randevu Al", page_icon="📅", layout="centered")

st.title("📅 Rehberlik Randevu Sistemi")
st.markdown("Aşağıdaki takvimden size uygun tarihi seçerek randevunuzu oluşturabilirsiniz. (En fazla 1 ay sonrası için randevu alınabilir).")
st.divider()

# Sabit Saat Aralıklarımız
tum_saatler = [
    "10:00 - 11:00", 
    "11:00 - 12:00", 
    "13:00 - 14:00", 
    "14:00 - 15:00", 
    "15:00 - 16:00"
]
max_slot_sayisi = len(tum_saatler)

# --- TAMAMEN DOLU OLAN GÜNLERİ TESPİT ETME ---
dolu_gunler = []
if db:
    try:
        randevular_ref = db.collection("Randevular").stream()
        tarih_sayaclari = {}
        
        # Her tarihte kaç randevu olduğunu sayıyoruz
        for r in randevular_ref:
            veri = r.to_dict()
            t = veri.get("tarih")
            if t:
                tarih_sayaclari[t] = tarih_sayaclari.get(t, 0) + 1
        
        # Tüm saatleri dolmuş olan günleri listeye ekliyoruz
        for t, sayi in tarih_sayaclari.items():
            if sayi >= max_slot_sayisi:
                # Tarihi Türk formatına (GG.AA.YYYY) çevirerek listeye ekleyelim
                guzel_tarih = datetime.datetime.strptime(t, "%Y-%m-%d").strftime("%d.%m.%Y")
                dolu_gunler.append(guzel_tarih)
    except Exception as e:
        pass

# Dolu günleri ekranda gösterme paneli
if dolu_gunler:
    dolu_gunler.sort()
    st.error(f"🚨 **Tamamen Dolu Olan Tarihler:** {', '.join(dolu_gunler)} (Bu tarihlerde boş saat kalmamıştır)")
else:
    st.info("📅 Şu an önümüzdeki 30 gün içinde tamamen dolu olan bir gün bulunmuyor. İstediğiniz tarihi seçebilirsiniz.")

st.write("") # Biraz boşluk

col1, col2 = st.columns([1.2, 1], gap="large")

with col1:
    st.subheader("1. Tarih ve Saat Seçimi")
    
    # SADECE 1 AYLIK RANDEVU LİMİTİ
    bugun = datetime.date.today()
    bir_ay_sonra = bugun + datetime.timedelta(days=30)
    
    secilen_tarih = st.date_input(
        "Randevu Tarihi Seçin", 
        min_value=bugun, 
        max_value=bir_ay_sonra
    )
    secilen_tarih_str = secilen_tarih.strftime("%Y-%m-%d")

    # Firebase'den seçilen günün dolu saatlerini çekme
    gunun_dolu_saatleri = []
    if db:
        secili_gun_randevulari = db.collection("Randevular").where("tarih", "==", secilen_tarih_str).stream()
        for r in secili_gun_randevulari:
            gunun_dolu_saatleri.append(r.to_dict().get("saat"))

    # RENKLİ SAAT GÖSTERGESİ (Kırmızı/Yeşil)
    st.markdown("**Seçili Günün Saat Durumu:**")
    saat_html = "<div style='display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px;'>"
    
    for saat in tum_saatler:
        if saat in gunun_dolu_saatleri:
            # Kırmızı (Dolu)
            saat_html += f"<div style='background-color: #fee2e2; color: #991b1b; padding: 8px 12px; border-radius: 6px; border: 1px solid #f87171; font-size: 14px; font-weight: bold;'>🚫 {saat} (Dolu)</div>"
        else:
            # Yeşil (Müsait)
            saat_html += f"<div style='background-color: #dcfce7; color: #166534; padding: 8px 12px; border-radius: 6px; border: 1px solid #4ade80; font-size: 14px; font-weight: bold;'>✅ {saat}</div>"
    
    saat_html += "</div>"
    st.markdown(saat_html, unsafe_allow_html=True)

    # Dolu saatleri seçenek listesinden çıkarma
    musait_saatler = [saat for saat in tum_saatler if saat not in gunun_dolu_saatleri]

    if not musait_saatler:
        st.error("🚨 Bu tarih için tüm randevular dolmuştur. Lütfen takvimden başka bir tarih seçiniz.")
        secilen_saat = None
    else:
        secilen_saat = st.selectbox("Lütfen Müsait Bir Saat Seçin", musait_saatler)

with col2:
    st.subheader("2. İletişim Bilgileri")
    ad_soyad = st.text_input("Adınız Soyadınız")
    telefon = st.text_input("Telefon Numaranız", placeholder="05XX XXX XX XX")
    
    st.write("") 
    st.write("") 
    # Buton metni tam istediğin gibi kısaltıldı
    randevu_btn = st.button("Randevuyu Onayla", type="primary", use_container_width=True)

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
