import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    roc_curve, auc, roc_auc_score
)
import joblib
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import label_binarize
import numpy as np

# --- Load datasets ---
students = pd.read_csv("students.csv")
jobs = pd.read_csv("jobs.csv")
resumes = pd.read_csv("resumes.csv")
applications = pd.read_csv("applications.csv")

# --- Merge ---
data = applications.merge(students, on="student_id", how="left")
data = data.merge(jobs, on="job_id", how="left")
data = data.merge(resumes, on="student_id", how="left")

# --- Safe get ---
def safe_get(col):
    return data[col].astype(str) if col in data.columns else pd.Series([""] * len(data))

# --- Combine text ---
data["combined_text"] = (
    safe_get("skills") + " " +
    safe_get("degree") + " " +
    safe_get("resume_text") + " " +
    safe_get("requirements")
)

# --- Target: Predict job title ---
if "title" not in data.columns:
    raise ValueError("❌ 'title' missing in jobs.csv — please ensure job data is correct.")

X = data["combined_text"]
y = data["title"]

# --- Split data ---
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# --- TF-IDF + KNN pipeline ---
model = Pipeline([
    ("tfidf", TfidfVectorizer(max_features=4000)),
    ("knn", KNeighborsClassifier(n_neighbors=5))
])

# --- Train model ---
print("🚀 Training Job-Type Recommendation Model...")
model.fit(X_train, y_train)

# --- Predictions ---
y_pred = model.predict(X_test)

# --- Evaluate ---
print("\n✅ Evaluation Results:")
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# --- Confusion Matrix ---
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(10, 6))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", 
            xticklabels=np.unique(y_test), yticklabels=np.unique(y_test))
plt.title("Confusion Matrix")
plt.xlabel("Predicted Label")
plt.ylabel("True Label")
plt.show()

# --- ROC Curve (multi-class handling) ---
y_bin = label_binarize(y_test, classes=np.unique(y))
y_pred_bin = label_binarize(y_pred, classes=np.unique(y))
n_classes = y_bin.shape[1]

fpr, tpr, roc_auc = {}, {}, {}
for i in range(n_classes):
    fpr[i], tpr[i], _ = roc_curve(y_bin[:, i], y_pred_bin[:, i])
    roc_auc[i] = auc(fpr[i], tpr[i])

plt.figure(figsize=(8, 6))
for i in range(n_classes):
    plt.plot(fpr[i], tpr[i], label=f'{np.unique(y)[i]} (AUC = {roc_auc[i]:.2f})')

plt.plot([0, 1], [0, 1], 'k--')
plt.title('ROC Curves for Job Type Prediction')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.legend()
plt.show()

# --- Save model ---
os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/job_recommendation_type_knn.pkl")
print("\n💾 Model saved as models/job_recommendation_type_knn.pkl")
