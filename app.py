from flask import Flask, render_template, request
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)
import pandas as pd
import joblib
import os
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="mdsaqeeb123#",
        database="student_performance_db"
    )

# ============================================================
# 1. CREATE FLASK APPLICATION
# ============================================================

app = Flask(__name__)
app.secret_key = "student-performance-secret-key"



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
# GENERATE PERSONALIZED RECOMMENDATIONS
# ============================================================

def generate_recommendations(data, prediction):

    recommendations = []

    prediction_lower = str(prediction).lower()

    # --------------------------------------------------------
    # POOR
    # --------------------------------------------------------

    if prediction_lower == "poor":

        if data["attendance_percentage"] < 75:
            recommendations.append(
                "Improve attendance. Try to maintain at least 75% attendance."
            )

        if data["internal_marks"] < 25:
            recommendations.append(
                "Internal marks are low. Revise regularly and prepare well for examinations."
            )

        if data["assignment_marks"] < 25:
            recommendations.append(
                "Complete assignments on time and clarify difficult topics."
            )

        if data["study_hours_per_day"] < 2:
            recommendations.append(
                "Increase focused study time. Try to study for at least 2 hours every day."
            )

        if data["previous_sgpa"] < 6:
            recommendations.append(
                "Focus on subjects where you previously performed poorly."
            )

        if data["backlogs"] > 0:
            recommendations.append(
                "Prioritize clearing your backlogs."
            )

        if data["lab_performance"] < 50:
            recommendations.append(
                "Improve practical skills by regularly practicing laboratory programs."
            )

        if data["participation"] < 50:
            recommendations.append(
                "Participate more actively in classes and discussions."
            )

        if not recommendations:
            recommendations.append(
                "The model predicts poor performance. Maintain a consistent study schedule and monitor your progress."
            )

    # --------------------------------------------------------
    # AVERAGE
    # --------------------------------------------------------

    elif prediction_lower == "average":

        recommendations.append(
            "Your performance is average. Focus on improving your weakest areas."
        )

        if data["attendance_percentage"] < 75:
            recommendations.append(
                "Improve your attendance."
            )

        if data["study_hours_per_day"] < 3:
            recommendations.append(
                "Increase your daily focused study time."
            )

        if data["backlogs"] > 0:
            recommendations.append(
                "Work on clearing your backlogs."
            )

    # --------------------------------------------------------
    # GOOD
    # --------------------------------------------------------

    elif prediction_lower == "good":

        recommendations.append(
            "Good performance! Continue maintaining your current academic routine."
        )

        if data["attendance_percentage"] < 75:
            recommendations.append(
                "Try to improve your attendance."
            )

        if data["study_hours_per_day"] < 2:
            recommendations.append(
                "Consider increasing your daily study time."
            )

    # --------------------------------------------------------
    # EXCELLENT
    # --------------------------------------------------------

    elif prediction_lower == "excellent":

        recommendations.append(
            "Excellent performance! Continue maintaining your current study habits."
        )

        recommendations.append(
            "Keep your attendance, assignments, practical work and participation consistent."
        )

        if data["backlogs"] == 0:
            recommendations.append(
                "Excellent! You currently have no backlogs."
            )

    return recommendations




# ============================================================
# 5. HOME PAGE
# ============================================================



@app.route("/")
def home():
    return render_template(
        "index.html"
    )


#No one can access it
@app.route("/predict-page")
def predict_page():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("prediction.html")


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

@app.route("/models")
def models_page():
    model_results = joblib.load(
        "saved_models/model_results.pkl"
    )
    return render_template("models.html",
                           model_results=model_results,best_model_name=best_model_name )


#Login Page Routing
   
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        connection = None
        cursor = None

        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)

            query = """
                SELECT id, username, password
                FROM users
                WHERE username = %s
            """

            cursor.execute(query, (username,))

            user = cursor.fetchone()

            if user and check_password_hash(user["password"], password):

                session["user_id"] = user["id"]
                session["username"] = user["username"]

                return redirect(url_for("predict_page"))

            else:
                flash("Invalid username or password.")

        except mysql.connector.Error as error:

            print("MySQL Error:", error)

            flash("Database connection error.")

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()

    return render_template("login.html")




#Register Page Opening Route
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        hashed_password = generate_password_hash(password)

        connection = None
        cursor = None

        try:

            connection = get_db_connection()
            cursor = connection.cursor()

            query = """
                INSERT INTO users (username, email, password)
                VALUES (%s, %s, %s)
            """

            cursor.execute(
                query,
                (username, email, hashed_password)
            )

            connection.commit()

            flash("Account created successfully. Please login.")

            return redirect(url_for("login"))

        except mysql.connector.IntegrityError:

            flash("Username or email already exists.")

        except mysql.connector.Error as error:

            print("MySQL Error:", error)

            flash("Registration failed.")

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()

    return render_template("register.html")



#logout Option route 
@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))




# ============================================================
# 7. RUN FLASK APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )