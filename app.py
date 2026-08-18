from flask import Flask


app = Flask(__name__)

app.secret_key = "student-performance-secret-key"


# ============================================================
# IMPORT ROUTES
# ============================================================

from routes.home_routes import home_bp
from routes.auth_routes import auth_bp
from routes.prediction_routes import prediction_bp
from routes.model_routes import model_bp


# ============================================================
# REGISTER ROUTES
# ============================================================

app.register_blueprint(home_bp)

app.register_blueprint(auth_bp)

app.register_blueprint(prediction_bp)

app.register_blueprint(model_bp)


# ============================================================
# RUN FLASK
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )