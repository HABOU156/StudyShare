from flask import Flask, send_from_directory, abort
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
from app.routes.user_routes import user_bp
from app.routes.wallet_routes import wallet_bp
from app.routes.file_routes import file_bp
import os
import socket

from werkzeug.utils import safe_join



# --- PATCH DE SÉCURITÉ POUR LES BYTES ---
class UpdatedJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.decode('utf-8')
        return super().default(obj)
# ----------------------------------------

app = Flask(__name__)
app.json = UpdatedJSONProvider(app) # On injecte le traducteur ici
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type"]}})

# Dossier racine du dépôt (parent de Backend/) — pages HTML, css/, js/
FRONTEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Indique à Flask où se trouve le dossier uploads
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Crée le dossier s'il n'existe pas encore au lancement
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Enregistrement des routes API (doit rester avant les routes « catch-all » du site)
app.register_blueprint(user_bp)
app.register_blueprint(wallet_bp)
app.register_blueprint(file_bp)


@app.route('/')
def home():
    """Page d’accueil du site (ouvre la même URL que l’API)."""
    return send_from_directory(FRONTEND_ROOT, 'index.html')


@app.route('/<path:path>')
def frontend_ou_fichiers_statiques(path):
    """
    Sert fichiers.html, css/styles.css, js/api.js, etc.
    Les routes /api/* sont gérées par les blueprints (priorité plus élevée).
    """
    try:
        full = safe_join(FRONTEND_ROOT, path)
        if full is None or not os.path.isfile(full):
            abort(404)
        directory, name = os.path.split(full)
        return send_from_directory(directory, name)
    except (OSError, ValueError):
        abort(404)


def _premier_port_libre(debut=5050, fin=5150):
    """Trouve un port TCP libre (évite 5000 AirPlay, 5001 souvent déjà utilisé)."""
    for p in range(debut, fin):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(('0.0.0.0', p))
            except OSError:
                continue
            return p
    raise SystemExit(
        'Aucun port libre entre %s et %s. Libérez un port ou faites : PORT=8000 python3 main.py'
        % (debut, fin - 1)
    )


if __name__ == '__main__':
    # PORT=8080 python3 main.py  → force un port précis
    # sinon → premier libre à partir de 5050 (affiche l’URL exacte)
    if os.environ.get('PORT'):
        port = int(os.environ['PORT'])
    else:
        port = _premier_port_libre()
        print('→ StudyShare API : http://127.0.0.1:%s' % port)
        print('  Si le site HTML ne joint pas l’API, ajoutez dans la page :')
        print("  <script>window.STUDYSHARE_API_BASE='http://127.0.0.1:%s';</script>" % port)
    app.run(debug=True, port=port)