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
    """
    Logique complexe : Portefeuille -> Statut Etudiant -> Table Abonnements.
    Respecte l'Exigence 8 : Validation de la logique d'affaire et gestion des erreurs[cite: 53, 56].
    """
    PRIX_ABONNEMENT = 20.0 

    try:
        wallet = wallet_repository.get_wallet_by_eid(eid)
        if not wallet:
            return False, "Portefeuille introuvable pour cet étudiant."

        solde = float(wallet['solde'])
        if solde < PRIX_ABONNEMENT:
            return False, f"Fonds insuffisants ({solde}$ / {PRIX_ABONNEMENT}$)."

        if not wallet_repository.update_solde(eid, solde - PRIX_ABONNEMENT):
            return False, "Erreur technique lors de la déduction du solde."

        if not user_repository.devenir_premium_db(eid):
            return False, "Paiement effectué, mais erreur lors de l'activation du statut."

        if not user_repository.enregistrer_abonnement(eid, PRIX_ABONNEMENT):
            return False, "Premium activé, mais erreur d'enregistrement dans l'historique."

        return True, "Abonnement Premium activé avec succès !"

    except Exception as e:
        print(f" Erreur critique achat premium : {e}")
        return False, "Une erreur technique est survenue sur le serveur."

def deposer_argent(eid, montant):
    wallet = wallet_repository.get_wallet_by_eid(eid)
    if not wallet:
        return False, "Portefeuille introuvable"

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

def annuler_premium(eid):
    succes = user_repository.annuler_premium_db(eid)
    if succes:
        return True, "Abonnement Premium annulé."
    return False, "Erreur lors de l'annulation."

def changer_mot_de_passe(eid, ancien_password, nouveau_password):
    if not nouveau_password or len(nouveau_password) < 8:
        return False, "Le nouveau mot de passe doit contenir au moins 8 caractères."
    return user_repository.changer_mot_de_passe(eid, ancien_password, nouveau_password)

def verifier_et_enregistrer_acces(eid, fid):
    try:
        user = user_repository.get_user_by_id(eid)
        if not user:
            return False, "Utilisateur introuvable."

        if user['premium'] == 1:
            return True, "Accès illimité Premium."

        if user_repository.a_deja_accede(eid, fid):
            return True, "Fichier déjà consulté."

        # Quota non-premium : max 5 fichiers distincts
        nb_fichiers = user_repository.compter_fichiers_uniques(eid)
        if nb_fichiers >= 5:
            return False, "Quota de 5 fichiers atteint. Passez à Premium !"

        # Tout est OK → enregistrement (le trigger SQL vérifie aussi côté DB)
        succes, message = user_repository.enregistrer_acces_fichier(eid, fid)
        return succes, message

    except Exception as e:
        return False, f"Erreur de vérification : {str(e)}"