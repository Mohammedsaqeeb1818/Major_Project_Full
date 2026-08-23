from flask import Blueprint, render_template, session
import joblib

from utils.model_loader import best_model_name


model_bp = Blueprint(
    "model",
    __name__
)


# ============================================================
# MODEL ANALYSIS PAGE
# ============================================================

@model_bp.route("/models")
def models_page():

    model_results = joblib.load(
        "saved_models/model_results.pkl"
    )

    return render_template(
        "models.html",
        model_results=model_results,
        best_model_name=best_model_name
    )


# ============================================================
# MODEL COMPARISON PAGE
# ============================================================
@model_bp.route("/comparison")
def comparison_page():

    model_results = joblib.load(
        "saved_models/model_results.pkl"
    )

    all_predictions = session.get(
        "all_predictions",
        {}
    )

    return render_template(
        "comparsion.html",

        model_results=model_results,

        best_model_name=best_model_name,

        all_predictions=all_predictions
    )