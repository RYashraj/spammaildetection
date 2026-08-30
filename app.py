"""
Phase 4 -- UI & Documentation
Assigned to: Vishwajeet

Streamlit App for Spam Email/SMS Detection
"""

import os
import re
import pickle
import streamlit as st
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Ensure required NLTK data is downloaded
@st.cache_resource
def download_nltk_data():
    nltk.download("stopwords", quiet=True)
    nltk.download("wordnet", quiet=True)
    nltk.download("omw-1.4", quiet=True)

download_nltk_data()

# ---------------------------------------------------------------------------
# Load Models
# ---------------------------------------------------------------------------
@st.cache_resource
def load_models():
    model_path = os.path.join("models", "spam_model.pkl")
    vectorizer_path = os.path.join("models", "vectorizer.pkl")
    
    if not os.path.exists(model_path) or not os.path.exists(vectorizer_path):
        st.error("Model files not found! Please run Phase 1, 2, and 3 scripts first.")
        st.stop()
        
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    with open(vectorizer_path, "rb") as f:
        vectorizer = pickle.load(f)
        
    return model, vectorizer

model, vectorizer = load_models()

# ---------------------------------------------------------------------------
# Text Cleaning Function (must match Phase 1)
# ---------------------------------------------------------------------------
stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)          # remove URLs
    text = re.sub(r"[^a-z\s]", " ", text)               # keep only letters
    tokens = text.split()
    tokens = [t for t in tokens if t not in stop_words and len(t) > 1]
    tokens = [lemmatizer.lemmatize(t) for t in tokens]
    return " ".join(tokens)

# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Spam Email Detector", page_icon="📧", layout="centered")

st.title("📧 Spam Email & SMS Detector")
st.markdown("Paste an email or SMS message below to check if it's spam or safe (ham).")

# Input area
user_input = st.text_area("Message Content:", height=150, placeholder="Enter text here...")

if st.button("Check Message", type="primary"):
    if not user_input.strip():
        st.warning("Please enter some text to analyze.")
    else:
        with st.spinner("Analyzing..."):
            # 1. Clean the input text
            cleaned_input = clean_text(user_input)
            
            if not cleaned_input.strip():
                st.error("The message contains no usable text after cleaning (e.g., only numbers/punctuation).")
            else:
                # 2. Vectorize
                vectorized_input = vectorizer.transform([cleaned_input])
                
                # 3. Predict
                prediction = model.predict(vectorized_input)[0]
                probabilities = model.predict_proba(vectorized_input)[0]
                
                spam_prob = probabilities[1] * 100
                ham_prob = probabilities[0] * 100
                
                st.markdown("---")
                # 4. Display Results
                if prediction == 1:
                    st.error(f"🚨 **SPAM DETECTED** (Confidence: {spam_prob:.1f}%)")
                else:
                    st.success(f"✅ **SAFE (HAM)** (Confidence: {ham_prob:.1f}%)")
                    
                # Optional: expander for details
                with st.expander("Show internal details"):
                    st.write("**Original Text:**", user_input)
                    st.write("**Cleaned Text:**", cleaned_input)
                    st.write("**Spam Probability:**", f"{spam_prob:.2f}%")
                    st.write("**Ham Probability:**", f"{ham_prob:.2f}%")
