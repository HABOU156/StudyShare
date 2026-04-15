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
        print(f" ERREUR SQL : {e}") 
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


def get_fichiers_avec_cours_et_note():
    """Liste des fichiers avec sigle du cours et note moyenne"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT f.fid, f.lien_access, f.type, f.cid, f.mise_en_ligne, c.sigle AS sigle_cours,
                   COALESCE(
                       (SELECT ROUND(AVG(r.note)) FROM Reviews r WHERE r.fid = f.fid),
                       0
                   ) AS note_moyenne
            FROM Fichiers f
            LEFT JOIN Cours c ON f.cid = c.cid
            ORDER BY f.mise_en_ligne DESC
            """
        )
        return cursor.fetchall()
    finally:
        conn.close()


def get_fichier_detail(fid):
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT f.fid, f.lien_access, f.type, f.cid, f.mise_en_ligne, c.sigle AS sigle_cours,
                   COALESCE(
                       (SELECT ROUND(AVG(r.note)) FROM Reviews r WHERE r.fid = f.fid),
                       0
                   ) AS note_moyenne
            FROM Fichiers f
            LEFT JOIN Cours c ON f.cid = c.cid
            WHERE f.fid = %s
            """,
            (fid,),
        )
        return cursor.fetchone()
    finally:
        conn.close()


def get_lien_access_par_fid(fid):
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT lien_access FROM Fichiers WHERE fid = %s", (fid,))
        row = cursor.fetchone()
        return row["lien_access"] if row else None
    finally:
        conn.close()


def get_all_cours():
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT cid, sigle FROM Cours ORDER BY sigle")
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

def ajouter_review_et_commentaire(eid, fid, note, titre, commentaire):
    """
    Insère une note dans Reviews et le texte dans Comments.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        

        query_review = """
            INSERT INTO Reviews (eid, fid, date_de_mise_enligne, note)
            VALUES (%s, %s, CURDATE(), %s)
        """
        cursor.execute(query_review, (eid, fid, note))
        rid = cursor.lastrowid # On récupère l'ID de la review pour le commentaire
        

        query_comment = """
            INSERT INTO Comments (rid, titre, commentaire)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query_comment, (rid, titre, commentaire))
        
        conn.commit()
        return True
    except Exception as e:
        print(f" Erreur SQL Review : {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def obtenir_reviews_par_fichier(fid):

    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        # Jointure pour récupérer la note et le texte du commentaire associé
        query = """
            SELECT R.note, R.date_de_mise_enligne, C.titre, C.commentaire, E.nom
            FROM Reviews R
            JOIN Comments C ON R.rid = C.rid
            JOIN Etudiants E ON R.eid = E.eid
            WHERE R.fid = %s
            ORDER BY R.date_de_mise_enligne DESC
        """
        cursor.execute(query, (fid,))
        return cursor.fetchall()
    finally:
        conn.close()

def calculer_moyenne_avis(fid):
    """
    Calcule la moyenne des notes pour un fichier spécifique.
    Exigence 4 : Utilisation d'agrégations (AVG)[cite: 39].
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT AVG(note) as moyenne, COUNT(*) as nb_avis FROM Reviews WHERE fid = %s"
        cursor.execute(query, (fid,))
        return cursor.fetchone()
    finally:
        conn.close()

def rechercher_fichiers_filtres(cid=None, type_doc=None):
    """
    Recherche des fichiers avec filtres optionnels.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT F.*, C.sigle 
            FROM Fichiers F
            JOIN Cours C ON F.cid = C.cid
            WHERE 1=1
        """
        params = []

        if cid:
            query += " AND F.cid = %s"
            params.append(cid)
        
        if type_doc:
            # On filtre par le type ENUM (Cours, Résumé, Examen, Exercices)
            query += " AND F.type = %s"
            params.append(type_doc)

        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    finally:
        conn.close()