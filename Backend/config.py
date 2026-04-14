import mysql.connector

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Iron2020", 
            database="StudyShare"
        )
        return conn
    except Exception as e:
        print(f"Erreur : {e}")
        return None