from flask import Blueprint, render_template, request, redirect, flash, current_app, session
from werkzeug.utils import secure_filename
import os
from utils.email_sender import enviar_email
from database.connection import db_connection
from routes.auth import login_required
from datetime import datetime

formulario_bp = Blueprint('formulario', __name__)

@formulario_bp.route('/', methods=['GET', 'POST'])
@login_required
def formulario():
    if request.method == 'POST':
        try:
            # Verifica se usuário está logado
            if not session.get('logado'):
                flash('Por favor, faça login para continuar.', 'error')
                return redirect('/login')
            
            # Dados do formulário
            sistema = request.form['sistema']
            tipo = request.form['tipo']
            descricao = request.form['descricao']

            # Dados do usuário logado
            usuario_id = session['usuario_id']
            usuario_tipo = session['usuario_tipo']
            
            # Busca dados do usuário no banco
            with db_connection() as con:
                cur = con.cursor()
                cur.execute("""
                    SELECT NOME, EMAIL, TELEFONE, CPF_CNPJ 
                    FROM USUARIOS 
                    WHERE ID = ?
                """, (usuario_id,))
                usuario = cur.fetchone()
                
                if not usuario:
                    flash('Usuário não encontrado.', 'error')
                    return redirect('/')
                
                nome, email, telefone, cpf_cnpj = usuario
                
                # Busca categoria baseada no tipo
                cur.execute("""
                    SELECT ID FROM CATEGORIAS 
                    WHERE NOME = ? AND ATIVO = TRUE
                """, (tipo,))
                categoria_result = cur.fetchone()
                
                if not categoria_result:
                    # Se não encontrar, usa categoria padrão ou cria uma
                    cur.execute("""
                        SELECT ID FROM CATEGORIAS 
                        WHERE NOME = 'Outro' AND ATIVO = TRUE
                    """)
                    categoria_result = cur.fetchone()
                    if not categoria_result:
                        # Cria categoria "Outro" se não existir
                        cur.execute("""
                            INSERT INTO CATEGORIAS (NOME, DESCRICAO, COR, ICONE, ATIVO)
                            VALUES ('Outro', ?, '#6B7280', 'fas fa-question', TRUE)
                        """, ('Outros tipos de solicitação'.encode('utf-8'),))
                        con.commit()
                        # Busca o ID da categoria recém-criada
                        cur.execute("""
                            SELECT ID FROM CATEGORIAS 
                            WHERE NOME = 'Outro' 
                            ORDER BY DTHR_CRIACAO DESC
                        """)
                        categoria_id = cur.fetchone()[0]
                    else:
                        categoria_id = categoria_result[0]
                else:
                    categoria_id = categoria_result[0]
                
                # Define prioridade padrão (média)
                prioridade_id = 2  # Média
                
                # Define status inicial
                status_id = 1  # Aberto
                
                # Gera código de referência
                data_atual = datetime.now()
                codigo = f"OS{data_atual.strftime('%Y%m%d')}"
                
                # Busca o próximo número sequencial
                cur.execute("""
                    SELECT COUNT(*) FROM SOLICITACOES 
                    WHERE CODIGO_REFERENCIA LIKE ?
                """, (f"{codigo}%",))
                count = cur.fetchone()[0]
                codigo_referencia = f"{codigo}{str(count + 1).zfill(4)}"
                
                # Calcula prazos baseado na prioridade
                cur.execute("SELECT PRAZO_HORAS FROM PRIORIDADES WHERE ID = ?", (prioridade_id,))
                prazo_result = cur.fetchone()
                prazo_horas = prazo_result[0] if prazo_result else 72
                
                # Calcula prazo de resolução (data atual + horas)
                from datetime import timedelta
                prazo_resolucao = datetime.now() + timedelta(hours=prazo_horas)
                
                # Upload de arquivo
                arquivo = request.files.get('arquivo')
                caminho_arquivo = None
                nome_arquivo = None
                
                if arquivo and arquivo.filename:
                    try:
                        nome_arquivo = secure_filename(arquivo.filename)
                        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
                        os.makedirs(upload_folder, exist_ok=True)
                        caminho_arquivo = os.path.join(upload_folder, nome_arquivo)
                        arquivo.save(caminho_arquivo)
                    except Exception as upload_error:
                        print(f"Erro no upload: {upload_error}")
                        # Continua sem o arquivo se houver erro
                        caminho_arquivo = None
                        nome_arquivo = None
                
                # Insere na nova estrutura da tabela SOLICITACOES
                # Para campos BLOB, precisamos converter string para bytes
                cur.execute("""
                    INSERT INTO SOLICITACOES (
                        CODIGO_REFERENCIA, TITULO, DESCRICAO, ID_CLIENTE, ID_CATEGORIA, 
                        ID_PRIORIDADE, ID_STATUS, SISTEMA, PRAZO_RESOLUCAO, 
                        DTHR_CRIACAO, DTHR_ATUALIZACAO
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (
                    codigo_referencia, tipo, descricao.encode('utf-8'), usuario_id, categoria_id,
                    prioridade_id, status_id, sistema, prazo_resolucao
                ))
                
                # Para Firebird, precisamos buscar o ID da solicitação recém-criada
                cur.execute("""
                    SELECT ID FROM SOLICITACOES 
                    WHERE CODIGO_REFERENCIA = ? 
                    ORDER BY DTHR_CRIACAO DESC
                """, (codigo_referencia,))
                solicitacao_id = cur.fetchone()[0]
                
                # Registra no histórico
                cur.execute("""
                    INSERT INTO HISTORICO (
                        ID_SOLICITACAO, ID_USUARIO, TIPO_ACAO, DESCRICAO, DTHR_ACAO
                    ) VALUES (?, ?, 'CRIACAO', ?, CURRENT_TIMESTAMP)
                """, (solicitacao_id, usuario_id, 'Solicitação criada pelo cliente'.encode('utf-8')))
                
                # Se há arquivo, registra como anexo
                if caminho_arquivo and nome_arquivo:
                    try:
                        cur.execute("""
                            INSERT INTO ANEXOS (
                                ID_SOLICITACAO, ID_USUARIO, NOME_ORIGINAL, NOME_ARQUIVO, CAMINHO_ARQUIVO, TIPO_MIME, 
                                TAMANHO_BYTES, DTHR_UPLOAD
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                        """, (
                            solicitacao_id, usuario_id, arquivo.filename, nome_arquivo, caminho_arquivo, 
                            arquivo.content_type, os.path.getsize(caminho_arquivo)
                        ))
                    except Exception as anexo_error:
                        print(f"Erro ao registrar anexo: {anexo_error}")
                        # Continua sem registrar o anexo
                
                con.commit()

                # Envia email de confirmação
                try:
                    enviar_email_confirmacao(codigo_referencia, nome, email, tipo, descricao, sistema)
                except Exception as email_error:
                    print(f"Erro ao enviar email: {email_error}")
                    # Continua mesmo se o email falhar
                
                # Redireciona para página de confirmação com os dados
                return render_template('confirmacao.html', 
                                     codigo_referencia=codigo_referencia,
                                     data_criacao=data_atual.strftime('%d/%m/%Y %H:%M'),
                                     sistema=sistema,
                                     tipo=tipo)
                
        except Exception as e:
            flash(f'Ocorreu um erro ao processar a solicitação: {str(e)}', 'error')
            return redirect('/')

    return render_template('form.html')

@formulario_bp.route('/confirmacao')
@login_required
def confirmacao():
    """Página de confirmação de solicitação enviada"""
    # Esta rota pode ser usada para mostrar confirmações de solicitações anteriores
    return render_template('confirmacao.html',
                         codigo_referencia="N/A",
                         data_criacao="N/A",
                         sistema="N/A",
                         tipo="N/A")

def enviar_email_confirmacao(codigo, nome, email, tipo, descricao, sistema):
    """Envia email de confirmação de abertura"""
    try:
        # Usa o serviço de email moderno se disponível
        from utils.email_service import EmailService
        email_service = EmailService()
        
        # Busca a solicitação criada
        with db_connection() as con:
            cur = con.cursor()
            cur.execute("""
                SELECT s.ID, s.CODIGO_REFERENCIA, s.TITULO, s.DESCRICAO, 
                       c.NOME as CATEGORIA, p.NOME as PRIORIDADE, s.PRAZO_RESOLUCAO
                FROM SOLICITACOES s
                JOIN CATEGORIAS c ON s.ID_CATEGORIA = c.ID
                JOIN PRIORIDADES p ON s.ID_PRIORIDADE = p.ID
                WHERE s.CODIGO_REFERENCIA = ?
            """, (codigo,))
            
            solicitacao = cur.fetchone()
            if solicitacao:
                # Envia email usando o template
                email_service.enviar_confirmacao_abertura(solicitacao[0])
            else:
                # Fallback para email simples
                enviar_email_simples(codigo, nome, email, tipo, descricao, sistema)
                
    except Exception as e:
        print(f"Erro no email moderno: {e}")
        # Fallback para email simples
        try:
            enviar_email_simples(codigo, nome, email, tipo, descricao, sistema)
        except Exception as e2:
            print(f"Erro no email simples: {e2}")
            # Se ambos falharem, apenas loga o erro

def enviar_email_simples(codigo, nome, email, tipo, descricao, sistema):
    """Envia email simples como fallback"""
    try:
        from utils.email_sender import enviar_email
        enviar_email(sistema, tipo, nome, "", email, descricao, None)
    except Exception as e:
        print(f"Erro ao enviar email simples: {e}")
        # Se falhar, apenas loga o erro mas não interrompe o fluxo
