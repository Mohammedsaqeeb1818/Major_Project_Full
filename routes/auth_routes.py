from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

import mysql.connector

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from utils.database import get_db_connection


auth_bp = Blueprint(
    "auth",
    __name__
)


#Login Page Routing
   
@auth_bp.route("/login", methods=["GET", "POST"])
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

                return redirect(
    url_for("prediction.predict_page")
)

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
@auth_bp.route("/register", methods=["GET", "POST"])
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

            return redirect(
    url_for("auth.login")
)

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
@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("auth.login")
    )
