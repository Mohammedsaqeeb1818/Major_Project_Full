import joblib
import os

# ============================================================
# 2. MODEL FILE PATHS
# ============================================================

MODEL_FOLDER = "saved_models"


MODEL_PATH = os.path.join(
    MODEL_FOLDER,
    "best_model.pkl"
)

SCALER_PATH = os.path.join(
    MODEL_FOLDER,
    "scaler.pkl"
)

IMPUTER_PATH = os.path.join(
    MODEL_FOLDER,
    "imputer.pkl"
)

LABEL_ENCODER_PATH = os.path.join(
    MODEL_FOLDER,
    "label_encoder.pkl"
)

FEATURE_COLUMNS_PATH = os.path.join(
    MODEL_FOLDER,
    "feature_columns.pkl"
)

BEST_MODEL_NAME_PATH = os.path.join(
    MODEL_FOLDER,
    "best_model_name.pkl"
)


# ============================================================
# 3. LOAD TRAINED MODEL
# ============================================================

model = joblib.load(MODEL_PATH)

scaler = joblib.load(SCALER_PATH)

imputer = joblib.load(IMPUTER_PATH)

label_encoder = joblib.load(
    LABEL_ENCODER_PATH
)

FEATURE_COLUMNS = joblib.load(
    FEATURE_COLUMNS_PATH
)

best_model_name = joblib.load(
    BEST_MODEL_NAME_PATH
)