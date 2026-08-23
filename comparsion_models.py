import pandas as pd
import joblib
import os



from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer

from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.svm import SVC
from sklearn.calibration import CalibratedClassifierCV


from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)


# ============================================================
# 1. CONFIGURATION
# ============================================================

DATA_FILE = "data/student_performance_project_100k.csv"

TARGET_COLUMN = "performance"

FEATURE_COLUMNS = [
    "attendance_percentage",
    "internal_marks",
    "assignment_marks",
    "study_hours_per_day",
    "previous_sgpa",
    "backlogs",
    "lab_performance",
    "participation"
]


# ============================================================
# 2. REAL-WORLD INPUT CONSTRAINTS
# ============================================================

CONSTRAINTS = {

    "attendance_percentage": (0, 100),

    "internal_marks": (0, 50),

    "assignment_marks": (0, 50),

    "study_hours_per_day": (0, 16),

    "previous_sgpa": (0, 10),

    "backlogs": (0, 10),

    "lab_performance": (0, 100),

    "participation": (0, 100)
}


# ============================================================
# 3. LOAD DATASET
# ============================================================

print("\nLoading dataset...")

df = pd.read_csv(DATA_FILE)

print("Dataset loaded successfully.")
print("Dataset shape:", df.shape)


# ============================================================
# 4. CHECK REQUIRED COLUMNS
# ============================================================

required_columns = FEATURE_COLUMNS + [TARGET_COLUMN]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    raise ValueError(
        "\nERROR: Missing columns in dataset:\n"
        + "\n".join(missing_columns)
    )


# ============================================================
# 5. SELECT FEATURES AND TARGET
# ============================================================

X = df[FEATURE_COLUMNS].copy()

y = df[TARGET_COLUMN].copy()


# ============================================================
# 6. CONVERT FEATURES TO NUMERIC
# ============================================================

for column in FEATURE_COLUMNS:

    X[column] = pd.to_numeric(
        X[column],
        errors="coerce"
    )


# ============================================================
# 7. HANDLE MISSING VALUES
# ============================================================

imputer = SimpleImputer(
    strategy="median"
)

X = pd.DataFrame(
    imputer.fit_transform(X),
    columns=FEATURE_COLUMNS
)


# ============================================================
# 8. ENCODE TARGET
# ============================================================

label_encoder = LabelEncoder()

y_encoded = label_encoder.fit_transform(y)


print("\nPerformance classes:")

for number, label in enumerate(label_encoder.classes_):

    print(
        number,
        "->",
        label
    )


# ============================================================
# 9. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y_encoded,

    test_size=0.20,

    random_state=42,

    stratify=y_encoded
)


print("\n========================================")
print("DATA SPLIT")
print("========================================")

print(
    "Training samples:",
    len(X_train)
)

print(
    "Testing samples :",
    len(X_test)
)


# ============================================================
# 10. FEATURE SCALING
# ============================================================

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(
    X_train
)

X_test_scaled = scaler.transform(
    X_test
)


# ============================================================
# 11. CREATE MODELS
# ============================================================

models = {

    "Decision Tree":
        DecisionTreeClassifier(
            random_state=42
        ),

    "KNN":
        KNeighborsClassifier(
            n_neighbors=5
        ),

    "Logistic Regression":
        LogisticRegression(
            max_iter=2000,
            random_state=42
        ),

    "Random Forest":
        RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            n_jobs=-1
        ),

    "SVM":
        CalibratedClassifierCV(
            SVC(
                kernel="rbf",
                C=1.0,
                gamma="scale",
                random_state=42
                ),
        ensemble=False
    )
}


# ============================================================
# 12. TRAIN AND COMPARE ALL MODELS
# ============================================================

results = {}

trained_models = {}

print("\n")
print("=" * 90)
print("                    MODEL COMPARISON")
print("=" * 90)

print(
    f"{'Model':<25}"
    f"{'Accuracy':<15}"
    f"{'Precision':<15}"
    f"{'Recall':<15}"
    f"{'F1 Score':<15}"
)

print("-" * 90)


for model_name, model in models.items():

    print(
        f"Training {model_name}..."
    )

    # --------------------------------------------------------
    # Models requiring scaling
    # --------------------------------------------------------

    if model_name in [
        "KNN",
        "Logistic Regression",
        "SVM"
    ]:

        model.fit(
            X_train_scaled,
            y_train
        )

        y_pred = model.predict(
            X_test_scaled
        )

    # --------------------------------------------------------
    # Tree-based models
    # --------------------------------------------------------

    else:

        model.fit(
            X_train,
            y_train
        )

        y_pred = model.predict(
            X_test
        )


    # --------------------------------------------------------
    # Evaluation
    # --------------------------------------------------------

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    precision = precision_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        average="weighted",
        zero_division=0
    )


    results[model_name] = {

        "accuracy": accuracy,

        "precision": precision,

        "recall": recall,

        "f1": f1
    }


    trained_models[model_name] = model


    print(
        f"{model_name:<25}"
        f"{accuracy * 100:<15.2f}"
        f"{precision:<15.4f}"
        f"{recall:<15.4f}"
        f"{f1:<15.4f}"
    )


# ============================================================
# 13. AUTOMATICALLY SELECT BEST MODEL
# ============================================================

best_model_name = max(

    results,

    key=lambda name: (
        results[name]["f1"],
        results[name]["accuracy"]
    )
)


best_model = trained_models[
    best_model_name
]

best_result = results[
    best_model_name
]


# ============================================================
# 13A. CONFIDENCE SCORE
# ============================================================

# Select the correct test data
# Scaled data is used for KNN, Logistic Regression and SVM.
# Original data is used for Decision Tree and Random Forest.

if best_model_name in [
    "KNN",
    "Logistic Regression",
    "SVM"
]:

    confidence_X_test = X_test_scaled

else:

    confidence_X_test = X_test


# Get probability for each performance class
probabilities = best_model.predict_proba(
    confidence_X_test
)


# Highest probability is the confidence
confidence_scores = probabilities.max(
    axis=1
)


# Convert to percentage
confidence_percentage = (
    confidence_scores * 100
)


print("\n========================================")
print("CONFIDENCE SCORE")
print("========================================")

print(
    f"Average Confidence : "
    f"{confidence_percentage.mean():.2f}%"
)

print(
    f"Minimum Confidence : "
    f"{confidence_percentage.min():.2f}%"
)

print(
    f"Maximum Confidence : "
    f"{confidence_percentage.max():.2f}%"
)



# ============================================================
# 14. DISPLAY BEST MODEL
# ============================================================

print("-" * 90)

print("\n🏆 BEST MODEL SELECTED")

print("----------------------------------------")

print(
    "Model     :",
    best_model_name
)

print(
    "Accuracy  :",
    round(
        best_result["accuracy"] * 100,
        2
    ),
    "%"
)

print(
    "Precision :",
    round(
        best_result["precision"],
        4
    )
)

print(
    "Recall    :",
    round(
        best_result["recall"],
        4
    )
)

print(
    "F1 Score  :",
    round(
        best_result["f1"],
        4
    )
)

print("----------------------------------------")


# ============================================================
# 15. CLASSIFICATION REPORT
# ============================================================

if best_model_name in [
    "KNN",
    "Logistic Regression",
    "SVM"
]:

    best_predictions = best_model.predict(
        X_test_scaled
    )

else:

    best_predictions = best_model.predict(
        X_test
    )


# ============================================================
# 15A. SAMPLE PREDICTIONS WITH CONFIDENCE
# ============================================================

print("\nSample Predictions with Confidence:")

for i in range(10):

    predicted_label = label_encoder.inverse_transform(
        [best_predictions[i]]
    )[0]

    print(
        f"Student {i + 1}: "
        f"Prediction = {predicted_label}, "
        f"Confidence = "
        f"{confidence_percentage[i]:.2f}%"
    )


print("\n")
print("=" * 90)
print("              BEST MODEL CLASSIFICATION REPORT")
print("=" * 90)

print(
    classification_report(
        y_test,
        best_predictions,
        target_names=label_encoder.classes_,
        zero_division=0
    )
)


# ============================================================
# 16. SAVE TRAINED MODEL AND PREPROCESSING OBJECTS
# ============================================================

print("\n")
print("=" * 90)
print("              SAVING MODEL FILES")
print("=" * 90)


# Create folder if it doesn't exist

os.makedirs(
    "saved_models",
    exist_ok=True
)


# ------------------------------------------------------------
# SAVE ALL TRAINED MODELS
# ------------------------------------------------------------

for model_name, trained_model in trained_models.items():

    safe_name = model_name.lower().replace(" ", "_")

    joblib.dump(
        trained_model,
        f"saved_models/{safe_name}.pkl"
    )


# ------------------------------------------------------------
# SAVE BEST MODEL
# ------------------------------------------------------------

joblib.dump(
    best_model,
    "saved_models/best_model.pkl"
)


# ------------------------------------------------------------
# SAVE SCALER
# ------------------------------------------------------------

joblib.dump(
    scaler,
    "saved_models/scaler.pkl"
)


# ------------------------------------------------------------
# SAVE IMPUTER
# ------------------------------------------------------------

joblib.dump(
    imputer,
    "saved_models/imputer.pkl"
)


# ------------------------------------------------------------
# SAVE LABEL ENCODER
# ------------------------------------------------------------

joblib.dump(
    label_encoder,
    "saved_models/label_encoder.pkl"
)


# ------------------------------------------------------------
# SAVE FEATURE COLUMNS
# ------------------------------------------------------------

joblib.dump(
    FEATURE_COLUMNS,
    "saved_models/feature_columns.pkl"
)


# ------------------------------------------------------------
# SAVE BEST MODEL NAME
# ------------------------------------------------------------

joblib.dump(
    best_model_name,
    "saved_models/best_model_name.pkl"
)


# ------------------------------------------------------------
# SAVE MODEL RESULTS
# ------------------------------------------------------------

joblib.dump(
    results,
    "saved_models/model_results.pkl"
)


print("\nModel files saved successfully!")

print("\nBest Model:")
print(best_model_name)

print("\nSaved files:")

print("1. best_model.pkl")
print("2. scaler.pkl")
print("3. imputer.pkl")
print("4. label_encoder.pkl")
print("5. feature_columns.pkl")
print("6. best_model_name.pkl")
print("7. model_results.pkl")

print("\n" + "=" * 90)
