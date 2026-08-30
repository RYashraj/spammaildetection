"""
Phase 3 -- Modeling
Assigned to: Meet

Steps:
  1. Load pickled TF-IDF train/test splits (models/train_test_splits.pkl)
  2. Train MultinomialNB
  3. Tune alpha via GridSearchCV(cv=5, scoring='f1')
  4. Evaluate best model: accuracy, precision, recall, F1, confusion matrix, classification_report
  5. Save best model to models/spam_model.pkl
"""

import os
import pickle
import pandas as pd
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
INPUT_DATA = os.path.join("models", "train_test_splits.pkl")
OUTPUT_MODEL = os.path.join("models", "spam_model.pkl")

# ---------------------------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------------------------
if not os.path.exists(INPUT_DATA):
    raise FileNotFoundError(
        f"[ERROR] '{INPUT_DATA}' not found. Run phase2_eda_vectorization.py first."
    )

print(f"[INFO] Loading train/test splits from '{INPUT_DATA}'...")
with open(INPUT_DATA, "rb") as f:
    X_train, X_test, y_train, y_test = pickle.load(f)

print(f"       X_train shape: {X_train.shape}")
print(f"       X_test shape:  {X_test.shape}")

# ---------------------------------------------------------------------------
# 2 & 3. Train and Tune Model (GridSearchCV)
# ---------------------------------------------------------------------------
print("\n[INFO] Tuning Multinomial Naive Bayes via GridSearchCV (cv=5)...")
# Define the parameter grid (alpha is the smoothing parameter)
param_grid = {"alpha": [0.01, 0.1, 0.5, 1.0, 5.0, 10.0]}

# Initialize the model and GridSearchCV
mnb = MultinomialNB()
grid_search = GridSearchCV(
    estimator=mnb,
    param_grid=param_grid,
    cv=5,
    scoring="f1",  # Optimizing for F1-score (balance of precision and recall)
    n_jobs=-1,      # Use all available CPU cores
    verbose=1
)

# Fit the model
grid_search.fit(X_train, y_train)

# Get the best model
best_model = grid_search.best_estimator_
print(f"[INFO] Best alpha parameter found: {grid_search.best_params_['alpha']}")
print(f"[INFO] Best cross-validation F1-score: {grid_search.best_score_:.4f}")

# ---------------------------------------------------------------------------
# 4. Evaluate Best Model
# ---------------------------------------------------------------------------
print("\n[INFO] Evaluating best model on test data...")
y_pred = best_model.predict(X_test)

acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
conf_matrix = confusion_matrix(y_test, y_pred)

print(f"\n--- Evaluation Metrics ---")
print(f"Accuracy : {acc:.4f} (Overall correctness)")
print(f"Precision: {prec:.4f} (When it predicts spam, how often is it right?)")
print(f"Recall   : {rec:.4f} (Out of all real spam, how much did it find?)")
print(f"F1-Score : {f1:.4f} (Harmonic mean of Precision and Recall)")

print("\n--- Confusion Matrix ---")
print(f"                     Predicted Ham (0)   Predicted Spam (1)")
print(f"Actual Ham (0) : {conf_matrix[0, 0]:>17} {conf_matrix[0, 1]:>20}")
print(f"Actual Spam (1): {conf_matrix[1, 0]:>17} {conf_matrix[1, 1]:>20}")

print("\n--- Classification Report ---")
print(classification_report(y_test, y_pred, target_names=["Ham", "Spam"]))

# ---------------------------------------------------------------------------
# 5. Save Best Model
# ---------------------------------------------------------------------------
print(f"\n[INFO] Saving best model to '{OUTPUT_MODEL}'...")
with open(OUTPUT_MODEL, "wb") as f:
    pickle.dump(best_model, f)

print("[DONE] Phase 3 complete. Model is ready for the Phase 4 UI (Vishwajeet).")
