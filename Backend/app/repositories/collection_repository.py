from config import get_db_connection


def creer_collection(eid, nom):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Collections (nom, date_creation, eid) VALUES (%s, CURDATE(), %s)",
            (nom, eid)
        )
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Erreur creer_collection : {e}")
        conn.rollback()
        return None
    finally:
        conn.close()


def lister_collections(eid):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.col_id, c.nom, c.date_creation,
                   COUNT(cf.fid) AS nb_fichiers
            FROM Collections c
            LEFT JOIN CollectionFichiers cf ON c.col_id = cf.col_id
            WHERE c.eid = %s
            GROUP BY c.col_id
            ORDER BY c.date_creation DESC
        """, (eid,))
        return cursor.fetchall()
    finally:
        conn.close()


def get_collection(col_id, eid):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT col_id, nom, date_creation FROM Collections WHERE col_id = %s AND eid = %s",
            (col_id, eid)
        )
        col = cursor.fetchone()
        if not col:
            return None
        cursor.execute("""
            SELECT f.fid, f.lien_access, f.type, co.sigle AS sigle_cours
            FROM CollectionFichiers cf
            JOIN Fichiers f ON cf.fid = f.fid
            LEFT JOIN Cours co ON f.cid = co.cid
            WHERE cf.col_id = %s
        """, (col_id,))
        col['fichiers'] = cursor.fetchall()
        return col
    finally:
        conn.close()


def ajouter_fichier(col_id, fid, eid):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT col_id FROM Collections WHERE col_id = %s AND eid = %s",
            (col_id, eid)
        )
        if not cursor.fetchone():
            return False, "Collection introuvable ou accès refusé."
        cursor.execute(
            "SELECT 1 FROM CollectionFichiers WHERE col_id = %s AND fid = %s",
            (col_id, fid)
        )
        if cursor.fetchone():
            return False, "Ce fichier est déjà dans la collection."
        cursor.execute(
            "INSERT INTO CollectionFichiers (col_id, fid) VALUES (%s, %s)",
            (col_id, fid)
        )
        conn.commit()
        return True, "Fichier ajouté à la collection."
    except Exception as e:
        print(f"Erreur ajouter_fichier : {e}")
        conn.rollback()
        return False, "Erreur technique."
    finally:
        conn.close()
