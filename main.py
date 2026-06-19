import streamlit as st
from twilio.rest import Client
import datetime

# --- SMS AYARLARI (TWILIO) ---
# Ücretsiz bir Twilio hesabı açarak bu bilgileri alabilirsin.
TWILIO_ACCOUNT_SID = 'buraya_hesap_sid_gelecek'
TWILIO_AUTH_TOKEN = 'buraya_auth_token_gelecek'
TWILIO_PHONE_NUMBER = '+1234567890' # Twilio'nun sana verdiği telefon numarası
HEDEF_TELEFON = '+905555555555'     # SMS'in gideceği kendi telefon numaran

def sms_gonder(ad, soyad, tarih, saat):
    """Twilio API kullanarak SMS gönderen fonksiyon"""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        mesaj_metni = f"Bilgilendirme: {ad} {soyad} isimli kişi {tarih} tarihi ve saat {saat} için randevu oluşturdu."
        
        message = client.messages.create(
            body=mesaj_metni,
            from_=TWILIO_PHONE_NUMBER,
            to=HEDEF_TELEFON
        )
        return True
    except Exception as e:
        st.error(f"SMS gönderilirken bir hata oluştu: {e}")
        return False

# --- KULLANICI ARAYÜZÜ (STREAMLIT) ---
st.title("📅 Randevu Alma Sistemi")
st.write("Lütfen randevu bilgilerinizi aşağıya giriniz.")

# Form yapısı kullanarak sayfanın gereksiz yenilenmesini önlüyoruz
with st.form("randevu_formu"):
    st.subheader("Kişisel Bilgiler")
    col1, col2 = st.columns(2)
    with col1:
        ad = st.text_input("Ad:")
    with col2:
        soyad = st.text_input("Soyad:")
        
    st.subheader("Zaman Seçimi")
    col3, col4 = st.columns(2)
    with col3:
        # Geçmiş bir tarihe randevu alınmasını engellemek için min_value bugüne ayarlandı
        tarih = st.date_input("Randevu Tarihi:", min_value=datetime.date.today())
    with col4:
        saat = st.time_input("Randevu Saati:")

    # Formu onaylama butonu
    submit_buton = st.form_submit_button("Randevu Al")

# Butona tıklandığında çalışacak işlemler
if submit_buton:
    if ad.strip() == "" or soyad.strip() == "":
        st.warning("⚠️ Lütfen ad ve soyad alanlarını eksiksiz doldurun.")
    else:
        with st.spinner("Randevunuz işleniyor ve SMS gönderiliyor..."):
            basarili_mi = sms_gonder(ad, soyad, tarih, saat)
            
            if basarili_mi:
                st.success(f"✅ Sayın {ad} {soyad}, {tarih} - {saat} için randevunuz başarıyla oluşturuldu!")
                st.info("Sistem yöneticisine SMS ile bilgilendirme yapıldı.")
