from flask import Flask, jsonify
from flask.json.provider import DefaultJSONProvider
from app.routes.user_routes import user_bp 
from app.routes.wallet_routes import wallet_bp
from app.routes.file_routes import file_bp
import os
try:
    from app.routes.file_routes import file_bp
    print("✅ Blueprint Fichier chargé avec succès")
except ImportError as e:
    print(f"❌ Erreur d'importation : {e}")



# --- PATCH DE SÉCURITÉ POUR LES BYTES ---
class UpdatedJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.decode('utf-8')
        return super().default(obj)
# ----------------------------------------

app = Flask(__name__)
app.json = UpdatedJSONProvider(app) # On injecte le traducteur ici

@app.route('/')
def home():
    return jsonify({"message": "Bienvenue sur l'API StudyShare !"}), 200

# Indique à Flask où se trouve le dossier uploads
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Crée le dossier s'il n'existe pas encore au lancement
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Enregistrement des routes
app.register_blueprint(user_bp)
app.register_blueprint(wallet_bp)
app.register_blueprint(file_bp)

if __name__ == '__main__':
    # On lance le serveur sur le port 5000
    app.run(debug=True, port=5000)