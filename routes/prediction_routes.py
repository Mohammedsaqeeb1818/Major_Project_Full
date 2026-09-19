from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    Response,
    stream_with_context,
    jsonify
)

import pandas as pd
import joblib
import numpy as np

from utils.database import get_db_connection

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

from utils.explainable_ai import (
    generate_explanation
)

from services.qwen_service import stream_qwen

import json


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
             # Data actually given to the model
            xai_input = input_scaled

        else:

            prediction_encoded = model.predict(
                input_imputed
            )
             # Data actually given to the model
            xai_input = input_imputed


        # ====================================================
        # CONVERT PREDICTION BACK TO ORIGINAL CLASS
        # ====================================================

        prediction = label_encoder.inverse_transform(
            prediction_encoded
        )[0]

        # ============================================================
        # SAVE PREDICTION HISTORY
        # ============================================================

        connection = None
        cursor = None

        try:

            connection = get_db_connection()

            cursor = connection.cursor()

            query = """
        INSERT INTO prediction_history
        (
            user_id,
            previous_sgpa,
            attendance_percentage,
            backlogs,
            prediction
        )
        VALUES (%s, %s, %s, %s, %s)
    """

            cursor.execute(
                query,
                (
                    session["user_id"],
                    previous_sgpa,
                    attendance,
                    int(backlogs),
                    prediction
                )
            )

            connection.commit()

        except Exception as db_error:

            print(
                "Prediction history save error:",
                db_error
            )

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()


       




        # ====================================================
        # LOAD BACKGROUND DATA FOR SHAP
        # ====================================================

        background_df = pd.read_csv(
            "data/student_performance_project_100k.csv"
        )

        # Keep only the features used by the model
        background_df = background_df[
            FEATURE_COLUMNS
        ]

        # Use a small representative sample
        background_df = background_df.sample(
            n=100,
            random_state=42
        )

        # ====================================================
        # PREPROCESS BACKGROUND DATA
        # ====================================================

        background_imputed = imputer.transform(
            background_df
        )

        background_imputed = pd.DataFrame(
            background_imputed,
            columns=FEATURE_COLUMNS
        )


        # ====================================================
        # SCALE BACKGROUND DATA IF REQUIRED
        # ====================================================

        if best_model_name in [
            "KNN",
            "Logistic Regression",
            "SVM"
        ]:

            background_xai = scaler.transform(
                background_imputed
            )

        else:

            background_xai = background_imputed

    # ====================================================
    # GENERATE EXPLAINABLE AI EXPLANATION
    # ====================================================

        explanation = generate_explanation(
            model,
            xai_input,
            FEATURE_COLUMNS,
            background_xai
        )

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

            # Load current model
            current_model = joblib.load(
                model_path
            )

            # ========================================================
            # PREPARE INPUT FOR CURRENT MODEL
            # ========================================================

            if model_name in [
                "KNN",
                "Logistic Regression",
                "SVM"
            ]:

                current_input = scaler.transform(
                    input_imputed
                )

            else:

                current_input = input_imputed

            # ========================================================
            # MAKE PREDICTION
            # ========================================================

            encoded_prediction = current_model.predict(
                current_input
            )

            # Convert encoded prediction to original class
            current_prediction = label_encoder.inverse_transform(
                encoded_prediction
            )[0]

            # Store prediction
            all_predictions[
                model_name
            ] = current_prediction

        # ====================================================
        # STORE CURRENT STUDENT MODEL PREDICTIONS
        # ====================================================

        session["all_predictions"] = all_predictions





# ====================================================
# GENERATE RECOMMENDATIONS
# ====================================================

        recommendations = generate_recommendations(
            input_data,
            prediction
        )


    # ====================================================
    # GENERATE QWEN AI EXPLANATION
    # ====================================================

        print("1. Prediction started")

        # After ML prediction
        print("2. ML prediction completed")

        # After SHAP explanation
        print("3. SHAP explanation completed")

        # Before Qwen
        print("4. Sending request to Qwen")

      
        print("5. Qwen response received")





    
        
    # ====================================================
    # DISPLAY RESULT
    # ====================================================

        return render_template(
    "xai.html",
    prediction=prediction,
    model_name=best_model_name,
    recommendations=recommendations,
    all_predictions=all_predictions,
    explanation=explanation,
    input_data=input_data
)


      

    except Exception as e:

        return render_template(

            "prediction.html",

            error=f"Prediction Error: {str(e)}"
        )


@prediction_bp.route("/ai-stream", methods=["POST"])
def ai_stream():
    try:
        data = request.get_json()

        prediction = data.get("prediction")
        input_data = data.get("input_data")
        explanation = data.get("explanation")
        recommendations = data.get("recommendations")

        prompt = f"""
You are an AI student performance advisor.

Prediction: {prediction}
Student Data: {input_data}
SHAP Explanation: {explanation}
Recommendations: {recommendations}

Explain the student's performance in simple language.
Give practical improvement suggestions.
Keep the response concise.
"""

        @stream_with_context
        def generate():
            for chunk in stream_qwen(prompt):
                yield chunk

        return Response(
            generate(),
            content_type="text/plain; charset=utf-8"
        )

    except Exception as e:
        print("AI Stream Error:", e)

        return jsonify({
            "error": "Unable to generate AI explanation."
        }), 500


@prediction_bp.route("/study-planner")
def study_planner_page():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    return render_template("study_planner.html")



@prediction_bp.route("/generate-study-plan", methods=["POST"])
def generate_study_plan():
    if "user_id" not in session:
        return {"error": "Please login first"}, 401

    try:
        data = request.get_json()

        difficult_subject = data.get("difficult_subject")
        study_goal = data.get("study_goal")
        available_hours = data.get("available_hours")

        if not difficult_subject or not study_goal or not available_hours:
            return {"error": "Please fill all fields"}, 400

        prompt = f"""
You are an AI study planner for college students.

Subject: {difficult_subject}
Goal: {study_goal}
Available Hours Per Day: {available_hours}

Create a short and practical DAILY STUDY TIMETABLE.

Use this exact format:

### Daily Timetable
- Session 1: Concept Learning - 40% of time
- Session 2: Practice Questions - 40% of time
- Session 3: Revision - 20% of time

### Important Topics
- List exactly 4 important topics.

### Daily Tasks
- Give exactly 3 tasks.

### Revision Tips
- Give exactly 2 tips.

Rules:
- Maximum 180 words.
- Use the available hours per day.
- Keep the plan practical for college students.
- Avoid repetition.
- Do not create a multi-week plan.
- Complete every section.
"""

        ai_plan = stream_qwen(prompt)

        return {
            "subject": difficult_subject,
            "goal": study_goal,
            "hours": available_hours,
            "plan": str(ai_plan)
        }

    except Exception as e:
        print("Study Planner Error:", e)
        return {"error": str(e)}, 500



#============================================================
# PREDICTION HISTORY
#============================================================

@prediction_bp.route("/prediction-history")
def prediction_history():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                id,
                previous_sgpa,
                attendance_percentage,
                backlogs,
                prediction,
                created_at
            FROM prediction_history
            WHERE user_id = %s
            ORDER BY created_at DESC
        """

        cursor.execute(query, (session["user_id"],))
        history = cursor.fetchall()

        return render_template(
            "prediction_history.html",
            history=history
        )

    except Exception as e:
        print("Prediction History Error:", e)
        return "Error loading prediction history", 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()