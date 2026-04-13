from app.repositories import user_repository, wallet_repository


#acess fichier 
def demander_acces_fichier(eid, fid):
    # Logique d'affaire : on vérifie la limite avant d'appeler le repo
    if not user_repository.peut_acceder_fichier(eid):
        return False, "Limite de 5 fichiers atteinte. Passez à Premium !"
    
    return user_repository.enregistrer_acces_fichier(eid, fid)


#inscription
def inscrire_etudiant(nom, courriel, password, uid_universite):
    # Logique d'affaire : On pourrait vérifier ici si le courriel finit par @ulaval.ca
    if not courriel or "@" not in courriel:
        return None, "Courriel invalide"
    
    user_id = user_repository.create_etudiant(nom, courriel, password, uid_universite)
    
    if user_id:
        return user_id, "Inscription réussie"
    return None, "Erreur lors de la création du compte"

from app.repositories import user_repository

def authentifier_etudiant(courriel, password):
    # On demande au repository de chercher l'utilisateur et de vérifier le hash
    user = user_repository.login_etudiant(courriel, password)
    print(f"DEBUG REPO OUTPUT: {user} | TYPE: {type(user)}")
    
    if user:
        # On peut ajouter ici une logique supplémentaire, 
        # comme mettre à jour la date de dernière connexion
        return user, "Connexion réussie"
    
    return None, "Courriel ou mot de passe incorrect"   

def acheter_premium(eid):
    # 1. Utilise le Wallet Repository pour l'argent
    wallet = wallet_repository.get_wallet_by_eid(eid)
    if not wallet:
        return False, "Portefeuille introuvable"

    solde = float(wallet['solde'])
    if solde < 20.0:
        return False, "Fonds insuffisants"

    # 2. Utilise le Wallet Repo pour déduire l'argent
    wallet_ok = wallet_repository.update_solde(eid, solde - 20.0)
    
    # 3. Utilise le User Repo pour changer le statut
    user_ok = user_repository.devenir_premium_db(eid)

    if wallet_ok and user_ok:
        return True, "Abonnement Premium activé !"
    return False, "Erreur lors de la transaction"

def deposer_argent(eid, montant):
    wallet = wallet_repository.get_wallet_by_eid(eid)
    if not wallet:
        return False, "Portefeuille introuvable"

    # On additionne l'ancien solde et le nouveau dépôt
    nouveau_solde = float(wallet['solde']) + float(montant)
    
    if wallet_repository.update_solde(eid, nouveau_solde):
        return True, f"Dépôt réussi. Nouveau solde : {nouveau_solde}$"
    return False, "Erreur technique lors de la mise à jour"

def obtenir_portefeuille(eid):
    # On va chercher dans le repository si le wallet existe
    wallet = user_repository.get_wallet_by_eid(eid)
    if wallet:
        return wallet, "Succès"
    return None, "Portefeuille introuvable"