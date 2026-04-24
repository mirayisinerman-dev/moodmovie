import streamlit as st
import requests
import os
import random
from dotenv import load_dotenv
from textblob import TextBlob

st.set_page_config(page_title="MoodMovie AI", page_icon="🎬", layout="wide")

def local_css():
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: #e0e0e0;
        }
        .stTextInput > div > div > input {
            background-color: rgba(255, 255, 255, 0.05);
            color: white;
            border: 1px solid #4f4f4f;
            border-radius: 10px;
        }
        .stButton > button {
            background: linear-gradient(45deg, #4b0082, #000046);
            color: #ffd700; 
            border: 1px solid #ffd700;
            border-radius: 50px;
            padding: 12px 35px;
            font-style: italic;
            box-shadow: 0 4px 15px rgba(75, 0, 130, 0.4);
            width: 100%;
        }

        .stButton > button:hover {
            background: linear-gradient(45deg, #6a0dad, #1e1e78);
            box-shadow: 0 0 25px rgba(255, 215, 0, 0.3);
            color: #ffffff;
            border: 1px solid #ffffff;
        }
        [data-testid="stVerticalBlock"] > div:has(div.stImage) {
            background-color: rgba(25, 28, 35, 0.7); /* Koyu kart rengi */
            padding: 15px;
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: border 0.3s ease, box-shadow 0.3s ease, background-color 0.3s ease;
        }

        [data-testid="stVerticalBlock"] > div:has(div.stImage):hover {
            border: 1px solid #ffd700; /* Butonla uyumlu altın sarısı */
            background-color: rgba(255, 255, 255, 0.08);
            box-shadow: 0 0 20px rgba(255, 215, 0, 0.2);
        }
        </style>
    """, unsafe_allow_html=True)

local_css()

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

GENRE_MAP = {
    "drama": 18, "romance": 10749, "comedy": 35, 
    "action": 28, "sci-fi": 878, "horror": 27, 
    "animation": 16, "thriller": 53
}

def detect_mood_ai(text):
    text_lower = text.lower()

    if any(word in text_lower for word in ["üzgün", "mutsuz", "ağlamak", "drama", "duygusal"]):
        return "drama"
    if any(word in text_lower for word in ["aşk", "sevgi", "romantik", "sevgili", "evlilik"]):
        return "romance"
    if any(word in text_lower for word in ["komik", "eğlence", "gülmek", "neşeli", "kahkaha"]):
        return "comedy"
    if any(word in text_lower for word in ["animasyon", "çizgi film", "çocuk", "renkli", "masal"]):
        return "animation"
    if any(word in text_lower for word in ["korku", "korkunç", "ürpertici", "zombi", "paranormal"]):
        return "horror"
    if any(word in text_lower for word in ["gerilim", "gizem", "suç", "polis", "dedektif"]):
        return "thriller"
    if any(word in text_lower for word in ["aksiyon", "macera", "heyecan", "vurdu kırdı", "savaş"]):
        return "action"
    if any(word in text_lower for word in ["uzay", "gelecek", "robot", "teknoloji", "bilim kurgu", "sci-fi","bilimsel"]):
        return "sci-fi"
    
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity 
    
    if polarity > 0.2:
        return "comedy animation"
    elif polarity < -0.2:
        return "thriller horror"
    else:
        return "action sci-fi"

def get_movies_from_api(genre_names):
    url = "https://api.themoviedb.org/3/discover/movie"
    genre_ids = [str(GENRE_MAP[g]) for g in genre_names.split() if g in GENRE_MAP]
    random_page = random.randint(1, 5) 

    params = {
        "api_key": TMDB_API_KEY,
        "with_genres": ",".join(genre_ids),
        "sort_by": "popularity.desc",
        "language": "tr-TR",
        "page": random_page,
        "vote_count.gte": 150 
    }

    try:
        response = requests.get(url, params=params)
        all_movies = response.json().get("results", [])
        if len(all_movies) >= 16:
            return random.sample(all_movies, 16)
        return all_movies
    except Exception as e:
        st.error(f"⚠️ Hata: {e}")
        return []


st.title("🎬 Bugün nasılsın?")
st.markdown("---")

user_input = st.text_input(
    "Şu anki ruh halini anlat, sana en uygun filmi seçeyim...",
    placeholder="Örn: Bugün çok enerjik hissediyorum, biraz aksiyon iyi gider!"
)

if st.button("Film Öner"):
    if not user_input:
        st.warning("Bir duygu yazmadın, bu şekilde tahmin edemem")
    else:
        with st.spinner('Senin için uygun filmler seçiliyor...'):
            suggested_genres = detect_mood_ai(user_input)
            movies = get_movies_from_api(suggested_genres)

            if movies:
                st.info(f"Duygu Analizi Sonucu: Senin için **{suggested_genres.upper()}** türünde filmler seçildi.")
                cols = st.columns(4)
                for i, m in enumerate(movies):
                    with cols[i % 4]:
                        poster_path = m.get('poster_path')
                        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/500x750?text=Afiş+Yok"
                        
                        st.image(poster_url, use_container_width=True)
                        st.markdown(f"### {m['title']}")
                        st.write(f"⭐ Puan: {m['vote_average']}")
                        
                        with st.expander("Film Özetini Oku"):
                            st.caption(m['overview'] if m['overview'] else "Bu film için özet mevcut değil.")
            else:
                st.error("Maalesef bu kriterlere uygun bir film listesi oluşturulamadı.")

st.markdown("---")
st.caption("Veriler TMDB API kullanılarak çekilmiştir. AI Analizi TextBlob kütüphanesi ile yapılmaktadır.")