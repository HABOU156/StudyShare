from flask import Blueprint, request, jsonify
from app.services import file_service

file_bp = Blueprint('file_bp', __name__)

@file_bp.route('/api/fichiers/upload', methods=['POST'])
def upload_fichier():
    # 1. Vérifie 'lien_access' car c'est le nom dans ton Postman
    if 'lien_access' not in request.files:
        return jsonify({"status": "error", "message": "Aucun fichier envoyé"}), 400
    
    fichier = request.files['lien_access']
    
    # 2. Récupère 'type' et 'cid' (noms de ton Postman)
    type_fichier = request.form.get('type')
    cid = request.form.get('cid')
    titre = request.form.get('titre') # Facultatif si pas dans la DB

    if not type_fichier or not cid:
        return jsonify({"status": "error", "message": "Métadonnées (type ou cid) manquantes"}), 400

    # 3. Appelle le service
    fid, message = file_service.televerser_fichier(fichier, titre, type_fichier, cid)
    
    if fid:
        return jsonify({"status": "success", "message": message, "fid": fid}), 201
    
    return jsonify({"status": "error", "message": message}), 500
@file_bp.route('/api/fichiers', methods=['GET'])
def lister_fichiers():
    # Route simple pour voir tous les fichiers disponibles
    fichiers = file_service.obtenir_liste_fichiers()
    return jsonify({"status": "success", "fichiers": fichiers}), 200


@file_bp.route('/api/fichiers/<int:fid>', methods=['GET'])
def detail_fichier(fid):
    row = file_service.obtenir_fichier_par_id(fid)
    if not row:
        return jsonify({"status": "error", "message": "Fichier introuvable"}), 404
    return jsonify({"status": "success", "fichier": row}), 200


@file_bp.route('/api/cours', methods=['GET'])
def lister_cours():
    from app.repositories import file_repository
    cours = file_repository.get_all_cours()
    return jsonify({"status": "success", "cours": cours}), 200

@file_bp.route('/api/fichiers/download/<filename>', methods=['GET'])
def download_fichier(filename):
    response = file_service.recuperer_fichier_physique(filename)
    if response:
        return response
    return jsonify({"status": "error", "message": "Fichier introuvable sur le serveur"}), 404


@file_bp.route('/api/fichiers/<int:fid>/download', methods=['GET'])
def download_fichier_par_fid(fid):
    response = file_service.recuperer_fichier_par_fid(fid)
    if response:
        return response
    return jsonify({"status": "error", "message": "Fichier introuvable sur le serveur"}), 404



@file_bp.route('/api/fichiers/<int:fid>/preview', methods=['GET'])
def preview_fichier_par_fid(fid):
    response = file_service.recuperer_fichier_par_fid(fid, as_attachment=False)
    if response:
        return response
    return jsonify({"status": "error", "message": "Fichier introuvable sur le serveur"}), 404

@file_bp.route('/api/fichiers/recherche', methods=['GET'])
def rechercher_fichiers():
    # On récupère les paramètres de l'URL (ex: ?cid=1&type=Cours)
    cid = request.args.get('cid')
    type_fichier = request.args.get('type')

    resultats = file_service.chercher_fichiers(cid, type_fichier)
    
    return jsonify({
        "status": "success",
        "count": len(resultats),
        "fichiers": resultats
    }), 200

@file_bp.route('/api/fichiers/review', methods=['POST'])
def poster_review():
    data = request.json
    
    # 1. Extraction des données
    eid = data.get('eid')
    fid = data.get('fid')
    note = data.get('note')
    titre = data.get('titre')
    commentaire = data.get('commentaire')

    # 2. Vérification des champs obligatoires (Exigence 60)
    # On s'assure qu'aucune donnée n'est manquante avant de contacter le service
    if not all([eid, fid, note, titre, commentaire]):
        return jsonify({"status": "error", "message": "Données incomplètes (eid, fid, note, titre ou commentaire manquant)."}), 400

    # 3. Appel unique au service (Exigence 55 : minimiser les communications)
    success, message = file_service.publier_avis(eid, fid, note, titre, commentaire)
    
    if success:
        return jsonify({"status": "success", "message": message}), 201
    
    return jsonify({"status": "error", "message": message}), 500