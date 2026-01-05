import streamlit as st
import pandas as pd
import os
import random

st.set_page_config(page_title="Kelime Avcısı", layout="centered")

st.title("🕵️ Dosya Dedektifi")

# 1. KLASÖRDEKİ DOSYALARI LİSTELE (Ekrana yazdıracağız)
files = os.listdir()
st.info(f"📂 GitHub Klasöründeki Dosyalar: {files}")

# 2. DOSYAYI BULMAYA ÇALIŞ
file_name = "Tum_Kelimeler.xlsx" # Senin yüklediğin dosya adı

if file_name in files:
    st.success(f"✅ {file_name} bulundu! Okunuyor...")
    try:
        df = pd.read_excel(file_name)
        st.write("Veri örneği:", df.head()) # İlk 5 satırı göster
    except Exception as e:
        st.error(f"Dosya bulundu ama okunamadı. Hata: {e}")
        st.stop()
else:
    st.error(f"❌ {file_name} bulunamadı! Lütfen yukarıdaki mavi kutudaki dosya isimlerini kontrol et.")
    # Belki adı farklıdır diye CSV deniyoruz
    csv_files = [f for f in files if f.endswith(".csv")]
    if csv_files:
        st.warning(f"Ama şu CSV dosyaları var: {csv_files}. Belki bunlardan biridir?")
    st.stop()

# --- BURAYA KADAR HATASIZ GELDİYSE OYUN BAŞLAR ---

# Sütun düzeltme
if 'Kelime' in df.columns and 'Word' in df.columns:
    df = df[['Kelime', 'Word']]
    df.columns = ['en', 'tr']
    df = df.dropna()

# Oyun Mantığı
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

st.divider()
st.subheader("🎮 Kelime Oyunu")

if st.session_state.current_q == "FINISHED":
    st.balloons()
    st.success("Bitti!")
elif st.session_state.current_q:
    q = st.session_state.current_q
    st.markdown(f"## {q['word']}")
    for opt in q['options']:
        if st.button(opt):
            if opt == q['correct']:
                st.session_state.learned_words.add(q['id'])
                st.success("Doğru!")
            else:
                st.error("Yanlış!")
            st.session_state.current_q = None
            st.rerun()
