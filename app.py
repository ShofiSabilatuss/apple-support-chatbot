import os
from flask import Flask, render_template, request, session
from model import chatbot_response

app = Flask(__name__)

# Gunakan secret key yang aman. Di production, sebaiknya pakai environment variable.
app.secret_key = "uas_machine_learning_chatbot" 

@app.route("/", methods=["GET", "POST"])
def index():
    # 1. Inisialisasi Chat History
    if "chat_history" not in session:
        session["chat_history"] = []

    # 2. Logika Reset Chat
    if request.args.get("reset") == "true":
        session["chat_history"] = []
        session.modified = True # Memaksa Flask memperbarui cookie session

    # 3. Logika Proses Pertanyaan (POST)
    if request.method == "POST":
        user_question = request.form.get("question")

        # Cek agar input tidak kosong atau hanya spasi
        if user_question and user_question.strip():
            
            # Panggil model chatbot dengan Error Handling
            try:
                bot_response = chatbot_response(user_question)
            except Exception as e:
                bot_response = "Maaf, terjadi kesalahan internal pada model."
                print(f"Error getting response: {e}")

            # Update Session
            # Ambil list, tambahkan data, lalu simpan kembali
            # Ini cara paling aman agar session di Flask terdeteksi perubahannya
            history = session["chat_history"]
            
            history.append({
                "user": user_question,
                "bot": bot_response
            })

            # PENTING: Batasi jumlah chat yang disimpan di session
            # Cookie Flask memiliki batas ukuran (4KB). Jika chat terlalu panjang, error akan muncul.
            # Kita batasi misal hanya menyimpan 10 percakapan terakhir.
            if len(history) > 10:
                history.pop(0) 

            session["chat_history"] = history
            session.modified = True

    return render_template(
        "index.html",
        chat_history=session["chat_history"]
    )

if __name__ == "__main__":
    # Konfigurasi untuk Deployment (Render/Heroku/Docker)
    # Cloud biasanya menyediakan PORT via environment variable
    # Host 0.0.0.0 wajib digunakan agar aplikasi bisa diakses dari luar container
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)