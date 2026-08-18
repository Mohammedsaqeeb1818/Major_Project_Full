import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="mdsaqeeb123#",
        database="student_performance_db"
    )