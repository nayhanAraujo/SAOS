from flask import Blueprint, request, jsonify
from models.solicitacao import SolicitacaoModel
from models.historico import HistoricoModel
from models.base import BaseModel
from utils.email_service import EmailService
from database.connection import db_connection
from datetime import datetime
import json

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Instâncias dos modelos
solicitacao_model = SolicitacaoModel()
historico_model = HistoricoModel()
email_service = EmailService()

# =====================================================
# ENDPOINTS DE SOLICITAÇÕES
# =====================================================

@api_bp.route('/solicitacoes', methods=['GET'])
def listar_solicitacoes():
    """Lista todas as solicitações com filtros"""
    try:
        # Parâmetros de filtro
        status_id = request.args.get('status_id', type=int)
        prioridade_id = request.args.get('prioridade_id', type=int)
        cliente_id = request.args.get('cliente_id', type=int)
        tecnico_id = request.args.get('tecnico_id', type=int)
        limit = request.args.get('limit', type=int, default=50)
        
        # Constrói a query base
        where_conditions = []
        params = []
        
        if status_id:
            where_conditions.append("ID_STATUS = ?")
            params.append(status_id)
        
        if prioridade_id:
            where_conditions.append("ID_PRIORIDADE = ?")
            params.append(prioridade_id)
        
        if cliente_id:
            where_conditions.append("ID_CLIENTE = ?")
            params.append(cliente_id)
        
        if tecnico_id:
            where_conditions.append("ID_TECNICO_RESPONSAVEL = ?")
            params.append(tecnico_id)
        
        where_clause = " AND ".join(where_conditions) if where_conditions else None
        
        # Busca as solicitações
        solicitacoes = solicitacao_model.get_all(
            where=where_clause,
            params=params,
            order_by="DTHR_CRIACAO DESC",
            limit=limit
        )
        
        return jsonify({
            'success': True,
            'data': solicitacoes,
            'total': len(solicitacoes)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/solicitacoes', methods=['POST'])
def criar_solicitacao():
    """Cria uma nova solicitação"""
    try:
        dados = request.get_json()
        
        # Validações básicas
        campos_obrigatorios = ['titulo', 'descricao', 'id_cliente', 'id_categoria', 'id_prioridade']
        for campo in campos_obrigatorios:
            if not dados.get(campo):
                return jsonify({
                    'success': False,
                    'error': f'Campo obrigatório não informado: {campo}'
                }), 400
        
        # Converte para o formato do banco
        dados_banco = {
            'TITULO': dados['titulo'],
            'DESCRICAO': dados['descricao'],
            'ID_CLIENTE': dados['id_cliente'],
            'ID_CATEGORIA': dados['id_categoria'],
            'ID_PRIORIDADE': dados['id_prioridade'],
            'SISTEMA': dados.get('sistema'),
            'MODULO': dados.get('modulo'),
            'ID_TECNICO_CRIADOR': dados.get('id_tecnico_criador'),
            'URGENTE': dados.get('urgente', False),
            'CONFIDENCIAL': dados.get('confidencial', False)
        }
        
        # Cria a solicitação
        solicitacao_id = solicitacao_model.criar_solicitacao(dados_banco)
        
        # Envia email de confirmação
        try:
            email_service.enviar_confirmacao_abertura(solicitacao_id)
        except Exception as email_error:
            print(f"Erro ao enviar email: {email_error}")
        
        # Retorna a solicitação criada
        solicitacao = solicitacao_model.get_by_id(solicitacao_id)
        
        return jsonify({
            'success': True,
            'data': solicitacao,
            'message': 'Solicitação criada com sucesso'
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/solicitacoes/<int:solicitacao_id>', methods=['GET'])
def obter_solicitacao(solicitacao_id):
    """Obtém uma solicitação específica"""
    try:
        solicitacao = solicitacao_model.get_by_id(solicitacao_id)
        
        if not solicitacao:
            return jsonify({
                'success': False,
                'error': 'Solicitação não encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'data': solicitacao
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/solicitacoes/<int:solicitacao_id>', methods=['PUT'])
def atualizar_solicitacao(solicitacao_id):
    """Atualiza uma solicitação"""
    try:
        dados = request.get_json()
        
        # Verifica se a solicitação existe
        solicitacao = solicitacao_model.get_by_id(solicitacao_id)
        if not solicitacao:
            return jsonify({
                'success': False,
                'error': 'Solicitação não encontrada'
            }), 404
        
        # Campos permitidos para atualização
        campos_permitidos = [
            'TITULO', 'DESCRICAO', 'ID_CATEGORIA', 'ID_PRIORIDADE',
            'ID_TECNICO_RESPONSAVEL', 'SISTEMA', 'MODULO', 'URGENTE', 'CONFIDENCIAL'
        ]
        
        dados_update = {}
        for campo in campos_permitidos:
            if campo.lower() in dados:
                dados_update[campo] = dados[campo.lower()]
        
        if dados_update:
            solicitacao_model.update(solicitacao_id, dados_update)
        
        # Retorna a solicitação atualizada
        solicitacao_atualizada = solicitacao_model.get_by_id(solicitacao_id)
        
        return jsonify({
            'success': True,
            'data': solicitacao_atualizada,
            'message': 'Solicitação atualizada com sucesso'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/solicitacoes/<int:solicitacao_id>/status', methods=['PUT'])
def atualizar_status_solicitacao(solicitacao_id):
    """Atualiza o status de uma solicitação"""
    try:
        dados = request.get_json()
        
        novo_status_id = dados.get('novo_status_id')
        tecnico_id = dados.get('tecnico_id')
        comentario = dados.get('comentario')
        
        if not novo_status_id or not tecnico_id:
            return jsonify({
                'success': False,
                'error': 'novo_status_id e tecnico_id são obrigatórios'
            }), 400
        
        # Atualiza o status
        solicitacao_model.atualizar_status(solicitacao_id, novo_status_id, tecnico_id, comentario)
        
        # Envia email de atualização
        try:
            email_service.enviar_atualizacao_status(solicitacao_id, novo_status_id, comentario)
        except Exception as email_error:
            print(f"Erro ao enviar email: {email_error}")
        
        # Retorna a solicitação atualizada
        solicitacao = solicitacao_model.get_by_id(solicitacao_id)
        
        return jsonify({
            'success': True,
            'data': solicitacao,
            'message': 'Status atualizado com sucesso'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/solicitacoes/<int:solicitacao_id>/comentarios', methods=['POST'])
def adicionar_comentario(solicitacao_id):
    """Adiciona um comentário à solicitação"""
    try:
        dados = request.get_json()
        
        comentario_texto = dados.get('comentario')
        usuario_id = dados.get('usuario_id')
        interno = dados.get('interno', False)
        
        if not comentario_texto or not usuario_id:
            return jsonify({
                'success': False,
                'error': 'comentario e usuario_id são obrigatórios'
            }), 400
        
        # Adiciona o comentário
        from models.comentario import ComentarioModel
        comentario_model = ComentarioModel()
        
        comentario_id = comentario_model.create({
            'ID_SOLICITACAO': solicitacao_id,
            'ID_USUARIO': usuario_id,
            'COMENTARIO': comentario_texto,
            'INTERNO': interno,
            'DTHR_CRIACAO': datetime.now()
        })
        
        # Registra no histórico
        historico_model.registrar_acao(
            solicitacao_id, usuario_id, 'COMENTARIO',
            f'Comentário adicionado: {comentario_texto[:50]}...'
        )
        
        return jsonify({
            'success': True,
            'message': 'Comentário adicionado com sucesso',
            'comentario_id': comentario_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# =====================================================
# ENDPOINTS DE DASHBOARD E RELATÓRIOS
# =====================================================

@api_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """Retorna dados do dashboard"""
    try:
        dados = solicitacao_model.get_dashboard_data()
        
        return jsonify({
            'success': True,
            'data': dados
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/solicitacoes/urgentes', methods=['GET'])
def solicitacoes_urgentes():
    """Retorna solicitações urgentes"""
    try:
        limit = request.args.get('limit', type=int, default=10)
        solicitacoes = solicitacao_model.buscar_urgentes(limit)
        
        return jsonify({
            'success': True,
            'data': solicitacoes,
            'total': len(solicitacoes)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/solicitacoes/vencidas', methods=['GET'])
def solicitacoes_vencidas():
    """Retorna solicitações vencidas"""
    try:
        limit = request.args.get('limit', type=int, default=10)
        solicitacoes = solicitacao_model.buscar_vencidas(limit)
        
        return jsonify({
            'success': True,
            'data': solicitacoes,
            'total': len(solicitacoes)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# =====================================================
# ENDPOINTS DE CATEGORIAS, PRIORIDADES E STATUS
# =====================================================

@api_bp.route('/categorias', methods=['GET'])
def listar_categorias():
    """Lista todas as categorias"""
    try:
        categoria_model = BaseModel()
        categoria_model.table_name = 'CATEGORIAS'
        
        categorias = categoria_model.get_all(
            where="ATIVO = TRUE",
            order_by="NOME"
        )
        
        return jsonify({
            'success': True,
            'data': categorias
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/prioridades', methods=['GET'])
def listar_prioridades():
    """Lista todas as prioridades"""
    try:
        prioridade_model = BaseModel()
        prioridade_model.table_name = 'PRIORIDADES'
        
        prioridades = prioridade_model.get_all(
            where="ATIVO = TRUE",
            order_by="ORDEM"
        )
        
        return jsonify({
            'success': True,
            'data': prioridades
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/status', methods=['GET'])
def listar_status():
    """Lista todos os status"""
    try:
        status_model = BaseModel()
        status_model.table_name = 'STATUS'
        
        status_list = status_model.get_all(
            where="ATIVO = TRUE",
            order_by="ORDEM"
        )
        
        return jsonify({
            'success': True,
            'data': status_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# =====================================================
# ENDPOINTS DE HISTÓRICO
# =====================================================

@api_bp.route('/solicitacoes/<int:solicitacao_id>/historico', methods=['GET'])
def historico_solicitacao(solicitacao_id):
    """Retorna o histórico de uma solicitação"""
    try:
        limit = request.args.get('limit', type=int, default=50)
        historico = historico_model.buscar_por_solicitacao(solicitacao_id, limit)
        
        return jsonify({
            'success': True,
            'data': historico,
            'total': len(historico)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# =====================================================
# ENDPOINTS DE EMAIL
# =====================================================

@api_bp.route('/solicitacoes/<int:solicitacao_id>/enviar-email', methods=['POST'])
def enviar_email_solicitacao(solicitacao_id):
    """Envia email para uma solicitação"""
    try:
        dados = request.get_json()
        tipo_email = dados.get('tipo')
        
        if tipo_email == 'confirmacao_abertura':
            sucesso = email_service.enviar_confirmacao_abertura(solicitacao_id)
        elif tipo_email == 'solicitacao_informacoes':
            informacoes = dados.get('informacoes_necessarias', '')
            sucesso = email_service.enviar_solicitacao_informacoes(solicitacao_id, informacoes)
        elif tipo_email == 'resolucao_concluida':
            solucao = dados.get('solucao', '')
            sucesso = email_service.enviar_resolucao_concluida(solicitacao_id, solucao)
        else:
            return jsonify({
                'success': False,
                'error': 'Tipo de email não suportado'
            }), 400
        
        return jsonify({
            'success': sucesso,
            'message': 'Email enviado com sucesso' if sucesso else 'Erro ao enviar email'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# =====================================================
# ENDPOINTS DE ADMINISTRAÇÃO
# =====================================================

@api_bp.route('/admin/stats', methods=['GET'])
def admin_stats():
    """Retorna estatísticas para o painel administrativo"""
    try:
        with db_connection() as con:
            cur = con.cursor()
            
            # Conta usuários
            cur.execute("SELECT COUNT(*) FROM USUARIOS WHERE ATIVO = TRUE")
            total_usuarios = cur.fetchone()[0]
            
            # Conta categorias
            cur.execute("SELECT COUNT(*) FROM CATEGORIAS WHERE ATIVO = TRUE")
            total_categorias = cur.fetchone()[0]
            
            # Conta status
            cur.execute("SELECT COUNT(*) FROM STATUS WHERE ATIVO = TRUE")
            total_status = cur.fetchone()[0]
            
            # Conta templates
            cur.execute("SELECT COUNT(*) FROM TEMPLATES_EMAIL WHERE ATIVO = TRUE")
            total_templates = cur.fetchone()[0]
            
            return jsonify({
                'success': True,
                'data': {
                    'usuarios': total_usuarios,
                    'categorias': total_categorias,
                    'status': total_status,
                    'templates': total_templates
                }
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/usuarios', methods=['GET'])
def listar_usuarios():
    """Lista todos os usuários"""
    try:
        with db_connection() as con:
            cur = con.cursor()
            
            cur.execute("""
                SELECT ID, NOME, EMAIL, CPF_CNPJ, TIPO_USUARIO, ATIVO, DTHR_CRIACAO
                FROM USUARIOS 
                ORDER BY NOME
            """)
            
            usuarios = []
            for row in cur.fetchall():
                usuarios.append({
                    'ID': row[0],
                    'NOME': row[1],
                    'EMAIL': row[2],
                    'CPF_CNPJ': row[3],
                    'TIPO_USUARIO': row[4],
                    'ATIVO': row[5],
                    'DTHR_CRIACAO': row[6].isoformat() if row[6] else None
                })
            
            return jsonify({
                'success': True,
                'data': usuarios
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/usuarios', methods=['POST'])
def criar_usuario():
    """Cria um novo usuário"""
    try:
        dados = request.get_json()
        
        # Validações básicas
        campos_obrigatorios = ['nome', 'email', 'tipo_usuario']
        for campo in campos_obrigatorios:
            if not dados.get(campo):
                return jsonify({
                    'success': False,
                    'error': f'Campo obrigatório não informado: {campo}'
                }), 400
        
        with db_connection() as con:
            cur = con.cursor()
            
            # Verifica se email já existe
            cur.execute("SELECT ID FROM USUARIOS WHERE EMAIL = ?", (dados['email'],))
            if cur.fetchone():
                return jsonify({
                    'success': False,
                    'error': 'Email já cadastrado'
                }), 400
            
            # Insere o usuário
            cur.execute("""
                INSERT INTO USUARIOS (NOME, EMAIL, CPF_CNPJ, TELEFONE, TIPO_USUARIO, SENHA, ATIVO, DTHR_CRIACAO)
                VALUES (?, ?, ?, ?, ?, ?, TRUE, CURRENT_TIMESTAMP)
            """, (
                dados['nome'],
                dados['email'],
                dados.get('cpf_cnpj'),
                dados.get('telefone'),
                dados['tipo_usuario'],
                dados.get('senha', '')  # Senha será definida pelo usuário no primeiro acesso
            ))
            
            con.commit()
            
            # Para Firebird, precisamos buscar o ID do usuário recém-criado
            cur.execute("""
                SELECT ID FROM USUARIOS 
                WHERE EMAIL = ? 
                ORDER BY DTHR_CRIACAO DESC
            """, (dados['email'],))
            novo_id = cur.fetchone()[0]
            
            return jsonify({
                'success': True,
                'message': 'Usuário criado com sucesso',
                'id': novo_id
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/usuarios/<int:usuario_id>', methods=['PUT'])
def atualizar_usuario(usuario_id):
    """Atualiza um usuário"""
    try:
        dados = request.get_json()
        
        with db_connection() as con:
            cur = con.cursor()
            
            # Verifica se usuário existe
            cur.execute("SELECT ID FROM USUARIOS WHERE ID = ?", (usuario_id,))
            if not cur.fetchone():
                return jsonify({
                    'success': False,
                    'error': 'Usuário não encontrado'
                }), 404
            
            # Atualiza o usuário
            cur.execute("""
                UPDATE USUARIOS 
                SET NOME = ?, EMAIL = ?, CPF_CNPJ = ?, TELEFONE = ?, TIPO_USUARIO = ?, ATIVO = ?
                WHERE ID = ?
            """, (
                dados.get('nome'),
                dados.get('email'),
                dados.get('cpf_cnpj'),
                dados.get('telefone'),
                dados.get('tipo_usuario'),
                dados.get('ativo', True),
                usuario_id
            ))
            
            con.commit()
            
            return jsonify({
                'success': True,
                'message': 'Usuário atualizado com sucesso'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/usuarios/<int:usuario_id>/toggle', methods=['POST'])
def toggle_usuario(usuario_id):
    """Ativa/desativa um usuário"""
    try:
        with db_connection() as con:
            cur = con.cursor()
            
            # Busca o status atual
            cur.execute("SELECT ATIVO FROM USUARIOS WHERE ID = ?", (usuario_id,))
            result = cur.fetchone()
            
            if not result:
                return jsonify({
                    'success': False,
                    'error': 'Usuário não encontrado'
                }), 404
            
            novo_status = not result[0]
            
            # Atualiza o status
            cur.execute("UPDATE USUARIOS SET ATIVO = ? WHERE ID = ?", (novo_status, usuario_id))
            con.commit()
            
            return jsonify({
                'success': True,
                'message': f'Usuário {"ativado" if novo_status else "desativado"} com sucesso',
                'ativo': novo_status
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/templates-email', methods=['GET'])
def listar_templates_email():
    """Lista todos os templates de email"""
    print("🔍 [API] Tentando listar templates de email...")
    try:
        with db_connection() as con:
            cur = con.cursor()
            
            print("🔍 [API] Executando query para buscar templates...")
            cur.execute("""
                SELECT ID, NOME, ASSUNTO, ATIVO, DTHR_CRIACAO, DTHR_ATUALIZACAO
                FROM TEMPLATES_EMAIL 
                ORDER BY NOME
            """)
            
            templates = []
            rows = cur.fetchall()
            print(f"🔍 [API] Encontrados {len(rows)} templates no banco de dados.")
            
            for row in rows:
                print(f"🔍 [API] Template row: {row}")
                templates.append({
                    'id': row[0],
                    'nome': row[1],
                    'assunto': row[2],
                    'ativo': row[3],
                    'dthr_criacao': row[4].isoformat() if row[4] else None,
                    'dthr_atualizacao': row[5].isoformat() if row[5] else None
                })
            
            print(f"🔍 [API] Retornando {len(templates)} templates para o frontend.")
            return jsonify({
                'success': True,
                'templates': templates
            })
            
    except Exception as e:
        print(f"❌ [API] Erro ao listar templates: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Erro ao listar templates: {str(e)}'
        }), 500

@api_bp.route('/templates-email', methods=['POST'])
def criar_template_email():
    """Cria um novo template de email"""
    try:
        dados = request.get_json()
        
        # Validações básicas
        if not dados.get('nome'):
            return jsonify({'success': False, 'message': 'Nome do template é obrigatório'}), 400
        
        if not dados.get('assunto'):
            return jsonify({'success': False, 'message': 'Assunto é obrigatório'}), 400
        
        if not dados.get('corpo_html'):
            return jsonify({'success': False, 'message': 'Corpo HTML é obrigatório'}), 400
        
        with db_connection() as con:
            cur = con.cursor()
            cur.execute("""
                INSERT INTO TEMPLATES_EMAIL (NOME, ASSUNTO, CORPO_HTML, CORPO_TEXTO, VARIAVEIS, ATIVO)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                dados['nome'],
                dados['assunto'],
                dados['corpo_html'].encode('utf-8'),
                dados.get('corpo_texto', '').encode('utf-8'),
                json.dumps(dados.get('variaveis', [])),
                dados.get('ativo', True)
            ))
            con.commit()
            
            return jsonify({
                'success': True,
                'message': 'Template criado com sucesso'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao criar template: {str(e)}'
        }), 500

@api_bp.route('/templates-email/<int:template_id>', methods=['GET'])
def obter_template_email(template_id):
    """Obtém um template específico"""
    try:
        with db_connection() as con:
            cur = con.cursor()
            cur.execute("""
                SELECT ID, NOME, ASSUNTO, CORPO_HTML, CORPO_TEXTO, VARIAVEIS, ATIVO
                FROM TEMPLATES_EMAIL
                WHERE ID = ?
            """, (template_id,))
            
            row = cur.fetchone()
            if row:
                template = {
                    'id': row[0],
                    'nome': row[1],
                    'assunto': row[2],
                    'corpo_html': row[3].decode('utf-8') if row[3] else '',
                    'corpo_texto': row[4].decode('utf-8') if row[4] else '',
                    'variaveis': json.loads(row[5]) if row[5] else [],
                    'ativo': row[6]
                }
                
                return jsonify({
                    'success': True,
                    'template': template
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Template não encontrado'
                }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao obter template: {str(e)}'
        }), 500

@api_bp.route('/templates-email/<int:template_id>', methods=['PUT'])
def atualizar_template_email(template_id):
    """Atualiza um template existente"""
    try:
        dados = request.get_json()
        
        # Validações básicas
        if not dados.get('nome'):
            return jsonify({'success': False, 'message': 'Nome do template é obrigatório'}), 400
        
        if not dados.get('assunto'):
            return jsonify({'success': False, 'message': 'Assunto é obrigatório'}), 400
        
        if not dados.get('corpo_html'):
            return jsonify({'success': False, 'message': 'Corpo HTML é obrigatório'}), 400
        
        with db_connection() as con:
            cur = con.cursor()
            cur.execute("""
                UPDATE TEMPLATES_EMAIL 
                SET NOME = ?, ASSUNTO = ?, CORPO_HTML = ?, CORPO_TEXTO = ?, 
                    VARIAVEIS = ?, ATIVO = ?, DTHR_ATUALIZACAO = CURRENT_TIMESTAMP
                WHERE ID = ?
            """, (
                dados['nome'],
                dados['assunto'],
                dados['corpo_html'].encode('utf-8'),
                dados.get('corpo_texto', '').encode('utf-8'),
                json.dumps(dados.get('variaveis', [])),
                dados.get('ativo', True),
                template_id
            ))
            con.commit()
            
            return jsonify({
                'success': True,
                'message': 'Template atualizado com sucesso'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao atualizar template: {str(e)}'
        }), 500

@api_bp.route('/templates-email/<int:template_id>', methods=['DELETE'])
def excluir_template_email(template_id):
    """Exclui um template (soft delete)"""
    try:
        with db_connection() as con:
            cur = con.cursor()
            cur.execute("""
                UPDATE TEMPLATES_EMAIL 
                SET ATIVO = FALSE, DTHR_ATUALIZACAO = CURRENT_TIMESTAMP
                WHERE ID = ?
            """, (template_id,))
            con.commit()
            
            return jsonify({
                'success': True,
                'message': 'Template excluído com sucesso'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao excluir template: {str(e)}'
        }), 500

@api_bp.route('/templates-email/<int:template_id>/toggle', methods=['POST'])
def toggle_template_email(template_id):
    """Ativa ou desativa um template"""
    try:
        dados = request.get_json()
        ativo = dados.get('ativo', False)
        
        with db_connection() as con:
            cur = con.cursor()
            cur.execute("""
                UPDATE TEMPLATES_EMAIL 
                SET ATIVO = ?, DTHR_ATUALIZACAO = CURRENT_TIMESTAMP
                WHERE ID = ?
            """, (ativo, template_id))
            con.commit()
            
            acao = 'ativado' if ativo else 'desativado'
            return jsonify({
                'success': True,
                'message': f'Template {acao} com sucesso'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao alterar status do template: {str(e)}'
        }), 500

@api_bp.route('/templates-email/testar', methods=['POST'])
def testar_template_email():
    """Envia email de teste usando um template"""
    try:
        dados = request.get_json()
        
        if not dados.get('template_id'):
            return jsonify({'success': False, 'message': 'ID do template é obrigatório'}), 400
        
        if not dados.get('email'):
            return jsonify({'success': False, 'message': 'Email de destino é obrigatório'}), 400
        
        # Importar o gerenciador de templates
        from utils.email_template_manager import EmailTemplateManager
        
        template_manager = EmailTemplateManager()
        
        # Enviar email de teste
        sucesso = template_manager.enviar_email_com_template(
            template_id=dados['template_id'],
            destinatario=dados['email'],
            variaveis=dados.get('variaveis', {})
        )
        
        if sucesso:
            return jsonify({
                'success': True,
                'message': 'Email de teste enviado com sucesso'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Erro ao enviar email de teste'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao testar template: {str(e)}'
        }), 500
