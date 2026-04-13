from flask import Blueprint, request, jsonify
from app.services import user_service

wallet_bp = Blueprint('wallet_bp', __name__)

# Route pour CONSULTER le solde (Ex: GET /api/wallet/3)
@wallet_bp.route('/api/wallet/<int:eid>', methods=['GET'])
def voir_wallet(eid):
    wallet, message = user_service.obtenir_portefeuille(eid)
    if wallet:
        return jsonify({"status": "success", "wallet": wallet}), 200
    return jsonify({"status": "error", "message": message}), 404

# Route pour DÉPOSER de l'argent (Ex: POST /api/wallet/depot)
@wallet_bp.route('/api/wallet/depot', methods=['POST'])
def ajouter_fonds():
    data = request.json
    eid = data.get('eid')
    montant = data.get('montant')

    if not eid or montant is None or montant <= 0:
        return jsonify({"status": "error", "message": "Données invalides"}), 400

    succes, message = user_service.deposer_argent(eid, montant)
    
    if succes:
        return jsonify({"status": "success", "message": message}), 200
    return jsonify({"status": "error", "message": message}), 500