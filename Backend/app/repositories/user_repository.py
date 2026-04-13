from config import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

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
        return False, "Erreur de connexion base de données"
    
    try:
        if not peut_acceder_fichier(eid):
            return False, "Limite de 5 fichiers atteinte. Passez à Premium !"
            
        cursor = conn.cursor()
        # On vérifie si l'étudiant n'a pas déjà accédé à CE fichier précis
        cursor.execute("SELECT * FROM Acceder WHERE eid = %s AND fid = %s", (eid, fid))
        if cursor.fetchone():
            return True, "Fichier déjà consulté (accès autorisé)"

        # Sinon, on insère le nouvel accès
        cursor.execute("INSERT INTO Acceder (eid, fid) VALUES (%s, %s)", (eid, fid))
        conn.commit()
        return True, "Accès autorisé et enregistré"
    except Exception as e:
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
        # Note : Dans ton script SQL, wid semble correspondre à l'eid
        query = "SELECT * FROM Wallets WHERE wid = %s"
        cursor.execute(query, (eid,))
        return cursor.fetchone()
    finally:
        conn.close()