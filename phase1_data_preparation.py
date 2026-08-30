"""
Phase 1 — Data Preparation
Assigned to: Yashraj

Steps:
  1. Load SMS Spam Collection dataset (data/spam.csv)
  2. Clean text: lowercase, strip punctuation/numbers, remove stopwords, tokenize, lemmatize
  3. Encode label: ham=0, spam=1
  4. Check and print class imbalance
  5. Save output to data/cleaned_spam.csv
"""

import os
import re
import string
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# ---------------------------------------------------------------------------
# Download required NLTK data (safe to run multiple times)
# ---------------------------------------------------------------------------
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)
nltk.download("omw-1.4", quiet=True)

# ---------------------------------------------------------------------------
# 1. Load dataset
# ---------------------------------------------------------------------------
DATA_PATH = os.path.join("data", "spam.csv")

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(
        f"\n[ERROR] Dataset not found at '{DATA_PATH}'.\n"
        "Please follow the steps below to obtain it:\n"
        "  1. Go to https://www.kaggle.com/datasets/uciml/sms-spam-collection-dataset\n"
        "  2. Download 'spam.csv'\n"
        "  3. Place it inside the 'data/' folder of this project.\n"
        "Then re-run this script."
    )

# The UCI SMS Spam dataset uses Windows-1252 encoding and has extra unnamed cols
df = pd.read_csv(DATA_PATH, encoding="windows-1252", usecols=[0, 1])
df.columns = ["label", "message"]

print(f"[INFO] Dataset loaded — {len(df)} rows")
print(df.head())

# ---------------------------------------------------------------------------
# 2. Clean text
# ---------------------------------------------------------------------------
stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()


def clean_text(text: str) -> str:
    """
    Cleans a single message string:
      - Lowercase
      - Remove URLs
      - Remove punctuation and digits
      - Tokenise on whitespace
      - Remove English stopwords
      - Lemmatise each token
    """
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)          # remove URLs
    text = re.sub(r"[^a-z\s]", " ", text)               # keep only letters
    tokens = text.split()
    tokens = [t for t in tokens if t not in stop_words and len(t) > 1]
    tokens = [lemmatizer.lemmatize(t) for t in tokens]
    return " ".join(tokens)


print("[INFO] Cleaning text (this may take a moment)…")
df["message"] = df["message"].astype(str).apply(clean_text)

# ---------------------------------------------------------------------------
# 3. Encode labels: ham → 0, spam → 1
# ---------------------------------------------------------------------------
df["label"] = df["label"].str.strip().map({"ham": 0, "spam": 1})

# Drop any rows with NaN labels (shouldn't happen with a clean dataset)
before = len(df)
df.dropna(subset=["label"], inplace=True)
df["label"] = df["label"].astype(int)
if len(df) < before:
    print(f"[WARN] Dropped {before - len(df)} rows with unrecognised labels.")

# ---------------------------------------------------------------------------
# 4. Class imbalance check
# ---------------------------------------------------------------------------
counts = df["label"].value_counts()
print("\n[INFO] Class distribution after encoding:")
print(f"  Ham  (0): {counts.get(0, 0):>5} ({counts.get(0, 0)/len(df)*100:.1f}%)")
print(f"  Spam (1): {counts.get(1, 0):>5} ({counts.get(1, 0)/len(df)*100:.1f}%)")
print(f"  Imbalance ratio (ham:spam) ≈ {counts.get(0, 0)/counts.get(1, 1):.1f}:1")

# ---------------------------------------------------------------------------
# 5. Save cleaned data
# ---------------------------------------------------------------------------
OUTPUT_PATH = os.path.join("data", "cleaned_spam.csv")
df.to_csv(OUTPUT_PATH, index=False)
print(f"\n[INFO] Cleaned dataset saved → '{OUTPUT_PATH}'")
print(f"       Shape: {df.shape}")
print(df.head())
