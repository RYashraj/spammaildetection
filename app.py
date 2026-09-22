"""
Phase 5 -- Upgraded Email-Focused UI
Assigned to: Vishwajeet

New Features:
  - Two input modes: Paste Text / Upload .eml File
  - .eml auto-parsing: extracts Sender, Subject, Body automatically
  - Separate Subject + Sender + Body analysis
  - Clear button resets all inputs and result
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
import pandas as pd
import altair as alt
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
local_nltk_path = os.path.join(os.path.dirname(__file__), "nltk_data")
if os.path.exists(local_nltk_path) and local_nltk_path not in nltk.data.path:
    nltk.data.path.insert(0, local_nltk_path)

@st.cache_resource
def init_nltk():
    try:
        nltk.download("stopwords", quiet=True)
        nltk.download("wordnet",   quiet=True)
        nltk.download("omw-1.4",   quiet=True)
    except Exception:
        pass

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
# Visual Explainability & Feature Contribution Helpers (PBL / Academic Feature)
# ---------------------------------------------------------------------------
def get_feature_contributions(cleaned_text: str, top_n: int = 10) -> pd.DataFrame:
    """
    Extract vocabulary tokens from the input text and compute their mathematical
    contribution to the Naive Bayes classification:
      Impact = TF-IDF(w) * [log P(w|Spam) - log P(w|Ham)]
    """
    if not cleaned_text.strip():
        return pd.DataFrame()

    vec_input = vectorizer.transform([cleaned_text])
    feature_indices = vec_input.nonzero()[1]

    if len(feature_indices) == 0:
        return pd.DataFrame()

    feature_names = vectorizer.get_feature_names_out()
    data = []

    for idx in feature_indices:
        word = str(feature_names[idx])
        tfidf = float(vec_input[0, idx])
        # Naive Bayes log-likelihood ratio: log P(w | Spam) - log P(w | Ham)
        log_ratio = float(model.feature_log_prob_[1, idx] - model.feature_log_prob_[0, idx])
        impact = tfidf * log_ratio
        direction = "Spam Indicator" if impact > 0 else "Ham Indicator"

        data.append({
            "Word": word,
            "Impact Score": round(impact, 4),
            "Magnitude": abs(impact),
            "Direction": direction,
            "TF-IDF": round(tfidf, 4),
            "Log-Ratio": round(log_ratio, 4),
        })

    df = pd.DataFrame(data)
    # Sort by absolute impact magnitude to find the most influential words
    df = df.sort_values(by="Magnitude", ascending=False).head(top_n)
    # Re-sort by Impact Score for clear vertical display in Altair
    df = df.sort_values(by="Impact Score", ascending=True)
    return df


def build_confidence_chart(spam_pct: float, ham_pct: float):
    """
    Native Streamlit / Altair horizontal probability distribution chart.
    """
    df_conf = pd.DataFrame([
        {"Class": "Ham (Safe)", "Probability": round(ham_pct, 1)},
        {"Class": "Spam",       "Probability": round(spam_pct, 1)}
    ])

    chart = (
        alt.Chart(df_conf)
        .mark_bar(cornerRadiusEnd=6, height=28)
        .encode(
            x=alt.X("Probability:Q", scale=alt.Scale(domain=[0, 100]), title="Prediction Probability (%)"),
            y=alt.Y("Class:N", sort=["Ham (Safe)", "Spam"], title=""),
            color=alt.Color(
                "Class:N",
                scale=alt.Scale(
                    domain=["Ham (Safe)", "Spam"],
                    range=["#22c55e", "#ef4444"]
                ),
                legend=None
            ),
            tooltip=[
                alt.Tooltip("Class:N", title="Category"),
                alt.Tooltip("Probability:Q", title="Probability (%)", format=".1f")
            ]
        )
        .properties(height=110)
    )

    text = (
        alt.Chart(df_conf)
        .mark_text(
            align="left",
            baseline="middle",
            dx=6,
            color="#e2e8f0",
            fontWeight="bold",
            fontSize=12
        )
        .encode(
            x=alt.X("Probability:Q"),
            y=alt.Y("Class:N", sort=["Ham (Safe)", "Spam"]),
            text=alt.Text("Probability:Q", format=".1f")
        )
    )
    return chart + text


def build_word_impact_chart(df_words: pd.DataFrame):
    """
    Horizontal bar chart showing terms that influenced Spam vs. Ham predictions.
    """
    if df_words.empty:
        return None

    chart = (
        alt.Chart(df_words)
        .mark_bar(cornerRadius=4, height=20)
        .encode(
            y=alt.Y(
                "Word:N",
                sort=alt.EncodingSortField(field="Impact Score", order="descending"),
                title="Terms / N-grams"
            ),
            x=alt.X("Impact Score:Q", title="Weighted Log-Odds Contribution (Impact Score)"),
            color=alt.Color(
                "Direction:N",
                scale=alt.Scale(
                    domain=["Ham Indicator", "Spam Indicator"],
                    range=["#22c55e", "#ef4444"]
                ),
                title="Influence Direction"
            ),
            tooltip=[
                alt.Tooltip("Word:N", title="Term"),
                alt.Tooltip("Direction:N", title="Indicator"),
                alt.Tooltip("Impact Score:Q", title="Impact Score", format=".3f"),
                alt.Tooltip("TF-IDF:Q", title="TF-IDF Weight", format=".3f"),
                alt.Tooltip("Log-Ratio:Q", title="Log-Odds Ratio Δ", format=".3f")
            ]
        )
        .properties(height=max(180, len(df_words) * 28))
    )

    rule = alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(color="#6b7280", strokeDash=[3, 3]).encode(x="x:Q")
    return chart + rule

# ---------------------------------------------------------------------------
# UI — Header
# ---------------------------------------------------------------------------
st.markdown("""
<div class="header-card">
  <h1>📧 Spam Email Detector</h1>
  <p>AI-powered spam detection. Paste text or upload a .eml file — all processed locally, no data is ever sent anywhere.</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Tabs — two input modes
# ---------------------------------------------------------------------------
tab1, tab2 = st.tabs(["✏️  Paste / Type", "📁  Upload .eml File"])

sender_val  = ""
subject_val = ""
body_val    = ""

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
    # Key changes on every clear so Streamlit creates a brand-new uploader (empty)
    eml_key  = f"eml_upload_{st.session_state.get('eml_uploader_key', 0)}"
    eml_file = st.file_uploader("Upload .eml file", type=["eml", "msg"],
                                label_visibility="collapsed", key=eml_key)

    if eml_file is not None:
        file_bytes = eml_file.read()
        sender_val, subject_val, body_val = parse_eml(file_bytes)
        st.success("Email parsed successfully!")
        st.markdown(f"**From:** `{sender_val}`")
        st.markdown(f"**Subject:** `{subject_val}`")
        with st.expander("Preview extracted body text"):
            st.write(body_val[:1000] + ("..." if len(body_val) > 1000 else ""))

# ---------------------------------------------------------------------------
# Session state — persists results across reruns
# ---------------------------------------------------------------------------
if "result" not in st.session_state:
    st.session_state.result = None
if "eml_uploader_key" not in st.session_state:
    st.session_state.eml_uploader_key = 0

# Callback: runs BEFORE page re-renders (so widgets haven't been drawn yet)
def clear_all():
    st.session_state.result          = None
    st.session_state.t1_sender       = ""
    st.session_state.t1_subject      = ""
    st.session_state.t1_body         = ""
    # Increment key → Streamlit creates a brand-new empty file uploader
    st.session_state.eml_uploader_key += 1

# ---------------------------------------------------------------------------
# Analyse + Clear Buttons
# ---------------------------------------------------------------------------
st.markdown("---")
col1, col2, col3 = st.columns([2, 1, 1])

with col2:
    analyse = st.button("🔍 Analyse Email", type="primary", use_container_width=True)
with col3:
    st.button("🗑️ Clear", use_container_width=True, on_click=clear_all)


# Handle Analyse
if analyse:
    combined = f"{subject_val} {subject_val} {sender_val} {body_val}".strip()

    if not combined.strip():
        st.warning("Please provide at least a message body to analyse.")
    else:
        with st.spinner("Analysing..."):
            label, spam_pct, cleaned = predict(combined)

        if label is None:
            st.error("No meaningful text found after cleaning (only numbers/punctuation).")
        else:
            # Store result in session state
            st.session_state.result = {
                "label":      label,
                "spam_pct":   spam_pct,
                "cleaned":    cleaned,
                "sender":     sender_val,
                "subject":    subject_val,
            }

# ---------------------------------------------------------------------------
# Result Display — only shown when a result exists in session state
# ---------------------------------------------------------------------------
if st.session_state.result:
    r       = st.session_state.result
    label   = r["label"]
    spam_pct = r["spam_pct"]
    ham_pct = 100 - spam_pct
    cleaned  = r["cleaned"]

    # ── Result Card ───────────────────────────────────────────────────────
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

    # ── Confidence Bar ────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"**Spam probability:** {spam_pct:.1f}%")
    st.progress(int(spam_pct))

    # ── Visual Analysis & Explainability Expander (PBL / Academic Feature) ──
    with st.expander("Visual Analysis & Model Explainability (Charts)", expanded=True):
        st.markdown("#### 1. Prediction Probability Breakdown")
        conf_chart = build_confidence_chart(spam_pct, ham_pct)
        st.altair_chart(conf_chart, use_container_width=True)

        st.markdown("#### 2. Term Influence Analysis (Explainable AI)")
        st.caption(
            "Visualizing the mathematical contribution of tokens in this message towards "
            "classification using Naive Bayes log-odds impact."
        )

        df_contributions = get_feature_contributions(cleaned, top_n=10)
        if df_contributions.empty:
            st.info("No matching vocabulary tokens found in this message to compute individual term weights.")
        else:
            word_chart = build_word_impact_chart(df_contributions)
            st.altair_chart(word_chart, use_container_width=True)

    # ── Details Expander ──────────────────────────────────────────────────
    with st.expander("Show analysis details"):
        if r["sender"]:
            st.markdown(f"**Sender:** `{r['sender']}`")
        if r["subject"]:
            st.markdown(f"**Subject:** `{r['subject']}`")
        st.markdown("**Cleaned text fed to model:**")
        st.code(cleaned[:500] + ("..." if len(cleaned) > 500 else ""), language=None)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;color:#374151;font-size:0.8rem;'>"
    "Spam Email Detector &middot; PBL Project &middot; All processing is 100% local"
    "</p>",
    unsafe_allow_html=True
)
