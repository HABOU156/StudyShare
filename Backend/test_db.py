from config import get_db_connection
import sys

def test():
    print("Tentative de connexion en cours...") # Ajoute ça pour voir si le script démarre
    try:
        db = get_db_connection()
        if db and db.is_connected():
            print("✅ Bravo Chedly ! La connexion à StudyShare est réussie.")
            cursor = db.cursor()
            cursor.execute("SELECT nom FROM Etudiants WHERE eid = 1")
            result = cursor.fetchone()
            if result:
                print(f"Test de lecture : L'étudiant trouvé est {result[0]}")
            db.close()
        else:
            print("❌ Connexion impossible. Vérifie config.py")
    except Exception as e:
        print(f"Une erreur est survenue : {e}")

if __name__ == "__main__":
    test()
    