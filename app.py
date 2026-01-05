import streamlit as st
import pandas as pd
import random

# --- Sayfa Ayarları ---
st.set_page_config(page_title="Kelime Avcısı", page_icon="🎓", layout="centered")

# --- CSS İle Biraz Güzelleştirelim ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        font-size: 16px;
    }
    .big-font {
        font-size: 40px !important;
        font-weight: bold;
        color: #4a90e2;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- Veri Yükleme ve Önbellekleme ---
@st.cache_data
def load_data():
    # Dosya adını buraya yazıyoruz. Excel ise pd.read_excel kullanabilirsin.
    # Senin dosyanın formatına göre CSV okuyoruz.
    try:
        df = pd.read_csv("kelimeler.csv")
        # Sütun isimlerini senin dosyana göre eşleyelim: Kelime(En), Word(Tr)
        # CSV'deki başlıkların tam olarak 'Kelime' ve 'Word' olduğunu varsayıyorum.
        # Değilse burayı dosyana göre düzeltmelisin.
        df = df[['Kelime', 'Word']]
        df.columns = ['en', 'tr']
        return df
    except Exception as e:
        st.error(f"Dosya okunamadı! Lütfen dosya adının 'kelimeler.csv' olduğundan emin olun. Hata: {e}")
        return pd.DataFrame()

df = load_data()

# --- Oturum Durumu (Session State) ---
if 'learned_words' not in st.session_state:
    st.session_state.learned_words = set()

if 'current_q' not in st.session_state:
    st.session_state.current_q = None

if 'score' not in st.session_state:
    st.session_state.score = 0

# --- Yeni Soru Getirme Fonksiyonu ---
def get_new_question():
    # Öğrenilmemiş kelimeleri filtrele
    unlearned = df[~df.index.isin(st.session_state.learned_words)]
    
    if len(unlearned) < 5:
        st.success("Tebrikler! Tüm kelimeleri bitirdin! 🎉")
        st.session_state.current_q = "FINISHED"
        return

    # Rastgele bir kelime seç (Doğru Cevap)
    target = unlearned.sample(1).iloc[0]
    target_idx = target.name
    
    # 4 tane rastgele yanlış cevap seç
    distractors = df[df.index != target_idx].sample(4)
    
    # Şıkları birleştir ve karıştır
    options = distractors['tr'].tolist() + [target['tr']]
    random.shuffle(options)
    
    st.session_state.current_q = {
        'word': target['en'],
        'correct': target['tr'],
        'options': options,
        'id': target_idx,
        'answered': False
    }

# İlk açılışta soru getir
if st.session_state.current_q is None:
    get_new_question()

# --- Arayüz Tasarımı ---
st.title("🇬🇧 ➔ 🇹🇷 Kelime Çalışması")

# İstatistikler
col1, col2, col3 = st.columns(3)
col1.metric("Toplam Kelime", len(df))
col2.metric("Öğrenilen", len(st.session_state.learned_words))
col3.metric("Kalan", len(df) - len(st.session_state.learned_words))

st.divider()

if st.session_state.current_q == "FINISHED":
    st.balloons()
    if st.button("Sıfırla ve Baştan Başla"):
        st.session_state.learned_words = set()
        st.session_state.score = 0
        get_new_question()
        st.rerun()

elif st.session_state.current_q:
    q = st.session_state.current_q
    
    # Sorulan Kelime
    st.markdown(f"<div class='big-font'>{q['word']}</div>", unsafe_allow_html=True)
    st.write("") # Boşluk

    # Şıklar için form
    with st.form("quiz_form"):
        # Radyo butonu yerine butonlar kullanmak için biraz trick yapıyoruz
        # Ancak form içinde radyo daha temiz çalışır.
        selection = st.radio("Doğru anlamı seç:", q['options'], label_visibility="collapsed")
        
        submitted = st.form_submit_button("Cevabı Kontrol Et", type="primary")

        if submitted:
            if selection == q['correct']:
                st.success(f"✅ Doğru! **{q['word']}** = **{q['correct']}**")
                
                # Öğrenildi işaretle (Kullanıcı isterse checkbox da koyabiliriz ama otomatik öğrenildi sayalım)
                st.session_state.learned_words.add(q['id'])
            else:
                st.error(f"❌ Yanlış. Doğrusu: **{q['correct']}** olacaktı.")
            
            st.session_state.current_q['answered'] = True

    # Sonraki Soru Butonu
    if st.session_state.current_q.get('answered'):
        if st.button("Sonraki Kelime ➝"):
            get_new_question()
            st.rerun()

# --- Yan Menü ---
with st.sidebar:
    st.write("### Hakkında")
    st.write("Bu uygulama Excel dosyasındaki kelimelerle pratik yapmanı sağlar.")
    progress = len(st.session_state.learned_words) / len(df) if len(df) > 0 else 0
    st.progress(progress)
    st.write(f"İlerleme: %{int(progress*100)}")