import shap


def generate_explanation(
    model,
    X,
    feature_names,
    background_data=None
):
    """
    Generate SHAP explanation for one student prediction.

    Parameters:
        model           : trained ML model
        X               : processed input of the student
        feature_names   : list of feature names
        background_data : reference data used by SHAP
    """

    # ====================================================
    # CREATE SHAP EXPLAINER
    # ====================================================

    if background_data is not None:

        explainer = shap.Explainer(
            model,
            background_data
        )

    else:

        explainer = shap.Explainer(
            model,
            X
        )


    # ====================================================
    # CALCULATE SHAP VALUES
    # ====================================================

    shap_result = explainer(X)

    values = shap_result.values[0]


    # ====================================================
    # HANDLE MULTICLASS OUTPUT
    # ====================================================

    if len(values.shape) > 1:

        predicted_class = model.predict(X)[0]

        values = values[:, predicted_class]


    # ====================================================
    # CREATE EXPLANATION
    # ====================================================

    explanation = []


    for i, feature in enumerate(feature_names):

        shap_value = float(
            values[i]
        )

        explanation.append({

            "feature": feature,

            "shap_value": shap_value,

            "importance": abs(shap_value)

        })

    # ====================================================
    # CONVERT SHAP IMPORTANCE TO PERCENTAGE
    # ====================================================

    total_importance = sum(
        item["importance"]
        for item in explanation
    )

    if total_importance > 0:

        for item in explanation:

            item["importance_percentage"] = (
                item["importance"] / total_importance
            ) * 100

    else:

        for item in explanation:

            item["importance_percentage"] = 0


    # ====================================================
    # SORT BY IMPORTANCE
    # ====================================================

    explanation.sort(
        key=lambda x: x["importance"],
        reverse=True
    )


    return explanation