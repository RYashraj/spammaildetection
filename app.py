"""
Phase 5 -- Upgraded Email-Focused UI
Assigned to: Vishwajeet

New Features:
  - Multi-modal input: Paste Text / Upload .eml File / Upload Image (OCR)
  - .eml auto-parsing: extracts Sender, Subject, Body automatically
  - Image OCR: reads text out of spam poster images
  - Separate Subject + Sender + Body analysis
  - Premium email-style UI
"""

import os
import re
import pickle
import email
import email.policy
import html
from html.parser import HTMLParser
import streamlit as st
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# ---------------------------------------------------------------------------
# Page config (must be first Streamlit call)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Spam Email Detector",
    page_icon="📧",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Custom CSS — premium email-style UI
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main { background: #0f1117; }

    .header-card {
        background: linear-gradient(135deg, #1a1f2e 0%, #16213e 100%);
        border: 1px solid #2d3561;
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
    }
    .header-card h1 { font-size: 2rem; font-weight: 700; color: #ffffff; margin: 0; }
    .header-card p  { color: #8b9dc3; margin: 6px 0 0 0; font-size: 0.95rem; }

    .result-spam {
        background: linear-gradient(135deg, #2d0a0a 0%, #3d1515 100%);
        border: 1px solid #ef4444;
        border-radius: 12px;
        padding: 20px 24px;
        margin-top: 20px;
    }
    .result-ham {
        background: linear-gradient(135deg, #0a2d0a 0%, #153d15 100%);
        border: 1px solid #22c55e;
        border-radius: 12px;
        padding: 20px 24px;
        margin-top: 20px;
    }
    .result-title { font-size: 1.4rem; font-weight: 700; margin: 0 0 6px 0; }
    .result-conf  { font-size: 0.9rem; color: #9ca3af; }

    .field-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 4px;
    }
    .detail-box {
        background: #1a1f2e;
        border: 1px solid #2d3561;
        border-radius: 10px;
        padding: 16px;
        margin-top: 16px;
    }
    .detail-row { display: flex; gap: 10px; margin-bottom: 8px; }
    .detail-key { color: #6b7280; font-size: 0.85rem; min-width: 110px; }
    .detail-val { color: #e2e8f0; font-size: 0.85rem; word-break: break-all; }

    .badge-spam { background:#7f1d1d; color:#fca5a5; padding:2px 10px; border-radius:999px; font-size:0.75rem; font-weight:600; }
    .badge-ham  { background:#14532d; color:#86efac; padding:2px 10px; border-radius:999px; font-size:0.75rem; font-weight:600; }

    div[data-testid="stTabs"] button { font-weight: 600; }
    div[data-testid="stFileUploader"] { border: 1px dashed #2d3561; border-radius: 10px; padding: 8px; }
    .stTextArea textarea { background: #1a1f2e !important; border: 1px solid #2d3561 !important; color: #e2e8f0 !important; }
    .stTextInput input  { background: #1a1f2e !important; border: 1px solid #2d3561 !important; color: #e2e8f0 !important; }

    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# NLTK setup
# ---------------------------------------------------------------------------
@st.cache_resource
def init_nltk():
    nltk.download("stopwords", quiet=True)
    nltk.download("wordnet",   quiet=True)
    nltk.download("omw-1.4",   quiet=True)

init_nltk()

# ---------------------------------------------------------------------------
# Load models
# ---------------------------------------------------------------------------
@st.cache_resource
def load_models():
    model_path      = os.path.join("models", "spam_model.pkl")
    vectorizer_path = os.path.join("models", "vectorizer.pkl")
    if not os.path.exists(model_path) or not os.path.exists(vectorizer_path):
        st.error("Model files missing! Run Phase 1 → 2 → 3 scripts first.")
        st.stop()
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    with open(vectorizer_path, "rb") as f:
        vec = pickle.load(f)
    return model, vec

model, vectorizer = load_models()

# ---------------------------------------------------------------------------
# Text cleaning (identical to Phase 1)
# ---------------------------------------------------------------------------
_stop_words  = set(stopwords.words("english"))
_lemmatizer  = WordNetLemmatizer()

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    tokens = [_lemmatizer.lemmatize(t)
              for t in text.split()
              if t not in _stop_words and len(t) > 1]
    return " ".join(tokens)

# ---------------------------------------------------------------------------
# HTML → plain text stripper
# ---------------------------------------------------------------------------
class _HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self._parts = []
    def handle_data(self, data):
        self._parts.append(data)
    def get_text(self):
        return " ".join(self._parts)

def strip_html(raw_html: str) -> str:
    s = _HTMLStripper()
    s.feed(html.unescape(raw_html))
    return s.get_text()

# ---------------------------------------------------------------------------
# .eml parser — returns (sender, subject, body)
# ---------------------------------------------------------------------------
def parse_eml(file_bytes: bytes):
    msg = email.message_from_bytes(file_bytes, policy=email.policy.default)
    sender  = msg.get("From",    "Unknown Sender")
    subject = msg.get("Subject", "No Subject")
    body    = ""

    if msg.is_multipart():
        for part in msg.walk():
            ctype    = part.get_content_type()
            cdispos  = str(part.get("Content-Disposition", ""))
            if "attachment" in cdispos:
                continue                      # skip attachments — never execute them
            if ctype == "text/plain":
                body += part.get_payload(decode=True).decode(errors="replace") + " "
            elif ctype == "text/html" and not body:
                raw = part.get_payload(decode=True).decode(errors="replace")
                body += strip_html(raw) + " "
    else:
        ctype = msg.get_content_type()
        raw   = msg.get_payload(decode=True).decode(errors="replace")
        body  = strip_html(raw) if ctype == "text/html" else raw

    return sender.strip(), subject.strip(), body.strip()

# ---------------------------------------------------------------------------
# OCR helper (optional — graceful fallback if Tesseract not installed)
# ---------------------------------------------------------------------------
def ocr_image(uploaded_file) -> str:
    try:
        import pytesseract
        from PIL import Image
        img  = Image.open(uploaded_file)
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception:
        return ""

# ---------------------------------------------------------------------------
# Prediction helper
# ---------------------------------------------------------------------------
def predict(combined_text: str):
    cleaned = clean_text(combined_text)
    if not cleaned.strip():
        return None, None, None
    vec_input   = vectorizer.transform([cleaned])
    label       = model.predict(vec_input)[0]
    probs       = model.predict_proba(vec_input)[0]
    return label, probs[1] * 100, cleaned   # (label, spam_pct, cleaned_text)

# ---------------------------------------------------------------------------
# UI — Header
# ---------------------------------------------------------------------------
st.markdown("""
<div class="header-card">
  <h1>📧 Spam Email Detector</h1>
  <p>AI-powered spam detection. Paste text, upload a .eml file, or scan an image — all processed locally, no data is ever sent anywhere.</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Tabs — three input modes
# ---------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["✏️  Paste / Type", "📁  Upload .eml File", "🖼️  Upload Image (OCR)"])

sender_val  = ""
subject_val = ""
body_val    = ""
ocr_status  = ""

# ── Tab 1: Paste Text ──────────────────────────────────────────────────────
with tab1:
    st.markdown('<p class="field-label">Sender Email (optional)</p>', unsafe_allow_html=True)
    sender_val  = st.text_input("Sender",  label_visibility="collapsed",
                                placeholder="e.g. noreply@apple-verify-secure.com", key="t1_sender")

    st.markdown('<p class="field-label">Subject Line (optional)</p>', unsafe_allow_html=True)
    subject_val = st.text_input("Subject", label_visibility="collapsed",
                                placeholder="e.g. URGENT: Your account has been suspended", key="t1_subject")

    st.markdown('<p class="field-label">Email / SMS Body</p>', unsafe_allow_html=True)
    body_val    = st.text_area("Body",     label_visibility="collapsed",
                               placeholder="Paste the full email or SMS message body here...",
                               height=180, key="t1_body")

# ── Tab 2: Upload .eml ─────────────────────────────────────────────────────
with tab2:
    st.markdown("""
    **How to download a .eml file:**
    - **Gmail:** Open email → `⋮ More` → `Download message` → saves `.eml`
    - **Outlook:** Open email → `File` → `Save As` → choose `.msg` or `.eml`

    > ✅ **Safe:** Attachments inside the file are never opened or executed.
    """)
    eml_file = st.file_uploader("Upload .eml file", type=["eml", "msg"], label_visibility="collapsed")

    if eml_file is not None:
        file_bytes = eml_file.read()
        sender_val, subject_val, body_val = parse_eml(file_bytes)
        st.success("Email parsed successfully! Fields auto-filled below:")
        st.markdown(f"**From:** `{sender_val}`")
        st.markdown(f"**Subject:** `{subject_val}`")
        with st.expander("Preview extracted body text"):
            st.write(body_val[:1000] + ("..." if len(body_val) > 1000 else ""))

# ── Tab 3: Image OCR ───────────────────────────────────────────────────────
with tab3:
    st.markdown("""
    **For spam emails that contain only an image (poster/banner):**
    Take a screenshot of the spam image, then upload it here.
    The app will read the text out of the image using OCR and analyze it.
    """)
    img_file = st.file_uploader("Upload image (.png, .jpg, .jpeg)", type=["png", "jpg", "jpeg"],
                                label_visibility="collapsed", key="ocr_upload")

    if img_file is not None:
        extracted = ocr_image(img_file)
        if extracted:
            body_val   = extracted
            ocr_status = "success"
            st.success("Text extracted from image successfully!")
            with st.expander("Preview extracted text"):
                st.write(extracted[:1000] + ("..." if len(extracted) > 1000 else ""))
        else:
            ocr_status = "fail"
            st.warning(
                "Could not extract text. Make sure **Tesseract** is installed:\n\n"
                "Download from: https://github.com/UB-Mannheim/tesseract/wiki\n\n"
                "Then add it to your System PATH and restart the app."
            )

# ---------------------------------------------------------------------------
# Analyse Button — works across all tabs
# ---------------------------------------------------------------------------
st.markdown("---")
col1, col2 = st.columns([3, 1])
with col2:
    analyse = st.button("🔍 Analyse Email", type="primary", use_container_width=True)

if analyse:
    # Combine all available fields: subject is weighted more by repeating it
    combined = f"{subject_val} {subject_val} {sender_val} {body_val}".strip()

    if not combined.strip():
        st.warning("Please provide at least a message body to analyse.")
    else:
        with st.spinner("Analysing..."):
            label, spam_pct, cleaned = predict(combined)

        if label is None:
            st.error("No meaningful text found after cleaning (only numbers/punctuation).")
        else:
            ham_pct = 100 - spam_pct

            # ── Result Card ───────────────────────────────────────────────
            if label == 1:
                st.markdown(f"""
                <div class="result-spam">
                  <p class="result-title">🚨 SPAM DETECTED</p>
                  <p class="result-conf">Spam confidence: <b>{spam_pct:.1f}%</b> &nbsp;|&nbsp; Ham confidence: {ham_pct:.1f}%</p>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="result-ham">
                  <p class="result-title">✅ SAFE — Ham</p>
                  <p class="result-conf">Ham confidence: <b>{ham_pct:.1f}%</b> &nbsp;|&nbsp; Spam confidence: {spam_pct:.1f}%</p>
                </div>""", unsafe_allow_html=True)

            # ── Confidence Bar ────────────────────────────────────────────
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"**Spam probability:** {spam_pct:.1f}%")
            st.progress(int(spam_pct))

            # ── Details Expander ──────────────────────────────────────────
            with st.expander("Show analysis details"):
                if sender_val:
                    st.markdown(f"**Sender:** `{sender_val}`")
                if subject_val:
                    st.markdown(f"**Subject:** `{subject_val}`")
                st.markdown(f"**Cleaned text fed to model:**")
                st.code(cleaned[:500] + ("..." if len(cleaned) > 500 else ""), language=None)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;color:#374151;font-size:0.8rem;'>"
    "Spam Email Detector · PBL Project · All processing is 100% local"
    "</p>",
    unsafe_allow_html=True
)
