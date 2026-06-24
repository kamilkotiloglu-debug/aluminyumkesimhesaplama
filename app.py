import streamlit as st
import math
import google.generativeai as genai

# --- YAPILANDIRMA ---

API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-pro')

st.set_page_config(page_title="Alüminyum Kesim & AI Asistanı", layout="wide")

# --- FONKSİYONLAR ---
def hesapla_kesim(boy, kesim_boyu, testere, delik_sayisi, delik_metrik, et_kalinligi):
    # Bir parçanın maliyeti: Kesim Boyu + Testere Payı
    # Not: Son parçada testere payı düşmeyebilir ama güvenlik için eklenir.
    toplam_tek_parca_payi = kesim_boyu + testere
    adet = int(boy / toplam_tek_parca_payi)
    
    testere_toplam_kayip = adet * testere
    kalan_sarfiyat = boy - (adet * kesim_boyu) - testere_toplam_kayip
    
    # Delik hurdası hesabı (Hacim x Yoğunluk)
    # Alüminyum yoğunluğu ~ 2.7 g/cm3 -> 0.0027 g/mm3
    yaricap = delik_metrik / 2
    delik_alani = math.pi * (yaricap**2)
    delik_hacmi = delik_alani * et_kalinligi * delik_sayisi * adet
    delik_hurda_gram = delik_hacmi * 0.0027
    
    return adet, testere_toplam_kayip, kalan_sarfiyat, round(delik_hurda_gram, 2)

# --- ARAYÜZ ---
st.title("🛠️ Alüminyum Kesim & Optimizasyon Asistanı")

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
        delik_metrik = st.selectbox("Delik Çapı (Metrik)", [0, 3, 4, 5, 6, 8, 10, 12])
        delik_sayisi = st.number_input("Parça Başına Delik Sayısı", value=1)

    if st.button("HESAPLA"):
        adet, t_kayip, sarfiyat, d_hurda = hesapla_kesim(profil_boyu, kesim_boyu, testere_kalinligi, delik_sayisi, delik_metrik, et_kalinligi)
        
        st.success(f"Sonuç: Bu profilden **{adet}** tam parça çıkar.")
        st.warning(f"Testere nedeniyle giden toplam boy: {t_kayip} mm")
        st.error(f"Kalan fire/sarfiyat: {sarfiyat} mm")
        st.info(f"Deliklerden çıkan toplam hurda ağırlığı: {d_hurda} gram")

with tab2:
    st.header("Yapay Zeka ile Verimlilik Önerisi")
    st.write("Farklı ölçüleriniz varsa buraya yazın, AI en az fire verecek dizilimi önersin.")
    input_text = st.text_area("Örn: 6000mm profilden 3 adet 1200mm, 5 adet 800mm kesilecek. Testere 3mm. Nasıl dizmeliyim?")
    
    if st.button("AI'ya Sor"):
        with st.spinner('Yapay zeka hesaplıyor...'):
            prompt = f"Bir alüminyum kesim ustası gibi davran. Verilen ölçülere göre en az fireyi verecek kesim planını yap. Ölçüler: {input_text}"
            response = model.generate_content(prompt)
            st.markdown(response.text)

with tab3:
    st.header("Kesim Ustası Oyunu")
    st.write("Bakalım kaç parça çıkacağını tahmin edebilecek misin?")
    
    if 'game_data' not in st.session_state:
        st.session_state.game_data = {
            "g_boy": 6000,
            "g_kesim": 450,
            "g_testere": 4
        }
    
    g = st.session_state.game_data
    st.info(f"Soru: {g['g_boy']}mm profilden, {g['g_testere']}mm testere ile {g['g_kesim']}mm kaç parça çıkar?")
    
    tahmin = st.number_input("Tahminin?", value=0)
    if st.button("Kontrol Et"):
        gercek_adet = int(g['g_boy'] / (g['g_kesim'] + g['g_testere']))
        if tahmin == gercek_adet:
            st.balloons()
            st.success("Tebrikler! Tam isabet.")
        else:
            st.error(f"Maalesef yanlış. Doğru cevap {gercek_adet} olmalıydı.")
