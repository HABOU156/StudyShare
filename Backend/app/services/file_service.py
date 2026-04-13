import os
from werkzeug.utils import secure_filename
from app.repositories import file_repository
from flask import send_from_directory

# Dossier où les fichiers sont sauvés
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

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
    # On pointe vers ton dossier uploads
    directory = os.path.join(os.getcwd(), 'uploads')
    try:
        # On vérifie si le fichier existe avant d'envoyer
        return send_from_directory(directory, filename, as_attachment=True)
    except FileNotFoundError:
        return None

def chercher_fichiers(cid=None, type_fichier=None):
    return file_repository.rechercher_fichiers_db(cid, type_fichier)

def obtenir_liste_fichiers():
    from app.repositories import file_repository
    return file_repository.get_tous_les_fichiers()