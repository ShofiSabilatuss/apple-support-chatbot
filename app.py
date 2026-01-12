import streamlit as st
from model import chatbot_response

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Apple Support Bot", page_icon="🍎")

st.title("🍎 Apple Support Chatbot")
st.write("Silakan tanya seputar dukungan perangkat Apple (Bisa Bahasa Indonesia/Inggris).")

# 2. Inisialisasi Session State (Agar history chat tidak hilang saat reload)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Sidebar: Tombol Reset
with st.sidebar:
    st.header("Pengaturan")
    if st.button("Hapus Riwayat Chat"):
        st.session_state.messages = []
        st.rerun()

# 4. Tampilkan Chat History yang sudah ada
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Input User & Proses Jawaban
if prompt := st.chat_input("Apa keluhan Anda?"):
    
    # Tampilkan pesan user
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Simpan pesan user ke history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Proses jawaban bot
    with st.chat_message("assistant"):
        with st.spinner("Sedang mencari jawaban..."):
            try:
                response = chatbot_response(prompt)
            except Exception as e:
                response = "Maaf, terjadi kesalahan pada sistem."
            st.markdown(response)
    
    # Simpan jawaban bot ke history
    st.session_state.messages.append({"role": "assistant", "content": response})
