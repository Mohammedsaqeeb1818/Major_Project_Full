from flask import Flask, render_template, request

import pandas as pd
import joblib
import os


# ============================================================
# 1. CREATE FLASK APPLICATION
# ============================================================

app = Flask(__name__)


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


print("\n========================================")
print("MODEL LOADED SUCCESSFULLY")
print("========================================")

print("Best Model:", best_model_name)

print("Features:")

for feature in FEATURE_COLUMNS:
    print("-", feature)

print("========================================")


# ============================================================
# 4. REAL-WORLD INPUT CONSTRAINTS
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
# 5. HOME PAGE
# ============================================================

@app.route("/")
def home():

    return render_template(
        "prediction.html"
    )


# ============================================================
# 6. PREDICTION
# ============================================================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        # ====================================================
        # GET VALUES FROM HTML FORM
        # ====================================================

        attendance = float(
            request.form.get(
                "attendance_percentage"
            )
        )

        internal = float(
            request.form.get(
                "internal_marks"
            )
        )

        assignment = float(
            request.form.get(
                "assignment_marks"
            )
        )

        study_hours = float(
            request.form.get(
                "study_hours_per_day"
            )
        )

        previous_sgpa = float(
            request.form.get(
                "previous_sgpa"
            )
        )

        backlogs = float(
            request.form.get(
                "backlogs"
            )
        )

        lab_performance = float(
            request.form.get(
                "lab_performance"
            )
        )

        participation = float(
            request.form.get(
                "participation"
            )
        )


        # ====================================================
        # CREATE INPUT DICTIONARY
        # ====================================================

        input_data = {

            "attendance_percentage":
                attendance,

            "internal_marks":
                internal,

            "assignment_marks":
                assignment,

            "study_hours_per_day":
                study_hours,

            "previous_sgpa":
                previous_sgpa,

            "backlogs":
                backlogs,

            "lab_performance":
                lab_performance,

            "participation":
                participation
        }


        # ====================================================
        # CHECK INPUT CONSTRAINTS
        # ====================================================

        constraint_errors = []


        for feature, value in input_data.items():

            minimum, maximum = CONSTRAINTS[
                feature
            ]

            if value < minimum or value > maximum:

                constraint_errors.append(
                    f"{feature.replace('_', ' ').title()} "
                    f"must be between {minimum} and {maximum}."
                )


        # ====================================================
        # IF CONSTRAINT ERROR
        # ====================================================

        if constraint_errors:

            return render_template(

                "prediction.html",

                error="Constraint Error",

                constraint_errors=constraint_errors
            )


        # ====================================================
        # CREATE DATAFRAME
        # ====================================================

        input_df = pd.DataFrame(
            [input_data]
        )


        # ====================================================
        # ENSURE CORRECT FEATURE ORDER
        # ====================================================

        input_df = input_df[
            FEATURE_COLUMNS
        ]


        # ====================================================
        # HANDLE MISSING VALUES
        # ====================================================

        input_imputed = imputer.transform(
            input_df
        )

        input_imputed = pd.DataFrame(
            input_imputed,
            columns=FEATURE_COLUMNS
        )


        # ====================================================
        # APPLY SAME PREPROCESSING USED DURING TRAINING
        # ====================================================

        if best_model_name in [

            "KNN",

            "Logistic Regression",

            "SVM"

        ]:

            input_scaled = scaler.transform(
                input_imputed
            )

            prediction_encoded = model.predict(
                input_scaled
            )

        else:

            prediction_encoded = model.predict(
                input_imputed
            )


        # ====================================================
        # CONVERT PREDICTION BACK TO ORIGINAL CLASS
        # ====================================================

        prediction = label_encoder.inverse_transform(
            prediction_encoded
        )[0]


        # ====================================================
        # DISPLAY RESULT
        # ====================================================

        return render_template(

            "prediction.html",

            prediction=prediction,

            model_name=best_model_name
        )


    except Exception as e:

        return render_template(

            "prediction.html",

            error=f"Prediction Error: {str(e)}"
        )


# ============================================================
# 7. RUN FLASK APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )