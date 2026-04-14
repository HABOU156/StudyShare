import os
from werkzeug.utils import secure_filename
from app.repositories import file_repository
from flask import send_from_directory

# Dossiers de référence (priorité Backend/uploads)
BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROJECT_ROOT = os.path.abspath(os.path.join(BACKEND_ROOT, ".."))
UPLOAD_FOLDER = os.path.join(BACKEND_ROOT, "uploads")

def televerser_fichier(file, titre, type_fichier, cid):
    if not file or file.filename == '':
        return None, "Aucun fichier sélectionné"

    try:
        # 1. Sécuriser le nom du fichier
        filename = secure_filename(file.filename)
        
        # 2. Créer le chemin complet pour le disque dur
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # 3. Sauvegarder physiquement le fichier
        file.save(file_path)

        # 4. Préparer le chemin pour la DB (lien_access)
        db_path = f"uploads/{filename}"
        
        # 5. Appeler le repository avec les bons arguments : titre, lien_access, type, cid
        fid = file_repository.create_fichier(titre, db_path, type_fichier, cid)

        if fid:
            return fid, "Fichier téléversé et enregistré avec succès"
        return None, "Erreur lors de l'enregistrement en base de données"

    except Exception as e:
        return None, f"Erreur technique : {str(e)}"

def recuperer_fichier_physique(filename):
    # On pointe vers Backend/uploads
    directory = UPLOAD_FOLDER
    try:
        # On vérifie si le fichier existe avant d'envoyer
        return send_from_directory(directory, filename, as_attachment=True)
    except FileNotFoundError:
        return None

def chercher_fichiers(cid=None, type_fichier=None):
    return file_repository.rechercher_fichiers_db(cid, type_fichier)

def obtenir_liste_fichiers():
    from app.repositories import file_repository
    return file_repository.get_fichiers_avec_cours_et_note()


def obtenir_fichier_par_id(fid):
    from app.repositories import file_repository
    return file_repository.get_fichier_detail(fid)


def recuperer_fichier_par_fid(fid, as_attachment=True):
    """Envoie le fichier physique à partir du fid (chemin relatif enregistré en BD)."""
    from app.repositories import file_repository
    lien = file_repository.get_lien_access_par_fid(fid)
    if not lien:
        return None
    return recuperer_fichier_par_chemin_relatif(lien, as_attachment=as_attachment)


def recuperer_fichier_par_chemin_relatif(lien_access, as_attachment=True):
    if not lien_access:
        return None
    lien_access = lien_access.replace("\\", "/").lstrip("/")
    # Compatibilité: accepte chemins DB de type "uploads/x.pdf" et "Backend/uploads/x.pdf"
    candidates = [
        os.path.normpath(os.path.join(PROJECT_ROOT, lien_access)),
        os.path.normpath(os.path.join(BACKEND_ROOT, lien_access)),
    ]
    # Données SQL historiques: lien_access = "fichiers/xxx.pdf"
    # Fichiers réels présents dans Backend/uploads/xxx.pdf
    if lien_access.startswith("fichiers/"):
        candidates.insert(0, os.path.normpath(os.path.join(UPLOAD_FOLDER, os.path.basename(lien_access))))
    if lien_access.startswith("uploads/"):
        candidates.insert(0, os.path.normpath(os.path.join(BACKEND_ROOT, lien_access[len("uploads/"):])))
    if lien_access.startswith("Backend/uploads/"):
        candidates.insert(0, os.path.normpath(os.path.join(PROJECT_ROOT, lien_access)))

    for full in candidates:
        if not (full.startswith(PROJECT_ROOT) or full.startswith(BACKEND_ROOT)):
            continue
        if not os.path.isfile(full):
            continue
        directory = os.path.dirname(full)
        basename = os.path.basename(full)
        try:
            return send_from_directory(directory, basename, as_attachment=as_attachment)
        except FileNotFoundError:
            continue
    return None

# Dans app/services/file_service.py

def publier_avis(eid, fid, note, titre, commentaire):
    """
    Logique d'affaire : Validation et publication.
    """
    try:
        # Validation (Exigence 60) [cite: 60]
        if not (1 <= int(note) <= 5):
            return False, "La note doit être entre 1 et 5."

        # Appel au repository (On importe file_repository en haut du fichier)
        from app.repositories import file_repository
        success = file_repository.ajouter_review_et_commentaire(eid, fid, note, titre, commentaire)
        
        if success:
            return True, "Avis publié !"
        return False, "Échec de l'enregistrement."

    except Exception as e:
        # Exigence 56 : Attraper les cas d'erreurs inattendus [cite: 56]
        print(f"Erreur : {e}")
        return False, str(e)
    
def obtenir_details_avis(fid):
    """
    Logique d'affaire : Récupère les avis et la moyenne pour un document.
    """
    try:
        if not fid:
            return None, "ID du fichier manquant."

        # On récupère les deux types d'informations
        stats = file_repository.calculer_moyenne_avis(fid)
        liste_reviews = file_repository.obtenir_reviews_par_fichier(fid)

        # On formate la réponse
        data = {
            "moyenne": round(stats['moyenne'], 1) if stats['moyenne'] else 0,
            "total_avis": stats['nb_avis'],
            "reviews": liste_reviews
        }
        return data, "Succès"
    except Exception as e:
        print(f"Erreur service reviews : {e}")
        return None, str(e)
    
def filtrer_fichiers(cid, type_doc):
    """
    Logique d'affaire pour le filtrage.
    """
    try:
        # Liste des types autorisés selon ton ENUM SQL 
        types_valides = ['Cours', 'Résumé', 'Examen', 'Exercices']
        
        # Si un type est fourni mais qu'il n'est pas dans la liste, on le rejette
        if type_doc and type_doc not in types_valides:
            return None, "Type de document invalide."

        resultats = file_repository.rechercher_fichiers_filtres(cid, type_doc)
        return resultats, "Succès"
    except Exception as e:
        return None, str(e)