from flask import Blueprint, render_template
import joblib

from utils.model_loader import best_model_name


model_bp = Blueprint(
    "model",
    __name__
)


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