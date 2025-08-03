from flask import Blueprint, render_template, request, redirect, flash, current_app
from werkzeug.utils import secure_filename
import os
from utils.email_sender import enviar_email
from database.connection import db_connection

formulario_bp = Blueprint('formulario', __name__)

@formulario_bp.route('/', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        try:
            sistema = request.form['sistema']
            tipo = request.form['tipo']
            nome = request.form['nome']
            telefone = request.form['telefone']
            email = request.form['email']
            descricao = request.form['descricao']

            arquivo = request.files.get('arquivo')
            caminho_arquivo = None
            if arquivo:
                nome_arquivo = secure_filename(arquivo.filename)
                upload_folder = current_app.config['UPLOAD_FOLDER']
                os.makedirs(upload_folder, exist_ok=True)
                caminho_arquivo = os.path.join(upload_folder, nome_arquivo)
                arquivo.save(caminho_arquivo)

            with db_connection() as con:
                cur = con.cursor()
                cur.execute("""INSERT INTO SOLICITACOES
                    (SISTEMA, TIPO_SOLICITACAO, NOME_SOLICITANTE, TELEFONE, EMAIL, DESCRICAO, CAMINHO_ANEXO)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (sistema, tipo, nome, telefone, email, descricao, caminho_arquivo)
                )
                con.commit()

            enviar_email(sistema, tipo, nome, telefone, email, descricao, caminho_arquivo)
            flash('Solicitação enviada com sucesso!')
            return redirect('/')
        except Exception as e:
            flash(f'Ocorreu um erro ao processar a solicitação: {str(e)}')
            return redirect('/')

    return render_template('form.html')
