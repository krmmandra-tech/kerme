import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Kelime Avcısı", page_icon="🎯", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 3.5em; font-size: 18px; border-radius: 12px; }
    .word-card { background-color: #f0f2f6; padding: 40px; border-radius: 20px; text-align: center; margin-bottom: 30px; }
    .big-font { font-size: 50px !important; font-weight: 800; color: #2c3e50; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        # BURASI KRİTİK: Senin dosya adını yazdım
        df = pd.read_excel("Tum_Kelimeler.xlsx")
        
        # Sütun isimlerini düzeltiyoruz
        if 'Kelime' in df.columns and 'Word' in df.columns:
            df = df[['Kelime', 'Word']]
            df.columns = ['en', 'tr']
            return df.dropna()
        else:
            st.error("Excel dosyasında 'Kelime' ve 'Word' sütunları bulunamadı.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Dosya okunamadı! Hata detayı: {e}")
        st.info("İPUCU: GitHub'daki dosya adının tam olarak 'Tum_Kelimeler.xlsx' olduğundan emin ol.")
        return pd.DataFrame()

df = load_data()

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

st.title("🇬🇧 Kelime Ezberle")

if not df.empty:
    done = len(st.session_state.learned_words)
    total = len(df)
    st.progress(done/total if total>0 else 0)
    st.write(f"Öğrenilen: {done} / {total}")

    if st.session_state.current_q == "FINISHED":
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
