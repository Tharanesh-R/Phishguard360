"""
CyberShield Advanced Phishing Detection Model Trainer
=====================================================
Trains a new Random Forest + Gradient Boosting ensemble model
using the dataset's URL features for phishing detection.
Memory-optimized version with chunked loading.
"""

import pandas as pd
import numpy as np
import joblib
import os
import sys
import gc
import warnings
warnings.filterwarnings("ignore")

from sklearn.model_selection import train_test_split
from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier,
    VotingClassifier
)
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

print("=" * 60)
print("  CyberShield Advanced Model Trainer")
print("=" * 60)
print()

# =============================
# STEP 1: Load Dataset (Memory-Optimized)
# =============================

print("[1/7] Loading dataset (memory-optimized)...")

try:
    # Read with reduced memory: use float32 instead of float64
    df = pd.read_csv(
        "dataset.csv",
        low_memory=True,
        dtype={col: "float32" for col in range(111)}  # numeric cols as float32
    )
    print(f"  Dataset loaded: {df.shape[0]:,} rows x {df.shape[1]} columns")
except Exception:
    # Fallback: load in chunks
    print("  Loading in chunks...")
    chunks = []
    for chunk in pd.read_csv("dataset.csv", chunksize=10000, low_memory=True):
        # Downcast numeric columns to save memory
        for col in chunk.select_dtypes(include=["float64"]).columns:
            chunk[col] = chunk[col].astype("float32")
        for col in chunk.select_dtypes(include=["int64"]).columns:
            chunk[col] = chunk[col].astype("int32")
        chunks.append(chunk)
    df = pd.concat(chunks, ignore_index=True)
    del chunks
    gc.collect()
    print(f"  Dataset loaded: {df.shape[0]:,} rows x {df.shape[1]} columns")

# =============================
# STEP 2: Prepare Data
# =============================

print("[2/7] Preparing data...")

label_col = "phishing"
if label_col not in df.columns:
    label_col = df.columns[-1]
    print(f"  Using last column as label: '{label_col}'")

# Map labels: -1 -> 0 if needed
unique_labels = set(df[label_col].unique())
if unique_labels == {-1, 1} or -1 in unique_labels:
    df[label_col] = df[label_col].replace(-1, 0)
    print("  Mapped labels: -1 -> 0 (legitimate), 1 -> 1 (phishing)")

# Separate features and labels
X = df.drop(label_col, axis=1)
y = df[label_col].astype(int)

print(f"  Label distribution: {dict(y.value_counts())}")
print(f"  Phishing ratio: {y.mean()*100:.1f}%")

# Handle missing/infinite values
X = X.fillna(0)
X = X.replace([np.inf, -np.inf], 0)

# Save feature names before any modification
feature_names = list(X.columns)

# Convert all to float32 to save memory
for col in X.columns:
    X[col] = pd.to_numeric(X[col], errors="coerce").fillna(0).astype("float32")

print(f"  Data prepared: {X.shape[0]:,} samples, {X.shape[1]} features")

# Free memory
del df
gc.collect()

print()

# =============================
# STEP 3: Train/Test Split
# =============================

print("[3/7] Splitting data (80% train, 20% test)...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"  Training set: {X_train.shape[0]:,} samples")
print(f"  Test set:     {X_test.shape[0]:,} samples")
print()

# =============================
# STEP 4: Train Models
# =============================

print("[4/7] Training models...")
print()

# --- Model 1: Random Forest ---
print("  [A] Training Random Forest (200 trees)...")
rf_model = RandomForestClassifier(
    n_estimators=200,
    max_depth=20,
    min_samples_split=5,
    min_samples_leaf=2,
    max_features="sqrt",
    random_state=42,
    n_jobs=-1,
    class_weight="balanced"
)
rf_model.fit(X_train, y_train)
rf_pred = rf_model.predict(X_test)
rf_acc = accuracy_score(y_test, rf_pred)
rf_f1 = f1_score(y_test, rf_pred)
print(f"      Accuracy: {rf_acc*100:.2f}%  |  F1: {rf_f1*100:.2f}%")
print()

# --- Model 2: Gradient Boosting ---
print("  [B] Training Gradient Boosting (150 trees)...")
gb_model = GradientBoostingClassifier(
    n_estimators=150,
    max_depth=8,
    learning_rate=0.1,
    min_samples_split=10,
    min_samples_leaf=5,
    subsample=0.8,
    random_state=42
)
gb_model.fit(X_train, y_train)
gb_pred = gb_model.predict(X_test)
gb_acc = accuracy_score(y_test, gb_pred)
gb_f1 = f1_score(y_test, gb_pred)
print(f"      Accuracy: {gb_acc*100:.2f}%  |  F1: {gb_f1*100:.2f}%")
print()

# --- Ensemble Model ---
print("  [C] Creating Ensemble (Soft Voting)...")
ensemble_model = VotingClassifier(
    estimators=[
        ("rf", rf_model),
        ("gb", gb_model)
    ],
    voting="soft",
    weights=[1.2, 1.0]
)
ensemble_model.fit(X_train, y_train)
ens_pred = ensemble_model.predict(X_test)
ens_acc = accuracy_score(y_test, ens_pred)
ens_f1 = f1_score(y_test, ens_pred)
print(f"      Accuracy: {ens_acc*100:.2f}%  |  F1: {ens_f1*100:.2f}%")
print()

# Pick best model
models_results = {
    "Random Forest": (rf_model, rf_acc, rf_f1, rf_pred),
    "Gradient Boosting": (gb_model, gb_acc, gb_f1, gb_pred),
    "Ensemble": (ensemble_model, ens_acc, ens_f1, ens_pred)
}

best_name = max(models_results, key=lambda k: models_results[k][2])  # sort by F1
best_model, best_acc, best_f1, best_pred = models_results[best_name]

print(f"  BEST MODEL: {best_name}")
print(f"  Accuracy: {best_acc*100:.2f}% | F1: {best_f1*100:.2f}%")
print()

# =============================
# STEP 5: Detailed Evaluation
# =============================

print("[5/7] Evaluating best model...")
print()

print("  Classification Report:")
print("  " + "-" * 55)
report = classification_report(y_test, best_pred, target_names=["Legitimate", "Phishing"])
for line in report.split("\n"):
    print(f"  {line}")
print()

cm = confusion_matrix(y_test, best_pred)
print("  Confusion Matrix:")
print(f"    True Negatives:  {cm[0][0]:,} (Legit correctly identified)")
print(f"    False Positives: {cm[0][1]:,} (Legit wrongly flagged)")
print(f"    False Negatives: {cm[1][0]:,} (Phishing missed)")
print(f"    True Positives:  {cm[1][1]:,} (Phishing caught)")
print()

prec = precision_score(y_test, best_pred)
rec = recall_score(y_test, best_pred)

# =============================
# STEP 6: Feature Importance
# =============================

print("[6/7] Top 20 features by importance...")
print()

if best_name in ("Random Forest", "Gradient Boosting"):
    importances = best_model.feature_importances_
else:
    importances = rf_model.feature_importances_

feature_imp = sorted(
    zip(feature_names, importances),
    key=lambda x: x[1],
    reverse=True
)

for i, (feat, imp) in enumerate(feature_imp[:20], 1):
    bar_len = int(imp * 200)
    bar = "█" * bar_len
    print(f"  {i:2d}. {feat:<35} {imp:.4f} {bar}")

top_features = [f[0] for f in feature_imp[:30]]
print()

# =============================
# STEP 7: Save Everything
# =============================

print("[7/7] Saving model artifacts...")

# 1. Save best model
model_path = "cybershield_advanced_model.pkl"
joblib.dump(best_model, model_path)
print(f"  Model saved: {model_path} ({os.path.getsize(model_path)/1024/1024:.1f} MB)")

# 2. Save feature names
feature_names_path = "model_feature_names.pkl"
joblib.dump(feature_names, feature_names_path)
print(f"  Feature names saved: {feature_names_path}")

# 3. Save metadata
metadata = {
    "model_type": best_name,
    "accuracy": round(best_acc * 100, 2),
    "precision": round(prec * 100, 2),
    "recall": round(rec * 100, 2),
    "f1_score": round(best_f1 * 100, 2),
    "n_features": len(feature_names),
    "n_training_samples": len(X_train),
    "n_test_samples": len(X_test),
    "feature_names": feature_names,
    "top_features": top_features,
    "all_models": {
        "Random Forest": {"accuracy": round(rf_acc*100,2), "f1": round(rf_f1*100,2)},
        "Gradient Boosting": {"accuracy": round(gb_acc*100,2), "f1": round(gb_f1*100,2)},
        "Ensemble": {"accuracy": round(ens_acc*100,2), "f1": round(ens_f1*100,2)},
    }
}
metadata_path = "model_metadata.pkl"
joblib.dump(metadata, metadata_path)
print(f"  Metadata saved: {metadata_path}")

print()
print("=" * 60)
print(f"  TRAINING COMPLETE!")
print(f"  Best Model: {best_name}")
print(f"  Accuracy:   {best_acc*100:.2f}%")
print(f"  Precision:  {prec*100:.2f}%")
print(f"  Recall:     {rec*100:.2f}%")
print(f"  F1-Score:   {best_f1*100:.2f}%")
print(f"  Model File: {model_path}")
print("=" * 60)
print()
print("  Now restart Flask: python app.py")
print()
