# Spam Email Detection — Project Plan

## Phase Assignment

| Phase | Deliverables | Assigned To |
|---|---|---|
| 1. Data Preparation | Dataset loading, cleaning, text preprocessing, imbalance check | Yashraj |
| 2. EDA & Vectorization | Exploratory analysis, visualizations, TF-IDF vectorization, train/test split | Shreyas |
| 3. Modeling | Model training (Multinomial Naive Bayes), hyperparameter tuning, evaluation metrics | Meet |
| 4. UI & Documentation | Streamlit prediction interface, README, final report | Vishwajeet |

---

## Antigravity Code-Generation Prompts

### Phase 1 — Data Preparation
```
Write Python script. Load SMS Spam Collection dataset (spam.csv, cols: label, message). Clean text: lowercase, strip punctuation/numbers, remove stopwords (NLTK), tokenize, lemmatize. Encode label ham=0/spam=1. Check class imbalance, print counts. Save output to cleaned_spam.csv. Output code only. No explanations.
```

### Phase 2 — EDA & Vectorization
```
Write Python script. Load cleaned_spam.csv. Plot class distribution bar chart, message length histogram by class, top-20 word frequency bar chart per class. Vectorize 'message' with TfidfVectorizer(max_features=3000, ngram_range=(1,2)). Stratified train_test_split 80/20, random_state=42. Save vectorizer, X_train, X_test, y_train, y_test via pickle. Output code only. No explanations.
```

### Phase 3 — Modeling
```
Write Python script. Load pickled TF-IDF train/test splits. Train MultinomialNB. Tune alpha via GridSearchCV(cv=5, scoring='f1'). Evaluate best model: accuracy, precision, recall, F1, confusion matrix, classification_report. Save best model as spam_model.pkl. Output code only. No explanations.
```

### Phase 4 — UI & Documentation
```
Write Streamlit app app.py. Load spam_model.pkl and vectorizer.pkl. Text input box for message. On submit: transform input, predict label, show "Spam"/"Ham" with confidence %. Clean minimal UI, title "Spam Email Detector". Also write README.md: project overview, setup steps, run command, folder structure. Output code only. No explanations.
```
