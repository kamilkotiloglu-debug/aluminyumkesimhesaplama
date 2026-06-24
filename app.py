import streamlit as st
import math
import google.generativeai as genai

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Alüminyum Kesim & Talaş Hesabı", layout="wide")

# --- AI YAPILANDIRMA ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        # Daha hızlı ve güncel model olan flash modelini kullanıyoruz
        model = genai.GenerativeModel('gemini-1.5-flash')
        ai_aktif = True
    else:
        ai_aktif = False
except:
    ai_aktif = False

# --- HESAPLAMA FONKSİYONU ---
def hesapla_kesim(boy, kesim_boyu, testere, metre_agirlik, delik_sayisi, delik_metrik, et_kalinligi):
    toplam_tek_parca_payi = kesim_boyu + testere
    if toplam_tek_parca_payi <= 0: return 0, 0, 0, 0, 0
    
    # Kaç adet çıkacağı
    adet = int(boy / toplam_tek_parca_payi)
    
    # Kesim sırasında testerenin yok ettiği (talaş olan) miktar
    # Formül: 1 kg/m profil için 1mm testere = 1 gram talaş
    bir_kesim_talas_gram = metre_agirlik * testere
    toplam_kesim_talas_gram = bir_kesim_talas_gram * adet
    
    # Fire/Sarfiyat (boy olarak)
    testere_toplam_boy_kaybi = adet * testere
    kalan_sarfiyat_boy = boy - (adet * kesim_boyu) - testere_toplam_boy_kaybi
    
    # Delik hurdası hesabı (Hacim x Yoğunluk)
    # Alüminyum yoğunluğu ~ 0.0027 g/mm3
    yaricap = delik_metrik / 2
    delik_alani = math.pi * (yaricap**2)
    delik_hacmi = delik_alani * et_kalinligi * delik_sayisi * adet
    delik_hurda_gram = delik_hacmi * 0.0027
    
    return adet, round(toplam_kesim_talas_gram, 2), round(kalan_sarfiyat_boy, 2), round(delik_hurda_gram, 2), testere_toplam_boy_kaybi

# --- ARAYÜZ ---
st.title("🛠️ Alüminyum Kesim & Talaş Hesaplayıcı")

if ai_aktif:
    st.sidebar.success("✅ AI Bağlantısı Aktif")
else:
    st.sidebar.warning("⚠️ AI Devre Dışı (Secret Key Eksik)")

tab1, tab2, tab3 = st.tabs(["📊 Teknik Hesaplama", "🤖 AI Optimizasyon", "🎮 Tahmin Oyunu"])

with tab1:
    st.header("Profil ve Kesim Bilgileri")
    col1, col2 = st.columns(2)
    
    with col1:
        profil_boyu = st.number_input("Profil Toplam Boyu (mm)", value=6000)
        kesim_boyu = st.number_input("Kesilecek Parça Boyu (mm)", value=550)
        testere_kalinligi = st.number_input("Testere Kalınlığı (mm)", value=3.0)
        metre_agirlik = st.number_input("Profil Metre Ağırlığı (kg/m)", value=1.50, help="Örn: 1.50 kg/m")
    
    with col2:
        st.subheader("Delik İşlemi (Varsa)")
        delik_metrik = st.number_input("Delik Çapı (Metrik mm)", value=8)
        et_kalinligi = st.number_input("Delinecek Yerin Et Kalınlığı (mm)", value=2.0)
        delik_sayisi = st.number_input("Parça Başına Delik Sayısı", value=1)

    if st.button("HESAPLAMAYI BAŞLAT"):
        adet, t_gram, sarfiyat_boy, d_hurda, t_boy = hesapla_kesim(
            profil_boyu, kesim_boyu, testere_kalinligi, metre_agirlik, delik_sayisi, delik_metrik, et_kalinligi
        )
        
        st.divider()
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Çıkan Parça", f"{adet} Adet")
        with c2:
            st.metric("Kesim Talaşı", f"{t_gram} Gram")
        with c3:
            st.metric("Delik Hurdası", f"{d_hurda} Gram")
            
        st.info(f"💡 **Detaylı Bilgi:** Kesim işlemi sonucunda toplam **{t_boy} mm** malzeme testere tarafından talaşa dönüştürüldü. Elinizde kalan net profil parçası (fire) **{sarfiyat_boy} mm**'dir.")

with tab2:
    st.header("AI Verimlilik Danışmanı")
    if not ai_aktif:
        st.error("AI özelliğini kullanmak için Streamlit Secrets kısmına GEMINI_API_KEY eklemelisiniz.")
    else:
        user_input = st.text_area("Kesim listesini yazın:", placeholder="Örn: 6000mm profilden 4 adet 1100mm, 2 adet 800mm kesilecek. En verimli nasıl dizerim?")
        if st.button("AI Analiz Et"):
            with st.spinner('Analiz ediliyor...'):
                prompt = f"Sen bir alüminyum kesim uzmanısın. Şu isteği analiz et ve en az fireyi verecek kesim sırasını/planını yaz: {user_input}"
                response = model.generate_content(prompt)
                st.markdown(response.text)

with tab3:
    st.header("Usta Tahmin Oyunu")
    st.write("Bakalım malzemenin hakkını verebilecek misin?")
    # Sabit oyun değerleri
    o_boy, o_kesim, o_testere = 6000, 480, 3
    st.warning(f"Soru: {o_boy}mm boyundaki profilden {o_testere}mm testere ile {o_kesim}mm kaç parça çıkar?")
    tahmin = st.number_input("Tahmin Adedi:", value=0)
    if st.button("Tahmini Kontrol Et"):
        gercek = int(o_boy / (o_kesim + o_testere))
        if tahmin == gercek:
            st.balloons()
            st.success(f"Tebrikler Usta! Tam isabet: {gercek} parça.")
        else:
            st.error(f"Maalesef... Doğru cevap {gercek} olmalıydı.")
