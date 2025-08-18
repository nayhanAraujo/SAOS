from flask import Flask
from routes.formulario import formulario_bp
from routes.api import api_bp
from routes.dashboard import dashboard_bp
from routes.auth import auth_bp
import os

app = Flask(__name__)
app.secret_key = 'segredo'
app.config['UPLOAD_FOLDER'] = 'uploads'

# Configurações adicionais
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['JSON_AS_ASCII'] = False  # Suporte a caracteres especiais no JSON

# Registra os blueprints
app.register_blueprint(formulario_bp)
app.register_blueprint(api_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(auth_bp)

# Cria diretórios necessários
os.makedirs('uploads', exist_ok=True)
os.makedirs('logs', exist_ok=True)

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')

