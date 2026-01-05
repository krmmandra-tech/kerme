import streamlit as st
import pandas as pd
import random
import os

st.set_page_config(page_title="Kelime Avcısı", page_icon="🎯", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 3.5em; font-size: 18px; border-radius: 12px; }
    .word-card { background-color: #f0f2f6; padding: 40px; border-radius: 20px; text-align: center; margin-bottom: 30px; }
    .big-font { font-size: 50px !important; font-weight: 800; color: #2c3e50; }
    </style>
""", unsafe_allow_html=True)

# --- AKILLI DOSYA BULUCU ---
@st.cache_data
def load_data():
    # Klasördeki tüm dosyaları tara
    files = os.listdir()
    
    # Önce .xlsx (Excel) dosyası var mı bak
    excel_files = [f for f in files if f.endswith('.xlsx') and 'kelime' in f.lower()]
    # Sonra .csv dosyası var mı bak
    csv_files = [f for f in files if f.endswith('.csv') and 'kelime' in f.lower()]
    
    selected_file = None
    file_type = None

    if excel_files:
        selected_file = excel_files[0]
        file_type = 'excel'
    elif csv_files:
        selected_file = csv_files[0]
        file_type = 'csv'
    
    # Hiçbir şey bulamazsa GitHub'daki dosya listesini göster (Hata ayıklama için)
    if not selected_file:
        st.error("❌ HATA: Klasörde Excel veya CSV dosyası bulunamadı!")
        st.write("GitHub klasöründe görünen dosyalar şunlar:", files)
        return pd.DataFrame()

    try:
        if file_type == 'excel':
            df = pd.read_excel(selected_file)
        else:
            df = pd.read_csv(selected_file)
            
        # Sütun isimlerini düzelt
        # Senin dosyanda 'Kelime' ve 'Word' var mı kontrol et
        if 'Kelime' in df.columns and 'Word' in df.columns:
            df = df[['Kelime', 'Word']]
            df.columns = ['en', 'tr']
            return df.dropna()
        else:
            st.error(f"⚠️ '{selected_file}' dosyası bulundu ama içinde 'Kelime' ve 'Word' sütunları yok.")
            st.write("Dosyadaki sütunlar:", df.columns.tolist())
            return pd.DataFrame()

    except Exception as e:
        st.error(f"Dosya ({selected_file}) okunurken hata oluştu: {e}")
        return pd.DataFrame()

df = load_data()

# --- Oyun Mantığı ---
if 'learned_words' not in st.session_state: st.session_state.learned_words = set()
if 'current_q' not in st.session_state: st.session_state.current_q = None

def get_new_question():
    if df.empty: return
    unlearned = df[~df.index.isin(st.session_state.learned_words)]
    
    if len(unlearned) == 0:
        st.session_state.current_q = "FINISHED"
        return
    
    target = unlearned.sample(1).iloc[0]
    distractors = df[df.index != target.name].sample(min(4, len(df)-1))
    options = distractors['tr'].tolist() + [target['tr']]
    random.shuffle(options)
    
    st.session_state.current_q = {'word': target['en'], 'correct': target['tr'], 'options': options, 'id': target.name, 'answered': False}

if st.session_state.current_q is None: get_new_question()

# --- Arayüz ---
st.title("🇬🇧 Kelime Ezberle")

if not df.empty:
    done = len(st.session_state.learned_words)
    total = len(df)
    st.progress(done/total if total>0 else 0)
    st.write(f"Öğrenilen: {done} / {total}")

    if st.session_state.current_q == "FINISHED":
        st.balloons()
        st.success("Tebrikler bitti! 🎉")
        if st.button("Baştan Başla"):
            st.session_state.learned_words = set()
            get_new_question()
            st.rerun()
            
    elif st.session_state.current_q:
        q = st.session_state.current_q
        st.markdown(f"<div class='word-card'><div class='big-font'>{q['word']}</div></div>", unsafe_allow_html=True)
        
        if not q['answered']:
            for opt in q['options']:
                if st.button(opt):
                    q['answered'] = True
                    if opt == q['correct']: st.session_state.learned_words.add(q['id'])
                    st.rerun()
        else:
            if q['user_selection'] == q['correct']: st.success("Doğru! ✅")
            else: st.error(f"Yanlış! Doğrusu: {q['correct']}")
            if st.button("Devam Et ➝"):
                get_new_question()
                st.rerun()
