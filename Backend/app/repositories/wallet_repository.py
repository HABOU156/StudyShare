from config import get_db_connection

def get_wallet_by_eid(eid):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Wallets WHERE eid = %s", (eid,))
        return cursor.fetchone()
    finally:
        conn.close()

def update_solde(eid, nouveau_montant):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE Wallets SET solde = %s WHERE eid = %s", (nouveau_montant, eid))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erreur SQL Wallet: {e}")
        return False
    finally:
        conn.close()