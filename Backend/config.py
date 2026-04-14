import mysql.connector

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin", 
            database="StudyShare"
        )
        return conn
    except Exception as e:
        print(f"Erreur : {e}")
        return None