"""
Phase 2 -- EDA & Vectorization
Assigned to: Shreyas

Steps:
  1. Load data/cleaned_spam.csv
  2. EDA: class distribution bar chart, message length histogram, top-20 word freq per class
  3. TF-IDF vectorization (max_features=3000, ngram_range=(1,2))
  4. Stratified train/test split 80/20, random_state=42
  5. Save vectorizer + splits to models/ via pickle
"""

import os
import pickle
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # non-interactive backend (safe on all machines)
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
sns.set_theme(style="darkgrid", palette="muted")
PLOTS_DIR = "plots"
os.makedirs(PLOTS_DIR, exist_ok=True)
os.makedirs("models", exist_ok=True)

INPUT_PATH  = os.path.join("data", "cleaned_spam.csv")
OUTPUT_VECT = os.path.join("models", "vectorizer.pkl")
OUTPUT_DATA = os.path.join("models", "train_test_splits.pkl")

# ---------------------------------------------------------------------------
# 1. Load cleaned data
# ---------------------------------------------------------------------------
if not os.path.exists(INPUT_PATH):
    raise FileNotFoundError(
        f"[ERROR] '{INPUT_PATH}' not found. Run phase1_data_preparation.py first."
    )

df = pd.read_csv(INPUT_PATH)
df["message"] = df["message"].fillna("").astype(str)
df["label"]   = df["label"].astype(int)

print(f"[INFO] Loaded cleaned dataset -- {len(df)} rows")
print(df["label"].value_counts().rename({0: "Ham", 1: "Spam"}))

# ---------------------------------------------------------------------------
# 2a. EDA -- Class distribution bar chart
# ---------------------------------------------------------------------------
label_counts = df["label"].value_counts().sort_index()
fig, ax = plt.subplots(figsize=(6, 4))
bars = ax.bar(
    ["Ham (0)", "Spam (1)"],
    label_counts.values,
    color=["#4C9BE8", "#E8664C"],
    edgecolor="white",
    linewidth=1.2,
)
for bar, val in zip(bars, label_counts.values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 40,
        str(val),
        ha="center", va="bottom", fontweight="bold", fontsize=11,
    )
ax.set_title("Class Distribution (Ham vs Spam)", fontsize=14, fontweight="bold", pad=12)
ax.set_ylabel("Message Count")
ax.set_ylim(0, label_counts.max() * 1.15)
plt.tight_layout()
path_dist = os.path.join(PLOTS_DIR, "class_distribution.png")
plt.savefig(path_dist, dpi=150)
plt.close()
print(f"[INFO] Saved -> {path_dist}")

# ---------------------------------------------------------------------------
# 2b. EDA -- Message length histogram by class
# ---------------------------------------------------------------------------
df["msg_len"] = df["message"].apply(lambda x: len(x.split()))

fig, ax = plt.subplots(figsize=(8, 4))
for label, color, name in [(0, "#4C9BE8", "Ham"), (1, "#E8664C", "Spam")]:
    subset = df[df["label"] == label]["msg_len"]
    ax.hist(subset, bins=40, alpha=0.65, color=color, label=f"{name} (mean={subset.mean():.0f})")
ax.set_title("Message Length Distribution by Class", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Word Count per Message")
ax.set_ylabel("Frequency")
ax.legend()
plt.tight_layout()
path_len = os.path.join(PLOTS_DIR, "message_length_distribution.png")
plt.savefig(path_len, dpi=150)
plt.close()
print(f"[INFO] Saved -> {path_len}")

# ---------------------------------------------------------------------------
# 2c. EDA -- Top-20 word frequency per class
# ---------------------------------------------------------------------------
def top_words(series, n=20):
    """Return top-n (word, count) pairs from a Series of space-separated tokens."""
    counter = Counter()
    for text in series:
        counter.update(text.split())
    return counter.most_common(n)


for label, color, name in [(0, "#4C9BE8", "Ham"), (1, "#E8664C", "Spam")]:
    words, counts = zip(*top_words(df[df["label"] == label]["message"]))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(list(reversed(words)), list(reversed(counts)), color=color, edgecolor="white")
    ax.set_title(f"Top-20 Words -- {name} Messages", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Frequency")
    plt.tight_layout()
    path_words = os.path.join(PLOTS_DIR, f"top20_words_{name.lower()}.png")
    plt.savefig(path_words, dpi=150)
    plt.close()
    print(f"[INFO] Saved -> {path_words}")

# ---------------------------------------------------------------------------
# 3. TF-IDF Vectorization
# ---------------------------------------------------------------------------
print("\n[INFO] Fitting TF-IDF vectorizer (max_features=3000, ngram_range=(1,2))...")
vectorizer = TfidfVectorizer(max_features=3000, ngram_range=(1, 2), sublinear_tf=True)
X = vectorizer.fit_transform(df["message"])
y = df["label"].values

print(f"[INFO] Feature matrix shape: {X.shape}")   # (5572, 3000)

# ---------------------------------------------------------------------------
# 4. Stratified train/test split 80/20
# ---------------------------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

print(f"[INFO] Train size : {X_train.shape[0]} samples")
print(f"[INFO] Test  size : {X_test.shape[0]} samples")
print(f"[INFO] Train spam%: {y_train.mean()*100:.1f}%  | Test spam%: {y_test.mean()*100:.1f}%")

# ---------------------------------------------------------------------------
# 5. Save vectorizer and splits via pickle
# ---------------------------------------------------------------------------
with open(OUTPUT_VECT, "wb") as f:
    pickle.dump(vectorizer, f)
print(f"\n[INFO] Vectorizer saved -> {OUTPUT_VECT}")

with open(OUTPUT_DATA, "wb") as f:
    pickle.dump((X_train, X_test, y_train, y_test), f)
print(f"[INFO] Train/test splits saved -> {OUTPUT_DATA}")

print("\n[DONE] Phase 2 complete. Models folder ready for Phase 3 (Meet).")
