import pandas as pd
import nltk
import string
import os
import logging

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords

# --- LIBRARY BARU ---
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory

# Agar hasil deteksi bahasa konsisten
DetectorFactory.seed = 0

# Konfigurasi Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== KONFIGURASI PATH & NLTK =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "dataset", "apple_support.csv")
NLTK_PATH = os.path.join(BASE_DIR, "nltk_data")

if not os.path.exists(NLTK_PATH):
    os.makedirs(NLTK_PATH)
nltk.data.path.append(NLTK_PATH)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    logger.info("Downloading NLTK stopwords...")
    nltk.download("stopwords", download_dir=NLTK_PATH)

# ===== LOAD DATASET =====
try:
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"File CSV tidak ditemukan di: {DATA_PATH}")

    data = pd.read_csv(DATA_PATH, engine="python", on_bad_lines="skip", header=0)
    data.columns = data.columns.str.strip().str.replace(";", "")
    
    if "Question" not in data.columns or "Answer" not in data.columns:
        raise ValueError("Dataset harus memiliki kolom 'Question' dan 'Answer'")
        
    logger.info("Dataset berhasil dimuat.")

except Exception as e:
    logger.error(f"Gagal memuat dataset: {e}")
    data = pd.DataFrame(columns=["Question", "Answer"])

# ===== PREPROCESSING =====
def preprocess(text):
    text = str(text).lower()
    text = text.translate(str.maketrans("", "", string.punctuation))
    try:
        stop_words = stopwords.words("english")
        text = " ".join([w for w in text.split() if w not in stop_words])
    except Exception:
        pass
    return text

if not data.empty:
    data["clean_question"] = data["Question"].apply(preprocess)
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(data["clean_question"])
else:
    X, vectorizer = None, None

# ===== TRANSLATION HELPER =====
def detect_language(text):
    try:
        return detect(text)
    except Exception:
        return "en" 

def translate_to_english(text):
    try:
        lang = detect_language(text)
        if lang != "en":
            return GoogleTranslator(source='auto', target='en').translate(text)
        return text
    except Exception as e:
        logger.warning(f"Error translate ke Inggris: {e}")
        return text

def translate_from_english(text, target_lang):
    try:
        if target_lang != "en":
            return GoogleTranslator(source='en', target=target_lang).translate(text)
        return text
    except Exception as e:
        logger.warning(f"Error translate output: {e}")
        return text

# ===== FUNGSI UTAMA (YANG DICARI APP.PY) =====
def chatbot_response(user_input):
    if data.empty or vectorizer is None:
        return "System Error: Dataset not loaded correctly."

    try:
        user_lang = detect_language(user_input)
        translated_input = translate_to_english(user_input)
        processed_input = preprocess(translated_input)

        user_vector = vectorizer.transform([processed_input])
        similarity_scores = cosine_similarity(user_vector, X)[0]

        max_similarity = similarity_scores.max()
        best_index = similarity_scores.argmax()

        THRESHOLD = 0.45

        if max_similarity >= THRESHOLD:
            answer_en = data["Answer"].iloc[best_index]
            return translate_from_english(answer_en, user_lang)
        else:
            msg_id = "Maaf, pertanyaan tersebut tidak tersedia dalam data saya."
            msg_en = "Sorry, that question is not available in my dataset."
            return msg_id if user_lang == 'id' else msg_en

    except Exception as e:
        logger.error(f"Error pada chatbot_response: {e}")
        return "Sorry, an error occurred while processing your request."
