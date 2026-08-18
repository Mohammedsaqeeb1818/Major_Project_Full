from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session
)

import pandas as pd
import joblib

from utils.model_loader import (
    model,
    scaler,
    imputer,
    label_encoder,
    FEATURE_COLUMNS,
    best_model_name
)

from utils.recommendations import (
    generate_recommendations
)


prediction_bp = Blueprint(
    "prediction",
    __name__
)

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

@prediction_bp.route("/predict-page")
def predict_page():

    if "user_id" not in session:

        return redirect(
            url_for("auth.login")
        )

    return render_template(
        "prediction.html"
    )


# ============================================================
# 6. PREDICTION
# ============================================================

@prediction_bp.route("/predict",methods=["POST"])
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

# ============================================================
# PREDICT USING ALL 5 MODELS
# ============================================================

        all_predictions = {}

        model_files = {

            "Decision Tree":
                "saved_models/decision_tree.pkl",

            "KNN":
                "saved_models/knn.pkl",

            "Logistic Regression":
                "saved_models/logistic_regression.pkl",

            "Random Forest":
                "saved_models/random_forest.pkl",

            "SVM":
                "saved_models/svm.pkl"
        }


        for model_name, model_path in model_files.items():

            current_model = joblib.load(model_path)

            if model_name in [
                "KNN",
                "Logistic Regression",
                "SVM"
            ]:

                input_scaled = scaler.transform(
                    input_imputed
                )

                encoded_prediction = current_model.predict(
                    input_scaled
                )

            else:

                encoded_prediction = current_model.predict(
                    input_imputed
                )

            current_prediction = label_encoder.inverse_transform(
                encoded_prediction
            )[0]

            all_predictions[model_name] = current_prediction

            recommendations = generate_recommendations(
            input_data,
            prediction
        )


    
        
    # ====================================================
    # DISPLAY RESULT
    # ====================================================

        return render_template(
        "prediction.html",

        prediction=prediction,

        model_name=best_model_name,

        recommendations=recommendations,

        all_predictions=all_predictions
)



      

    except Exception as e:

        return render_template(

            "prediction.html",

            error=f"Prediction Error: {str(e)}"
        )