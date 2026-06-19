import streamlit as st
from twilio.rest import Client
import datetime
import os

# --- SMS AYARLARI (GİZLİ BİLGİLER - RENDER ÜZERİNDEN ÇEKİLECEK) ---
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
HEDEF_TELEFON = os.environ.get('HEDEF_TELEFON')

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
        tarih = st.date_input("Randevu Tarihi:", min_value=datetime.date.today())
    with col4:
        saat = st.time_input("Randevu Saati:")

    submit_buton = st.form_submit_button("Randevu Al")

if submit_buton:
    if ad.strip() == "" or soyad.strip() == "":
        st.warning("⚠️ Lütfen ad ve soyad alanlarını eksiksiz doldurun.")
    else:
        with st.spinner("Randevunuz işleniyor ve SMS gönderiliyor..."):
            basarili_mi = sms_gonder(ad, soyad, tarih, saat)
            
            if basarili_mi:
                st.success(f"✅ Sayın {ad} {soyad}, {tarih} - {saat} için randevunuz başarıyla oluşturuldu!")
                st.info("Sistem yöneticisine SMS ile bilgilendirme yapıldı.")
