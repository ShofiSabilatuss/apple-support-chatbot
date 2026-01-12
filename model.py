import streamlit as st

# 1. Konfigurasi Halaman (Judul Tab & Ikon)
st.set_page_config(page_title="UAS Chatbot ML", page_icon="🤖")

# Judul di dalam aplikasi
st.title("🤖 Chatbot Machine Learning")
st.write("Silakan tanya seputar dukungan perangkat Apple.")

# 2. Inisialisasi Session State (Pengganti session Flask)
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# 3. Sidebar: Tombol Reset (Pengganti logika reset di Flask)
with st.sidebar:
    st.header("Pengaturan")
    if st.button("Hapus Riwayat Chat"):
        st.session_state["chat_history"] = []
        st.rerun() # Refresh halaman

# 4. Tampilkan Chat History yang tersimpan
# Streamlit menggambar ulang layar dari atas ke bawah setiap ada interaksi
for chat in st.session_state["chat_history"]:
    with st.chat_message("user"):
        st.markdown(chat["user"])
    with st.chat_message("assistant"):
        st.markdown(chat["bot"])

# 5. Input User & Logika Proses (Pengganti method POST)
if user_input := st.chat_input("Ketik pertanyaan Anda di sini..."):
    
    # Tampilkan pesan user langsung di UI agar responsif
    with st.chat_message("user"):
        st.markdown(user_input)

    # Proses jawaban bot
    with st.chat_message("assistant"):
        with st.spinner("Sedang memproses..."):
            try:
                bot_response = chatbot_response(user_input)
            except Exception as e:
                bot_response = "Maaf, terjadi kesalahan internal pada model."
                print(f"Error: {e}")
            
            st.markdown(bot_response)

    # 6. Simpan ke Session State (Logika History)
    st.session_state["chat_history"].append({
        "user": user_input,
        "bot": bot_response
    })

    # Batasi history maksimal 10 percakapan (Sama seperti logika Flask Anda)
    if len(st.session_state["chat_history"]) > 10:
        st.session_state["chat_history"].pop(0)

