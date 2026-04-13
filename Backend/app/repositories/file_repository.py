from config import get_db_connection

def create_fichier(titre, lien_access, type_fichier, cid):
    """
    titre : ignoré car absent de la DB actuelle
    lien_access : le chemin physique
    type_fichier : ENUM('Cours', 'Résumé', 'Examen', 'Exercices')
    cid : ID du cours
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # On ajoute 'mise_en_ligne' dans les colonnes et CURDATE() dans les values
        query = """
            INSERT INTO Fichiers (lien_access, type, cid, mise_en_ligne)
            VALUES (%s, %s, %s, CURDATE())
        """
        values = (lien_access, type_fichier, cid)
        
        cursor.execute(query, values)
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"❌ ERREUR SQL : {e}") # Regarde ton terminal pour voir ce message
        return None
    finally:
        conn.close()

def get_tous_les_fichiers():
    """Récupère la liste de tous les fichiers disponibles"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Fichiers")
        return cursor.fetchall()
    finally:
        conn.close()

def rechercher_fichiers_db(cid=None, type_fichier=None):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM Fichiers WHERE 1=1"
        params = []

        if cid:
            query += " AND cid = %s"
            params.append(cid)
        if type_fichier:
            query += " AND type = %s"
            params.append(type_fichier)

        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    finally:
        conn.close()