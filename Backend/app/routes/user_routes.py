from flask import Blueprint, request, jsonify, session
from app.services import user_service
from app.repositories import user_repository
from functools import wraps

# On utilise un Blueprint pour organiser les routes
user_bp = Blueprint('user_bp', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"status": "error", "message": "Accès interdit. Connectez-vous d'abord."}), 401
        return f(*args, **kwargs)
    return decorated_function


@user_bp.route('/api/universites', methods=['GET'])
def lister_universites():
    rows = user_repository.list_universites()
    return jsonify({"status": "success", "universites": rows}), 200


@user_bp.route('/api/acceder-fichier', methods=['POST'])
@login_required
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
        session['user_id'] = user['eid']  # On trace l'ID pour login_required
        session['is_premium'] = user['premium'] # On trace le statut pour le quota
        session.permanent = True # Optionnel: garde la session même si on ferme l'onglet
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
@login_required
def passer_premium():
    eid = session['user_id']

    succes, message = user_service.acheter_premium(eid)

    if succes:
        session['is_premium'] = 1  # Synchronise la session Flask
        return jsonify({"status": "success", "message": message}), 200
    return jsonify({"status": "error", "message": message}), 402

@user_bp.route('/api/se-desabonner', methods=['POST'])
@login_required
def se_desabonner():
    eid = session['user_id']
    succes, message = user_service.annuler_premium(eid)
    if succes:
        session['is_premium'] = 0
        return jsonify({"status": "success", "message": message}), 200
    return jsonify({"status": "error", "message": message}), 400

@user_bp.route('/api/mon-compte', methods=['GET'])
@login_required
def get_mon_compte():
    eid = session['user_id']
    user = user_repository.get_user_details(eid)
    if not user:
        return jsonify({"status": "error", "message": "Utilisateur introuvable."}), 404
    return jsonify({"status": "success", "user": user}), 200

@user_bp.route('/api/session-check', methods=['GET'])
def check_session():
    if 'user_id' in session:
        return jsonify({
            "logged_in": True, 
            "user_id": session['user_id'],
            "premium": session.get('is_premium', 0)
        }), 200
    return jsonify({"logged_in": False}), 200

@user_bp.route('/api/changer-mot-de-passe', methods=['POST'])
@login_required
def changer_mot_de_passe():
    eid = session['user_id']
    data = request.json or {}
    ancien = data.get('ancien_password', '')
    nouveau = data.get('nouveau_password', '')
    if not ancien or not nouveau:
        return jsonify({"status": "error", "message": "Données incomplètes."}), 400
    succes, message = user_service.changer_mot_de_passe(eid, ancien, nouveau)
    if succes:
        return jsonify({"status": "success", "message": message}), 200
    return jsonify({"status": "error", "message": message}), 400

@user_bp.route('/api/deconnexion', methods=['POST'])
def deconnexion():
    session.clear() # Efface toutes les données de session [cite: 51]
    return jsonify({"status": "success", "message": "Déconnecté avec succès"}), 200


