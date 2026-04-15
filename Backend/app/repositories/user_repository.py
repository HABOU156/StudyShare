from config import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash


def list_universites():
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT uid, nom FROM Universite ORDER BY nom")
        return cursor.fetchall()
    finally:
        conn.close()


def create_etudiant(nom, courriel, password, uid_universite):

    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        
        # hashage mdps
        hashed_password = generate_password_hash(password)
        
        query = """
            INSERT INTO Etudiants (nom, courriel, passwordHash, premium, uid)
            VALUES (%s, %s, %s, %s, %s)
        """
        values = (nom, courriel, hashed_password, 0, uid_universite)
        
        cursor.execute(query, values)
        conn.commit()
        
        user_id = cursor.lastrowid
        
        # creer wallet pr chaque etudiant
        cursor.execute("INSERT INTO Wallets (solde, eid) VALUES (%s, %s)", (0.00, user_id))
        conn.commit()
        
        return user_id
    except Exception as e:
        print(f"Erreur insertion : {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def peut_acceder_fichier(eid):
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # 1. On vérifie d'abord si l'étudiant est Premium
        cursor.execute("SELECT premium FROM Etudiants WHERE eid = %s", (eid,))
        user = cursor.fetchone()
        
        if user and user['premium'] == 1:
            return True # 
            
        
        cursor.execute("SELECT COUNT(*) as total FROM Acceder WHERE eid = %s", (eid,))
        count = cursor.fetchone()
        
        return count['total'] < 5 
    finally:
        conn.close()

def enregistrer_acces_fichier(eid, fid):
    conn = get_db_connection()
    if not conn:
        return False, "Erreur de connexion"
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        #  Vérifier si l'étudiant est premium (accès illimité)
        cursor.execute("SELECT premium FROM Etudiants WHERE eid = %s", (eid,))
        user = cursor.fetchone()
        is_premium = user['premium'] if user else 0

        
        cursor.execute("SELECT aid FROM Acceder WHERE eid = %s AND fid = %s", (eid, fid))
        deja_visite = cursor.fetchone()

        if not is_premium and not deja_visite:
            cursor.execute("SELECT COUNT(DISTINCT fid) as total FROM Acceder WHERE eid = %s", (eid,))
            count = cursor.fetchone()
            if count['total'] >= 5:
                return False, "Limite de 5 fichiers atteinte. Devenez Premium !"

        if not deja_visite:
            cursor.execute("SELECT lien_access FROM Fichiers WHERE fid = %s", (fid,))
            fichier = cursor.fetchone()
            nom = fichier['lien_access'] if fichier else "Fichier inconnu"

            query = """
                INSERT INTO Acceder (eid, fid, date_visite, nom_fichier) 
                VALUES (%s, %s, CURDATE(), %s)
            """
            cursor.execute(query, (eid, fid, nom))
            conn.commit()
            
        return True, "Accès accordé"

    except Exception as e:
        print(f"Erreur Acceder : {e}")
        return False, str(e)
    finally:
        conn.close()

#la focntion de conversion en bytes est implemente par l'IA pour resoudre un bug qu on a eu au debut  
def login_etudiant(courriel, password):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Etudiants WHERE courriel = %s", (courriel,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['passwordHash'], password):
            # FONCTION INTERNE : Convertit les bytes en string si nécessaire
            def force_str(obj):
                if isinstance(obj, bytes):
                    return obj.decode('utf-8')
                return obj

            clean_user = {
                "eid": user['eid'],
                "nom": force_str(user['nom']),
                "courriel": force_str(user['courriel']),
                "premium": user['premium'],
                "uid": user['uid']
            }
            return clean_user 
            
        return None
    finally:
        conn.close()

def devenir_premium_db(eid):
    """Change le statut de l'étudiant en Premium (1)"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE Etudiants SET premium = 1 WHERE eid = %s", (eid,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Erreur SQL Premium : {e}")
        return False
    finally:
        conn.close()

def get_wallet_by_eid(eid):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT wid, eid, CAST(solde AS FLOAT) as solde FROM Wallets WHERE eid = %s", (eid,))
        return cursor.fetchone()
    finally:
        conn.close()

def enregistrer_abonnement(eid, cout, duree_mois=6):
   
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO Abonnements (date_debut, date_fin, cout, eid)
            VALUES (CURDATE(), DATE_ADD(CURDATE(), INTERVAL %s MONTH), %s, %s)
        """
        cursor.execute(query, (duree_mois, cout, eid))
        conn.commit()
        return True
    except Exception as e:
        print(f" Erreur SQL Abonnements : {e}")
        return False
    finally:
        conn.close()

def get_user_by_id(eid):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT eid, premium FROM Etudiants WHERE eid = %s", (eid,))
        return cursor.fetchone()
    finally:
        conn.close()

def get_user_details(eid):
    """Retourne nom, courriel, université et statut premium de l'étudiant."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT e.eid, e.nom, e.courriel, e.premium, u.nom AS nom_universite
            FROM Etudiants e
            LEFT JOIN Universite u ON e.uid = u.uid
            WHERE e.eid = %s
            """,
            (eid,)
        )
        return cursor.fetchone()
    finally:
        conn.close()

def a_deja_accede(eid, fid):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT aid FROM Acceder WHERE eid = %s AND fid = %s",
            (eid, fid)
        )
        return cursor.fetchone() is not None
    finally:
        conn.close()

def annuler_premium_db(eid):
    """Remet le statut premium à 0."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE Etudiants SET premium = 0 WHERE eid = %s", (eid,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Erreur SQL annuler premium : {e}")
        return False
    finally:
        conn.close()

def compter_fichiers_uniques(eid):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT COUNT(DISTINCT fid) as total FROM Acceder WHERE eid = %s",
            (eid,)
        )
        row = cursor.fetchone()
        return row['total'] if row else 0
    finally:
        conn.close()

def changer_mot_de_passe(eid, ancien_password, nouveau_password):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT passwordHash FROM Etudiants WHERE eid = %s", (eid,))
        row = cursor.fetchone()
        if not row:
            return False, "Utilisateur introuvable."
        hash_actuel = row['passwordHash']
        if isinstance(hash_actuel, bytes):
            hash_actuel = hash_actuel.decode('utf-8')
        if not check_password_hash(hash_actuel, ancien_password):
            return False, "Mot de passe actuel incorrect."
        nouveau_hash = generate_password_hash(nouveau_password)
        cursor.execute(
            "UPDATE Etudiants SET passwordHash = %s WHERE eid = %s",
            (nouveau_hash, eid)
        )
        conn.commit()
        return True, "Mot de passe modifié avec succès."
    except Exception as e:
        print(f"Erreur changer_mot_de_passe : {e}")
        conn.rollback()
        return False, "Erreur technique lors du changement de mot de passe."
    finally:
        conn.close()