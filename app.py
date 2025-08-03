from flask import Flask
from routes.formulario import formulario_bp

app = Flask(__name__)
app.secret_key = 'segredo'
app.config['UPLOAD_FOLDER'] = 'uploads'

app.register_blueprint(formulario_bp)

if __name__ == '__main__':
    app.run(debug=True)
