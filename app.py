import streamlit as st
import math
import google.generativeai as genai

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Alüminyum Kesim & AI", layout="wide")

# --- AI YAPILANDIRMA ---
# Streamlit Secrets'tan API anahtarını almayı dener
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-pro')
        ai_aktif = True
    else:
        ai_aktif = False
except:
    ai_aktif = False

# --- HESAPLAMA FONKSİYONU ---
def hesapla_kesim(boy, kesim_boyu, testere, delik_sayisi, delik_metrik, et_kalinligi):
    toplam_tek_parca_payi = kesim_boyu + testere
    if toplam_tek_parca_payi <= 0: return 0, 0, 0, 0
    
    adet = int(boy / toplam_tek_parca_payi)
    testere_toplam_kayip = adet * testere
    kalan_sarfiyat = boy - (adet * kesim_boyu) - testere_toplam_kayip
    
    # Alüminyum yoğunluğu ~ 0.0027 g/mm3
    yaricap = delik_metrik / 2
    delik_alani = math.pi * (yaricap**2)
    delik_hacmi = delik_alani * et_kalinligi * delik_sayisi * adet
    delik_hurda_gram = delik_hacmi * 0.0027
    
    return adet, testere_toplam_kayip, round(kalan_sarfiyat, 2), round(delik_hurda_gram, 2)

# --- ARAYÜZ ---
st.title("🛠️ Alüminyum Kesim & Optimizasyon")

tab1, tab2, tab3 = st.tabs(["📊 Hesaplama", "🤖 AI Optimizasyon", "🎮 Tahmin Oyunu"])

with tab1:
    st.header("Kesim Parametreleri")
    col1, col2 = st.columns(2)
    with col1:
        profil_boyu = st.number_input("Profil Boyu (mm)", value=6000)
        kesim_boyu = st.number_input("İstenen Kesim Boyu (mm)", value=550)
        testere_kalinligi = st.number_input("Testere Kalınlığı (mm)", value=3.0)
    with col2:
        et_kalinligi = st.number_input("Profil Et Kalınlığı (mm)", value=2.0)
        delik_metrik = st.number_input("Delik Çapı (Metrik)", value=8)
        delik_sayisi = st.number_input("Parça Başına Delik Sayısı", value=1)

    if st.button("HESAPLA"):
        adet, t_kayip, sarfiyat, d_hurda = hesapla_kesim(profil_boyu, kesim_boyu, testere_kalinligi, delik_sayisi, delik_metrik, et_kalinligi)
        st.success(f"Sonuç: Bu profilden {adet} tam parça çıkar.")
        st.write(f"📏 Testere Kaybı: {t_kayip} mm")
        st.write(f"♻️ Kalan Sarfiyat: {sarfiyat} mm")
        st.write(f"🔩 Delik Hurdası: {d_hurda} gram")

with tab2:
    st.header("AI Verimlilik Önerisi")
    if not ai_aktif:
        st.warning("AI özelliğini kullanmak için Streamlit Secrets kısmına GEMINI_API_KEY eklemelisiniz.")
    else:
        user_input = st.text_area("Örn: 6000mm profilden 3 adet 1200mm, 5 adet 800mm kesilecek. En iyi dizilim nedir?")
        if st.button("AI'ya Sor"):
            with st.spinner('AI hesaplıyor...'):
                prompt = f"Sen bir alüminyum ustasısın. En az fire verecek kesim planını yap: {user_input}"
                response = model.generate_content(prompt)
                st.markdown(response.text)

with tab3:
    st.header("Kesim Ustası Oyunu")
    st.info("Bakalım kaç parça çıkacağını tahmin edebilecek misin?")
    q_boy, q_kesim, q_testere = 6000, 450, 4
    st.write(f"Soru: {q_boy}mm profilden, {q_testere}mm testere ile {q_kesim}mm kaç parça çıkar?")
    tahmin = st.number_input("Tahminin?", value=0)
    if st.button("Kontrol Et"):
        gercek = int(q_boy / (q_kesim + q_testere))
        if tahmin == gercek:
            st.balloons()
            st.success("Tebrikler! Tam isabet.")
        else:
            st.error(f"Hata! Doğru cevap: {gercek}")
