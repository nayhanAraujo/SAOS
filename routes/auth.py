from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database.connection import db_connection
import re
import hashlib

auth_bp = Blueprint('auth', __name__)

def validar_cpf(cpf):
    """Valida CPF"""
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False
    
    # Validação do primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    if int(cpf[9]) != digito1:
        return False
    
    # Validação do segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    if int(cpf[10]) != digito2:
        return False
    
    return True

def validar_cnpj(cnpj):
    """Valida CNPJ"""
    # Remove caracteres não numéricos
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    
    if len(cnpj) != 14:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cnpj == cnpj[0] * 14:
        return False
    
    # Validação do primeiro dígito verificador
    multiplicadores1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * multiplicadores1[i] for i in range(12))
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    if int(cnpj[12]) != digito1:
        return False
    
    # Validação do segundo dígito verificador
    multiplicadores2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * multiplicadores2[i] for i in range(13))
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    if int(cnpj[13]) != digito2:
        return False
    
    return True

def hash_senha(senha):
    """Gera hash da senha"""
    return hashlib.sha256(senha.encode()).hexdigest()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        tipo_usuario = request.form.get('tipo_usuario')
        identificacao = request.form.get('identificacao', '').strip()
        senha = request.form.get('senha', '').strip()
        
        print(f"🔍 [LOGIN] Tentativa de login:")
        print(f"   Tipo: {tipo_usuario}")
        print(f"   Identificação: {identificacao}")
        print(f"   Senha: {'*' * len(senha)}")
        
        if not identificacao or not senha:
            print("❌ [LOGIN] Campos vazios")
            flash('Por favor, preencha todos os campos.', 'error')
            return render_template('login.html')
        
        try:
            with db_connection() as con:
                cur = con.cursor()
                
                if tipo_usuario == 'cliente':
                    print("👤 [LOGIN] Processando login de CLIENTE")
                    # Valida CPF ou CNPJ
                    cpf_cnpj_limpo = re.sub(r'[^0-9]', '', identificacao)
                    
                    if len(cpf_cnpj_limpo) == 11:
                        if not validar_cpf(identificacao):
                            print("❌ [LOGIN] CPF inválido")
                            flash('CPF inválido.', 'error')
                            return render_template('login.html')
                    elif len(cpf_cnpj_limpo) == 14:
                        if not validar_cnpj(identificacao):
                            print("❌ [LOGIN] CNPJ inválido")
                            flash('CNPJ inválido.', 'error')
                            return render_template('login.html')
                    else:
                        print("❌ [LOGIN] CPF/CNPJ com tamanho incorreto")
                        flash('CPF deve ter 11 dígitos ou CNPJ deve ter 14 dígitos.', 'error')
                        return render_template('login.html')
                    
                    # Busca cliente por CPF/CNPJ
                    query = """
                        SELECT ID, NOME, EMAIL, TIPO_USUARIO, ATIVO 
                        FROM USUARIOS 
                        WHERE CPF_CNPJ = ? AND TIPO_USUARIO = 'CLIENTE'
                    """
                    print(f"🔍 [LOGIN] Executando query: {query}")
                    print(f"🔍 [LOGIN] Parâmetros: {identificacao}")
                    
                else:  # técnico
                    print("👨‍💻 [LOGIN] Processando login de TÉCNICO")
                    # Valida email
                    email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
                    if not re.match(email_regex, identificacao):
                        print("❌ [LOGIN] Email inválido")
                        flash('E-mail inválido.', 'error')
                        return render_template('login.html')
                    
                    # Busca técnico por email
                    query = """
                        SELECT ID, NOME, EMAIL, TIPO_USUARIO, ATIVO 
                        FROM USUARIOS 
                        WHERE EMAIL = ? AND TIPO_USUARIO IN ('TECNICO', 'ADMIN')
                    """
                    print(f"🔍 [LOGIN] Executando query: {query}")
                    print(f"🔍 [LOGIN] Parâmetros: {identificacao}")
                
                cur.execute(query, (identificacao,))
                usuario = cur.fetchone()
                
                if not usuario:
                    print("❌ [LOGIN] Usuário não encontrado no banco")
                    flash('Usuário não encontrado.', 'error')
                    return render_template('login.html')
                
                usuario_id, nome, email, tipo_usuario, ativo = usuario
                print(f"✅ [LOGIN] Usuário encontrado:")
                print(f"   ID: {usuario_id}")
                print(f"   Nome: {nome}")
                print(f"   Email: {email}")
                print(f"   Tipo: {tipo_usuario}")
                print(f"   Ativo: {ativo}")
                
                if not ativo:
                    print("❌ [LOGIN] Usuário inativo")
                    flash('Usuário inativo. Entre em contato com o administrador.', 'error')
                    return render_template('login.html')
                
                # Verifica senha
                print("🔐 [LOGIN] Verificando senha...")
                cur.execute("""
                    SELECT SENHA FROM USUARIOS WHERE ID = ?
                """, (usuario_id,))
                senha_hash_banco = cur.fetchone()[0]
                
                print(f"🔐 [LOGIN] Senha do banco: {senha_hash_banco[:20]}..." if senha_hash_banco else "🔐 [LOGIN] Senha do banco: None")
                
                # Se não há senha no banco (usuário antigo), aceita qualquer senha
                if senha_hash_banco:
                    senha_hash_digitada = hash_senha(senha)
                    print(f"🔐 [LOGIN] Senha digitada (hash): {senha_hash_digitada[:20]}...")
                    print(f"🔐 [LOGIN] Senhas iguais: {senha_hash_digitada == senha_hash_banco}")
                    
                    if senha_hash_digitada != senha_hash_banco:
                        print("❌ [LOGIN] Senha incorreta")
                        flash('Senha incorreta.', 'error')
                        return render_template('login.html')
                else:
                    print("⚠️ [LOGIN] Usuário sem senha no banco - aceitando qualquer senha")
                
                print("✅ [LOGIN] Senha válida - criando sessão")
                
                # Armazena dados na sessão
                session['usuario_id'] = usuario_id
                session['usuario_nome'] = nome
                session['usuario_email'] = email
                session['usuario_tipo'] = tipo_usuario
                session['logado'] = True
                
                print(f"✅ [LOGIN] Sessão criada:")
                print(f"   usuario_id: {session['usuario_id']}")
                print(f"   usuario_nome: {session['usuario_nome']}")
                print(f"   usuario_email: {session['usuario_email']}")
                print(f"   usuario_tipo: {session['usuario_tipo']}")
                print(f"   logado: {session['logado']}")
                
                # Atualiza último acesso
                cur.execute("""
                    UPDATE USUARIOS 
                    SET DTHR_ULTIMO_ACESSO = CURRENT_TIMESTAMP 
                    WHERE ID = ?
                """, (usuario_id,))
                con.commit()
                
                print("✅ [LOGIN] Último acesso atualizado")
                flash(f'Bem-vindo(a), {nome}!', 'success')
                
                # Redireciona baseado no tipo de usuário
                if tipo_usuario in ['TECNICO', 'ADMIN']:
                    print("🔄 [LOGIN] Redirecionando para Dashboard")
                    return redirect(url_for('dashboard.dashboard'))
                else:
                    print("🔄 [LOGIN] Redirecionando para Formulário")
                    return redirect(url_for('formulario.formulario'))
                    
        except Exception as e:
            print(f"❌ [LOGIN] Erro durante login: {str(e)}")
            import traceback
            traceback.print_exc()
            flash(f'Erro ao fazer login: {str(e)}', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Logout do usuário"""
    session.clear()
    flash('Você foi desconectado com sucesso.', 'success')
    return redirect(url_for('auth.login'))

def login_required(f):
    """Decorator para verificar se usuário está logado"""
    from functools import wraps
    from flask import redirect, url_for, flash
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logado'):
            flash('Por favor, faça login para acessar esta página.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator para verificar se usuário é admin"""
    from functools import wraps
    from flask import redirect, url_for, flash
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("🔍 [ADMIN_REQUIRED] Verificando acesso...")
        print("🔍 [ADMIN_REQUIRED] Sessão:", dict(session))
        print("🔍 [ADMIN_REQUIRED] logado:", session.get('logado'))
        print("🔍 [ADMIN_REQUIRED] usuario_tipo:", session.get('usuario_tipo'))
        
        if not session.get('logado'):
            print("❌ [ADMIN_REQUIRED] Usuário não logado")
            flash('Por favor, faça login para acessar esta página.', 'error')
            return redirect(url_for('auth.login'))
        
        if session.get('usuario_tipo') not in ['ADMIN']:
            print("❌ [ADMIN_REQUIRED] Usuário não é admin")
            flash('Acesso negado. Você não tem permissão para acessar esta área.', 'error')
            return redirect(url_for('dashboard.dashboard'))
        
        print("✅ [ADMIN_REQUIRED] Acesso permitido")
        return f(*args, **kwargs)
    return decorated_function
