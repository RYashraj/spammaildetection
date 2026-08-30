"""
PPT Generator for Spam Email Detection Project
D2D Batch, Sem 5
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from lxml import etree
import copy

# ─── Color Palette ────────────────────────────────────────────────────────────
NAVY       = RGBColor(0x1A, 0x1F, 0x3C)
BLUE       = RGBColor(0x23, 0x5D, 0xC8)
LIGHT_BLUE = RGBColor(0xDB, 0xE9, 0xFF)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_GRAY = RGBColor(0xF1, 0xF5, 0xF9)
MID_GRAY   = RGBColor(0x94, 0xA3, 0xB8)
DARK_TEXT  = RGBColor(0x1E, 0x29, 0x3B)
GREEN      = RGBColor(0x05, 0x96, 0x69)
RED        = RGBColor(0xDC, 0x26, 0x26)
ACCENT     = RGBColor(0xF5, 0x9E, 0x0B)

prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)

BLANK = prs.slide_layouts[6]   # completely blank layout

# ─── Helper Functions ─────────────────────────────────────────────────────────

def add_rect(slide, l, t, w, h, fill_color, radius=0):
    shape = slide.shapes.add_shape(1, Inches(l), Inches(t), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.fill.background()
    return shape

def add_textbox(slide, text, l, t, w, h,
                font_size=18, bold=False, color=DARK_TEXT,
                align=PP_ALIGN.LEFT, wrap=True, italic=False):
    txb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    txb.word_wrap = wrap
    tf  = txb.text_frame
    tf.word_wrap = wrap
    p   = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size  = Pt(font_size)
    run.font.bold  = bold
    run.font.color.rgb = color
    run.font.italic = italic
    return txb

def add_para(tf, text, font_size=16, bold=False, color=DARK_TEXT,
             align=PP_ALIGN.LEFT, space_before=6, italic=False):
    p = tf.add_paragraph()
    p.alignment = align
    p.space_before = Pt(space_before)
    run = p.add_run()
    run.text = text
    run.font.size  = Pt(font_size)
    run.font.bold  = bold
    run.font.color.rgb = color
    run.font.italic = italic
    return p

def add_bullet_box(slide, items, l, t, w, h,
                   font_size=15, color=DARK_TEXT, bullet="•  "):
    txb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    txb.word_wrap = True
    tf  = txb.text_frame
    tf.word_wrap = True
    first = True
    for item in items:
        if first:
            p = tf.paragraphs[0]
            first = False
        else:
            p = tf.add_paragraph()
        p.space_before = Pt(5)
        run = p.add_run()
        run.text = bullet + item
        run.font.size  = Pt(font_size)
        run.font.color.rgb = color
    return txb

def header_bar(slide, title, subtitle=None):
    """Blue top bar with white title text."""
    add_rect(slide, 0, 0, 13.33, 1.4, NAVY)
    add_textbox(slide, title, 0.4, 0.12, 12.5, 0.7,
                font_size=28, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
    if subtitle:
        add_textbox(slide, subtitle, 0.4, 0.82, 12.5, 0.45,
                    font_size=14, color=LIGHT_BLUE, align=PP_ALIGN.LEFT)

def footer(slide, page_num, total=12):
    add_rect(slide, 0, 7.18, 13.33, 0.32, NAVY)
    add_textbox(slide, "Spam Email Detection  |  D2D Batch  |  Sem 5",
                0.3, 7.2, 9, 0.28, font_size=10, color=MID_GRAY)
    add_textbox(slide, f"{page_num} / {total}",
                12.5, 7.2, 0.8, 0.28, font_size=10, color=MID_GRAY,
                align=PP_ALIGN.RIGHT)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 1 — Title
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)

# full background
add_rect(s, 0, 0, 13.33, 7.5, NAVY)

# blue accent strip on left
add_rect(s, 0, 0, 0.25, 7.5, BLUE)

# email icon placeholder (big ✉ emoji)
add_textbox(s, "📧", 0.8, 0.9, 2, 2, font_size=80, color=WHITE)

# Title
add_textbox(s, "Spam Email Detection System",
            3.0, 1.3, 9.8, 1.2,
            font_size=38, bold=True, color=WHITE)

add_textbox(s, "AI-Powered Mail Classifier using NLP & Naive Bayes",
            3.0, 2.55, 9.8, 0.7,
            font_size=18, color=LIGHT_BLUE)

# divider
add_rect(s, 3.0, 3.4, 7, 0.04, BLUE)

# Team & batch info
add_textbox(s, "D2D Batch  |  Sem 5  |  PBL Project",
            3.0, 3.55, 9, 0.5, font_size=15, color=MID_GRAY)

add_textbox(s, "Team Members:   Yashraj  ·  Shreyas  ·  Meet  ·  Vishwajeet",
            3.0, 4.1, 9.5, 0.5, font_size=16, bold=True, color=WHITE)

footer(s, 1)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 2 — Problem Statement
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, 13.33, 7.5, LIGHT_GRAY)
header_bar(s, "The Problem", "Why does spam detection matter?")

# Left column — statistics
add_rect(s, 0.4, 1.6, 3.8, 1.1, RED)
add_textbox(s, "45%", 0.4, 1.6, 3.8, 0.7,
            font_size=36, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
add_textbox(s, "of all emails worldwide are spam",
            0.4, 2.2, 3.8, 0.4, font_size=12, color=WHITE, align=PP_ALIGN.CENTER)

add_rect(s, 0.4, 2.9, 3.8, 1.1, BLUE)
add_textbox(s, "₹ Crores",0.4, 2.9, 3.8, 0.7,
            font_size=32, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
add_textbox(s, "lost to phishing scams every year in India",
            0.4, 3.5, 3.8, 0.4, font_size=12, color=WHITE, align=PP_ALIGN.CENTER)

add_rect(s, 0.4, 4.2, 3.8, 1.1, GREEN)
add_textbox(s, "Millions",0.4, 4.2, 3.8, 0.7,
            font_size=32, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
add_textbox(s, "of users deceived by fake 'selected' or 'winner' mails",
            0.4, 4.8, 3.8, 0.4, font_size=12, color=WHITE, align=PP_ALIGN.CENTER)

# Right column — problem description
add_textbox(s, "What is Spam?",
            4.6, 1.55, 8.3, 0.5, font_size=18, bold=True, color=NAVY)
add_bullet_box(s, [
    "Unsolicited, unwanted emails sent in bulk",
    "Contains fake prizes, urgent threats, phishing links",
    "Wastes time and poses serious security risks",
    "Manually filtering them is inefficient and unreliable",
], 4.6, 2.1, 8.3, 2.2, font_size=15)

add_textbox(s, "Our Goal:",
            4.6, 4.4, 8.3, 0.5, font_size=18, bold=True, color=NAVY)
add_textbox(s,
    "Build an intelligent system that automatically detects "
    "whether an email is Spam or Ham (safe) — using Machine Learning.",
    4.6, 4.9, 8.3, 1.2, font_size=15, color=DARK_TEXT)

footer(s, 2)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 3 — Our Solution (Overview)
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, 13.33, 7.5, LIGHT_GRAY)
header_bar(s, "Our Solution", "What we built and why")

# Two columns
# Left: What
add_rect(s, 0.4, 1.6, 5.9, 5.3, WHITE)
add_textbox(s, "What We Built", 0.7, 1.75, 5.3, 0.5,
            font_size=17, bold=True, color=BLUE)
add_bullet_box(s, [
    "A 5-phase ML pipeline from raw data to live app",
    "NLP-based text cleaning & lemmatization",
    "TF-IDF vectorization to convert text to numbers",
    "Multinomial Naive Bayes classifier (98% accuracy)",
    "Streamlit web app with 2 input modes:",
    "   – Paste text (Subject + Sender + Body)",
    "   – Upload a real .eml email file",
    "Clear button, result confidence bar, analysis view",
], 0.7, 2.35, 5.5, 4.0, font_size=14)

# Right: Why
add_rect(s, 6.7, 1.6, 6.2, 2.45, WHITE)
add_textbox(s, "Why This Approach?", 7.0, 1.75, 5.8, 0.5,
            font_size=17, bold=True, color=BLUE)
add_bullet_box(s, [
    "Naive Bayes is the industry standard for text spam",
    "TF-IDF captures word importance, not just frequency",
    "Lightweight — runs fully on your local machine",
    "No data is ever sent to any server",
], 7.0, 2.35, 5.8, 1.5, font_size=14)

add_rect(s, 6.7, 4.25, 6.2, 2.65, WHITE)
add_textbox(s, "Dataset Used", 7.0, 4.4, 5.8, 0.5,
            font_size=17, bold=True, color=BLUE)
add_bullet_box(s, [
    "SMS Spam Collection (UCI ML Repository / Kaggle)",
    "5,572 messages — 4,825 Ham + 747 Spam",
    "Same NLP pipeline applies to emails — technique is identical",
], 7.0, 4.95, 5.8, 1.6, font_size=14)

footer(s, 3)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 4 — Tech Stack
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, 13.33, 7.5, LIGHT_GRAY)
header_bar(s, "Technology Stack", "Tools and libraries used")

techs = [
    ("Python 3.12",   "Core programming language",         "🐍"),
    ("NLTK",          "Stopword removal, lemmatization",    "🔤"),
    ("Scikit-learn",  "TF-IDF vectorizer + Naive Bayes",   "🤖"),
    ("Pandas",        "Data loading and manipulation",     "📊"),
    ("Matplotlib /\nSeaborn", "EDA visualizations",        "📈"),
    ("Streamlit",     "Interactive web application UI",    "🌐"),
    ("Pickle",        "Save & load trained model files",   "💾"),
    ("email (stdlib)","Parse .eml files safely",           "📧"),
]

cols = 4
per_col = 2
box_w = 2.9
box_h = 2.2
gap_x = 0.35
gap_y = 0.35
start_x = 0.4
start_y = 1.55

for i, (name, desc, icon) in enumerate(techs):
    col = i % cols
    row = i // cols
    x = start_x + col * (box_w + gap_x)
    y = start_y + row * (box_h + gap_y)
    add_rect(s, x, y, box_w, box_h, WHITE)
    add_textbox(s, icon, x + 0.1, y + 0.1, 0.7, 0.6, font_size=26)
    add_textbox(s, name, x + 0.1, y + 0.65, box_w - 0.2, 0.45,
                font_size=15, bold=True, color=NAVY)
    add_textbox(s, desc, x + 0.1, y + 1.1, box_w - 0.2, 0.8,
                font_size=12, color=MID_GRAY)

footer(s, 4)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 5 — Project Pipeline
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, 13.33, 7.5, LIGHT_GRAY)
header_bar(s, "Project Pipeline", "5 phases from raw data to live web app")

phases = [
    ("Phase 1",    "Data\nPreparation",  "Clean text, encode labels", BLUE),
    ("Phase 2",    "EDA &\nVectorize",   "Explore data, TF-IDF",      RGBColor(0x70, 0x5C, 0xDB)),
    ("Phase 3",    "Model\nTraining",    "Train Naive Bayes (98%)",    GREEN),
    ("Phase 4",    "Web App\nUI",        "Streamlit interface",        ACCENT),
    ("Phase 5",    "Smart\nInput",       ".eml parser, Clear button",  RED),
]

bw = 2.0
bh = 2.6
gap = 0.35
sy = 2.0

for i, (ph, title, desc, color) in enumerate(phases):
    x = 0.4 + i * (bw + gap)
    add_rect(s, x, sy, bw, bh, color)
    add_textbox(s, ph,    x+0.1, sy+0.1,   bw-0.2, 0.4,  font_size=12, color=WHITE, align=PP_ALIGN.CENTER)
    add_textbox(s, title, x+0.1, sy+0.5,   bw-0.2, 0.9,  font_size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_textbox(s, desc,  x+0.1, sy+1.45,  bw-0.2, 0.85, font_size=12, color=WHITE, align=PP_ALIGN.CENTER)

    # arrow (except after last)
    if i < len(phases) - 1:
        ax = x + bw + 0.05
        add_textbox(s, "→", ax, sy + 0.95, 0.3, 0.5,
                    font_size=22, bold=True, color=NAVY, align=PP_ALIGN.CENTER)

# bottom note
add_textbox(s,
    "Each phase produces an output that feeds directly into the next phase — a complete, end-to-end Machine Learning pipeline.",
    0.4, 4.85, 12.5, 0.6, font_size=14, color=DARK_TEXT, align=PP_ALIGN.CENTER)

footer(s, 5)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 6 — Phase 1: Data Preparation (Yashraj)
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, 13.33, 7.5, LIGHT_GRAY)
header_bar(s, "Phase 1 — Data Preparation", "File: phase1_data_preparation.py  |  Lead: Yashraj")

add_rect(s, 0.4, 1.6, 5.9, 5.3, WHITE)
add_textbox(s, "What was done?", 0.7, 1.75, 5.3, 0.5,
            font_size=17, bold=True, color=BLUE)
add_bullet_box(s, [
    "Loaded SMS Spam Collection dataset (spam.csv)",
    "Removed duplicate and null entries",
    "Converted text to lowercase",
    "Removed punctuation, numbers & URLs",
    "Removed stop words (e.g. 'the', 'is', 'a')",
    "Applied Lemmatization (e.g. 'running' → 'run')",
    "Encoded labels: ham = 0, spam = 1",
    "Saved cleaned data to: data/cleaned_spam.csv",
    "Checked and reported class imbalance",
], 0.7, 2.35, 5.5, 4.2, font_size=14)

add_rect(s, 6.7, 1.6, 6.2, 2.5, WHITE)
add_textbox(s, "Output", 7.0, 1.75, 5.8, 0.5,
            font_size=17, bold=True, color=BLUE)
add_bullet_box(s, [
    "cleaned_spam.csv  →  5,572 rows",
    "4,825 Ham messages (86.6%)",
    "   747 Spam messages (13.4%)",
], 7.0, 2.35, 5.8, 1.5, font_size=15)

add_rect(s, 6.7, 4.3, 6.2, 2.6, WHITE)
add_textbox(s, "Why these steps?", 7.0, 4.45, 5.8, 0.5,
            font_size=17, bold=True, color=BLUE)
add_bullet_box(s, [
    "ML models cannot understand raw noisy text",
    "Stop words add no spam-detection value",
    "Lemmatization reduces word variety so the",
    "  model learns patterns, not exact spellings",
], 7.0, 5.0, 5.8, 1.7, font_size=14)

footer(s, 6)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 7 — Phase 2: EDA & Vectorization (Shreyas)
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, 13.33, 7.5, LIGHT_GRAY)
header_bar(s, "Phase 2 — EDA & Vectorization", "File: phase2_eda_vectorization.py  |  Lead: Shreyas")

add_rect(s, 0.4, 1.6, 5.9, 5.3, WHITE)
add_textbox(s, "Exploratory Data Analysis (EDA)", 0.7, 1.75, 5.3, 0.5,
            font_size=17, bold=True, color=BLUE)
add_bullet_box(s, [
    "Plotted class distribution (Ham vs Spam bar chart)",
    "Word count distribution — spam msgs are longer",
    "Generated Word Clouds for spam and ham words",
    "Top 15 most frequent words in spam messages",
    "Correlation between message length & spam label",
    "All plots saved to: plots/ folder",
], 0.7, 2.35, 5.5, 2.8, font_size=14)

add_textbox(s, "TF-IDF Vectorization", 0.7, 5.2, 5.3, 0.5,
            font_size=17, bold=True, color=BLUE)
add_bullet_box(s, [
    "Converted cleaned text into numerical feature matrix",
    "max_features = 5,000 most important words",
    "Split data: 80% train / 20% test",
    "Saved: vectorizer.pkl, train_test_splits.pkl",
], 0.7, 5.75, 5.5, 1.1, font_size=14)

add_rect(s, 6.7, 1.6, 6.2, 5.3, WHITE)
add_textbox(s, "What is TF-IDF?", 7.0, 1.75, 5.8, 0.5,
            font_size=17, bold=True, color=BLUE)
add_textbox(s,
    "TF-IDF stands for Term Frequency - Inverse Document Frequency.",
    7.0, 2.35, 5.8, 0.5, font_size=14, bold=True, color=DARK_TEXT)
add_bullet_box(s, [
    "TF: How often does a word appear in this message?",
    "IDF: How rare is this word across all messages?",
    "",
    "Words like 'FREE', 'WIN', 'CLAIM' appear very",
    "often in spam but rarely in normal messages →",
    "they get a HIGH TF-IDF score → model learns",
    "that these words = high spam probability.",
    "",
    "Common words like 'the', 'you', 'is' appear",
    "everywhere → low IDF → low score → ignored.",
], 7.0, 2.95, 5.8, 3.5, font_size=14)

footer(s, 7)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 8 — Phase 3: Model Training (Meet)
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, 13.33, 7.5, LIGHT_GRAY)
header_bar(s, "Phase 3 — ML Model Training", "File: phase3_modeling.py  |  Lead: Meet")

add_rect(s, 0.4, 1.6, 5.9, 5.3, WHITE)
add_textbox(s, "Model: Multinomial Naive Bayes", 0.7, 1.75, 5.5, 0.5,
            font_size=17, bold=True, color=BLUE)
add_bullet_box(s, [
    "Loaded train/test data from vectorizer output",
    "Trained MultinomialNB with alpha=0.1 (tuned)",
    "Evaluated on 1,115 unseen test messages",
    "Performed hyperparameter search for best alpha",
    "Saved final model to: models/spam_model.pkl",
], 0.7, 2.35, 5.5, 2.3, font_size=14)

add_textbox(s, "Results", 0.7, 4.75, 5.5, 0.5,
            font_size=17, bold=True, color=BLUE)

# Accuracy box
add_rect(s, 0.7, 5.3, 2.4, 1.3, GREEN)
add_textbox(s, "98%",       0.7, 5.35, 2.4, 0.8, font_size=36, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
add_textbox(s, "Accuracy",  0.7, 6.1,  2.4, 0.4, font_size=13, color=WHITE, align=PP_ALIGN.CENTER)

add_rect(s, 3.3, 5.3, 2.8, 1.3, BLUE)
add_textbox(s, "~1 ms",       3.3, 5.35, 2.8, 0.8, font_size=36, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
add_textbox(s, "Prediction time", 3.3, 6.1, 2.8, 0.4, font_size=13, color=WHITE, align=PP_ALIGN.CENTER)

# Right col
add_rect(s, 6.7, 1.6, 6.2, 5.3, WHITE)
add_textbox(s, "Why Naive Bayes?", 7.0, 1.75, 5.8, 0.5,
            font_size=17, bold=True, color=BLUE)
add_bullet_box(s, [
    "Specifically designed for text classification",
    "Calculates probability of spam vs ham based",
    "  on the frequency of each TF-IDF word",
    "Extremely fast — trains in seconds",
    "Proven industry standard: used in Gmail,",
    "  Yahoo Mail spam filters since early 2000s",
    "",
    "Confusion Matrix (on test set of 1,115):",
    "  True Ham:   966  |  False Spam:  9",
    "  True Spam:  124  |  False Ham:  16",
], 7.0, 2.35, 5.8, 4.5, font_size=14)

footer(s, 8)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 9 — Phase 4 & 5: Web App (Vishwajeet)
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, 13.33, 7.5, LIGHT_GRAY)
header_bar(s, "Phase 4 & 5 — Web Application", "File: app.py  |  Lead: Vishwajeet")

add_rect(s, 0.4, 1.6, 5.9, 5.3, WHITE)
add_textbox(s, "What was built", 0.7, 1.75, 5.3, 0.5,
            font_size=17, bold=True, color=BLUE)
add_bullet_box(s, [
    "Interactive Streamlit web application (app.py)",
    "Loads trained model & vectorizer on startup",
    "Two input modes (tabs):",
    "   ✏️  Tab 1: Paste Sender + Subject + Body",
    "   📁  Tab 2: Upload a .eml email file",
    "Auto-parses .eml → fills all fields automatically",
    "Safe: attachments are NEVER opened or executed",
    "Clear button resets all inputs and results",
    "Confidence progress bar for visual clarity",
    "Analysis details expander (shows cleaned text)",
    "Premium dark UI with Inter font & custom CSS",
], 0.7, 2.35, 5.5, 4.3, font_size=14)

add_rect(s, 6.7, 1.6, 6.2, 5.3, WHITE)
add_textbox(s, "How to use it", 7.0, 1.75, 5.8, 0.5,
            font_size=17, bold=True, color=BLUE)
add_bullet_box(s, [
    "Run:  python -m streamlit run app.py",
    "Opens at: http://localhost:8501",
    "",
    "Option A — Type/Paste:",
    "  Enter Sender, Subject, and Body",
    "  → Click 🔍 Analyse Email",
    "",
    "Option B — .eml File:",
    "  In Gmail: ⋮ More → Download message",
    "  Upload the .eml file to the app",
    "  → Fields are filled automatically",
    "  → Click 🔍 Analyse Email",
    "",
    "Result shows: SPAM 🚨 or HAM ✅ + confidence %",
], 7.0, 2.35, 5.8, 4.5, font_size=14)

footer(s, 9)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 10 — Team Contributions
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, 13.33, 7.5, LIGHT_GRAY)
header_bar(s, "Team Contributions", "D2D Batch  |  Sem 5  |  Each member owned a complete phase")

members = [
    ("Yashraj",     "Data Engineer",    BLUE,
     "Phase 1 — Data Preparation",
     ["Sourced & loaded the SMS Spam dataset",
      "Built the full NLP cleaning pipeline",
      "Stopword removal, lemmatization, label encoding",
      "Generated cleaned_spam.csv (5,572 rows)"]),
    ("Shreyas",     "Data Analyst",     RGBColor(0x70, 0x5C, 0xDB),
     "Phase 2 — EDA & Vectorization",
     ["Generated EDA visualizations & word clouds",
      "Analysed spam vs ham word patterns",
      "Built TF-IDF vectorizer (5,000 features)",
      "Created 80/20 train-test split"]),
    ("Meet",        "ML Engineer",      GREEN,
     "Phase 3 — Model Training",
     ["Trained Multinomial Naive Bayes classifier",
      "Tuned hyperparameter alpha for best performance",
      "Achieved 98% accuracy on 1,115 test messages",
      "Saved final model as spam_model.pkl"]),
    ("Vishwajeet",  "UI Developer",     ACCENT,
     "Phase 4 & 5 — Web Application",
     ["Built Streamlit web app (app.py)",
      "Added .eml file upload & auto-parsing",
      "Implemented Clear button with session state",
      "Designed premium dark UI with custom CSS"]),
]

bw = 2.9
bh = 5.1
gap = 0.36
sy = 1.55

for i, (name, role, color, phase, bullets) in enumerate(members):
    x = 0.35 + i * (bw + gap)
    add_rect(s, x, sy, bw, 0.9, color)
    add_textbox(s, name, x+0.1, sy+0.05, bw-0.2, 0.45,
                font_size=19, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_textbox(s, role, x+0.1, sy+0.5,  bw-0.2, 0.35,
                font_size=12, color=WHITE, align=PP_ALIGN.CENTER)
    add_rect(s, x, sy+0.9, bw, bh-0.9, WHITE)
    add_textbox(s, phase, x+0.15, sy+1.05, bw-0.3, 0.5,
                font_size=13, bold=True, color=color)
    add_bullet_box(s, bullets, x+0.15, sy+1.6, bw-0.3, 3.0,
                   font_size=12.5, color=DARK_TEXT, bullet="• ")

footer(s, 10)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 11 — Results & Key Learnings
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, 13.33, 7.5, LIGHT_GRAY)
header_bar(s, "Results & Key Learnings", "What we achieved and what we discovered")

# Metric boxes
metrics = [
    ("98%",     "Model Accuracy",          GREEN),
    ("5,572",   "Messages Trained On",     BLUE),
    ("~1 ms",   "Prediction Speed",        RGBColor(0x70, 0x5C, 0xDB)),
    ("2 Modes", "Input Methods in App",    ACCENT),
]
for i, (val, label, color) in enumerate(metrics):
    x = 0.4 + i * 3.15
    add_rect(s, x, 1.55, 2.8, 1.5, color)
    add_textbox(s, val,   x+0.1, 1.6, 2.6, 0.85, font_size=30, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_textbox(s, label, x+0.1, 2.4, 2.6, 0.5,  font_size=12,           color=WHITE, align=PP_ALIGN.CENTER)

# Learnings
add_rect(s, 0.4, 3.25, 5.9, 4.0, WHITE)
add_textbox(s, "Key Technical Learnings", 0.7, 3.4, 5.3, 0.5,
            font_size=17, bold=True, color=BLUE)
add_bullet_box(s, [
    "NLP preprocessing is crucial — raw text alone won't work",
    "TF-IDF is highly effective for short text classification",
    "Naive Bayes works because spam language is predictable",
    "Class imbalance (87% ham) is real — model must handle it",
    "False positives exist — e.g. 'You are selected for SIH'",
    "  is flagged spam because 'selected' = spam word in training data",
], 0.7, 3.95, 5.5, 2.8, font_size=14)

add_rect(s, 6.7, 3.25, 6.2, 4.0, WHITE)
add_textbox(s, "Known Limitations & Future Scope", 7.0, 3.4, 5.8, 0.5,
            font_size=17, bold=True, color=BLUE)
add_bullet_box(s, [
    "Trained on SMS data — email-specific dataset would improve",
    "Image-only spam (poster emails) cannot be read (no OCR)",
    "Sender domain reputation not deeply analyzed",
    "Future: Active Learning — user feedback retrains model",
    "Future: Gmail API integration for real-time scanning",
    "Future: Browser extension for in-browser detection",
], 7.0, 3.95, 5.8, 2.8, font_size=14)

footer(s, 11)

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 12 — Thank You
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(BLANK)
add_rect(s, 0, 0, 13.33, 7.5, NAVY)
add_rect(s, 0, 0, 0.25, 7.5, BLUE)

add_textbox(s, "Thank You!", 0.8, 1.5, 11.5, 1.4,
            font_size=52, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

add_rect(s, 3.5, 3.1, 6.33, 0.05, BLUE)

add_textbox(s,
    "Spam Email Detection System\nD2D Batch  |  Sem 5  |  PBL Project",
    0.8, 3.3, 11.5, 0.9,
    font_size=18, color=LIGHT_BLUE, align=PP_ALIGN.CENTER)

add_textbox(s,
    "Yashraj   ·   Shreyas   ·   Meet   ·   Vishwajeet",
    0.8, 4.35, 11.5, 0.6,
    font_size=20, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

add_textbox(s,
    "Built with Python  ·  NLTK  ·  Scikit-learn  ·  Streamlit",
    0.8, 5.1, 11.5, 0.5,
    font_size=14, color=MID_GRAY, align=PP_ALIGN.CENTER)

add_textbox(s,
    "github.com/RYashraj/spammaildetection",
    0.8, 5.75, 11.5, 0.5,
    font_size=13, color=LIGHT_BLUE, align=PP_ALIGN.CENTER, italic=True)

footer(s, 12)

# ─────────────────────────────────────────────────────────────────────────────
# Save
# ─────────────────────────────────────────────────────────────────────────────
output_path = r"c:\Self\Python\PBLPROJ\Spam_Email_Detection_PBL.pptx"
prs.save(output_path)
print(f"PPT saved: {output_path}")
