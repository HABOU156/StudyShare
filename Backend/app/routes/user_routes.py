from flask import Blueprint, request, jsonify
from app.services import user_service

# On utilise un Blueprint pour organiser les routes
user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/api/acceder-fichier', methods=['POST'])
def acceder_fichier():
    data = request.json
    succes, message = user_service.demander_acces_fichier(data['eid'], data['fid'])
    
    if succes:
        return jsonify({"status": "ok", "message": message}), 200
    return jsonify({"status": "blocked", "message": message}), 403

@user_bp.route('/api/inscription', methods=['POST'])
def inscription():
    data = request.json
    
    # On délègue tout le travail au service
    user_id, message = user_service.inscrire_etudiant(
        data.get('nom'),
        data.get('courriel'),
        data.get('password'),
        data.get('uid_universite')
    )
    
    if user_id:
        return jsonify({"status": "success", "user_id": user_id, "message": message}), 201
    return jsonify({"status": "error", "message": message}), 400

#log in 
@user_bp.route('/api/connexion', methods=['POST'])
def connexion():
    data = request.json
    courriel = data.get('courriel')
    password = data.get('password')
    
    user, message = user_service.authentifier_etudiant(courriel, password)
    
    if user:
        return jsonify({
            "status": "success",
            "message": message,
            "user": user
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": message
        }), 401
    
@user_bp.route('/api/devenir-premium', methods=['POST'])
def passer_premium():
    data = request.json
    eid = data.get('eid')
    
    # Appelle la logique complexe du service (check solde + update statut)
    succes, message = user_service.acheter_premium(eid)
    
    if succes:
        return jsonify({"status": "success", "message": message}), 200
    return jsonify({"status": "error", "message": message}), 402 # 402 = Paiement requis