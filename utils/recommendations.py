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