from flask import Blueprint, request, jsonify, session
from app.services import collection_service
from app.routes.user_routes import login_required

collection_bp = Blueprint('collection_bp', __name__)


@collection_bp.route('/api/collections', methods=['GET'])
@login_required
def lister_collections():
    eid = session['user_id']
    cols = collection_service.lister_collections(eid)
    return jsonify({"status": "success", "collections": cols}), 200


@collection_bp.route('/api/collections', methods=['POST'])
@login_required
def creer_collection():
    eid = session['user_id']
    data = request.json or {}
    nom = data.get('nom', '')
    col_id, message = collection_service.creer_collection(eid, nom)
    if col_id:
        return jsonify({"status": "success", "col_id": col_id, "message": message}), 201
    return jsonify({"status": "error", "message": message}), 400


@collection_bp.route('/api/collections/<int:col_id>', methods=['GET'])
@login_required
def detail_collection(col_id):
    eid = session['user_id']
    col, message = collection_service.obtenir_collection(col_id, eid)
    if col:
        return jsonify({"status": "success", "collection": col}), 200
    return jsonify({"status": "error", "message": message}), 404


@collection_bp.route('/api/collections/<int:col_id>/fichiers', methods=['POST'])
@login_required
def ajouter_fichier_collection(col_id):
    eid = session['user_id']
    data = request.json or {}
    fid = data.get('fid')
    if not fid:
        return jsonify({"status": "error", "message": "fid manquant."}), 400
    succes, message = collection_service.ajouter_fichier(col_id, int(fid), eid)
    if succes:
        return jsonify({"status": "success", "message": message}), 200
    return jsonify({"status": "error", "message": message}), 400
