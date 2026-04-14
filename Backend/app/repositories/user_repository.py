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
        
        # EXIGENCE SÉCURITÉ : Chiffrage du mot de passe (Hashage)
        hashed_password = generate_password_hash(password)
        
        query = """
            INSERT INTO Etudiants (nom, courriel, passwordHash, premium, uid)
            VALUES (%s, %s, %s, %s, %s)
        """
        # Par défaut, premium est à 0 (faux)
        values = (nom, courriel, hashed_password, 0, uid_universite)
        
        cursor.execute(query, values)
        conn.commit()
        
        user_id = cursor.lastrowid
        
        # EXIGENCE PROJET : Créer automatiquement un Wallet pour l'étudiant
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
            return True # Les premiums ont un accès illimité
            
        # 2. Sinon, on compte combien de fichiers il a déjà consultés
        cursor.execute("SELECT COUNT(*) as total FROM Acceder WHERE eid = %s", (eid,))
        count = cursor.fetchone()
        
        return count['total'] < 5 # Retourne True s'il en a moins de 5
    finally:
        conn.close()

def enregistrer_acces_fichier(eid, fid):
    conn = get_db_connection()
    if not conn:
        return False, "Erreur de connexion"
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # 1. Vérifier si l'étudiant est premium (accès illimité)
        cursor.execute("SELECT premium FROM Etudiants WHERE eid = %s", (eid,))
        user = cursor.fetchone()
        is_premium = user['premium'] if user else 0

        # 2. Vérifier si c'est une première visite pour ce fichier
        # (Si déjà visité, on autorise sans décompter du quota)
        cursor.execute("SELECT aid FROM Acceder WHERE eid = %s AND fid = %s", (eid, fid))
        deja_visite = cursor.fetchone()

        if not is_premium and not deja_visite:
            # 3. Vérifier le quota (Max 5 fichiers différents)
            cursor.execute("SELECT COUNT(DISTINCT fid) as total FROM Acceder WHERE eid = %s", (eid,))
            count = cursor.fetchone()
            if count['total'] >= 5:
                return False, "Limite de 5 fichiers atteinte. Devenez Premium !"

        # 4. Si accès autorisé et nouvelle visite, on enregistre
        if not deja_visite:
            # Récupérer le nom du fichier pour l'historique
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

            # On crée le dictionnaire en forçant la conversion de chaque champ
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
    """
    Enregistre la trace de l'abonnement dans la table Abonnements.
    Exigence 3 : Cohérence avec la modélisation.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Calcule les dates (6 mois par défaut comme dans ton SQL)
        query = """
            INSERT INTO Abonnements (date_debut, date_fin, cout, eid)
            VALUES (CURDATE(), DATE_ADD(CURDATE(), INTERVAL %s MONTH), %s, %s)
        """
        cursor.execute(query, (duree_mois, cout, eid))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Erreur SQL Abonnements : {e}")
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