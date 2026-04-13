from config import get_db_connection

def create_fichier(titre, lien_access, type_fichier, cid):
    """
    titre : sera stocké dans lien_access ou une autre colonne si tu en ajoutes une
    lien_access : le chemin vers le fichier (ex: uploads/devoir.pdf)
    type_fichier : DOIT être 'Cours', 'Résumé', 'Examen' ou 'Exercices'
    cid : l'ID du cours existant dans ta table Cours
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # On respecte tes colonnes : lien_access, type, cid
        query = """
            INSERT INTO Fichiers (lien_access, type, cid)
            VALUES (%s, %s, %s)
        """
        # Note : Ta table n'a pas de colonne 'titre', 
        # donc on insère le chemin et le type pour l'instant.
        values = (lien_access, type_fichier, cid)
        
        cursor.execute(query, values)
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"❌ ERREUR SQL : {e}")
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