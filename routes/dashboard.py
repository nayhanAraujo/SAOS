from flask import Blueprint, render_template, session
from routes.auth import login_required, admin_required
from database.connection import db_connection

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    """Página principal do dashboard"""
    # Buscar dados específicos do usuário logado
    usuario_id = session.get('usuario_id')
    usuario_tipo = session.get('usuario_tipo')
    
    print(f"🔍 [DASHBOARD] Usuário ID: {usuario_id}, Tipo: {usuario_tipo}")
    
    try:
        with db_connection() as con:
            cur = con.cursor()
            
            # Primeiro, vamos verificar se há solicitações no banco
            cur.execute("SELECT COUNT(*) FROM SOLICITACOES")
            total_solicitacoes = cur.fetchone()[0]
            print(f"🔍 [DASHBOARD] Total de solicitações no banco: {total_solicitacoes}")
            
            # Verificar todas as solicitações para debug
            cur.execute("SELECT FIRST 5 ID, CODIGO_REFERENCIA, TITULO, ID_CLIENTE FROM SOLICITACOES")
            todas_solicitacoes = cur.fetchall()
            print(f"🔍 [DASHBOARD] Primeiras 5 solicitações: {todas_solicitacoes}")
            
            # Buscar solicitações do usuário
            if usuario_tipo == 'CLIENTE':
                # Cliente vê suas próprias solicitações
                print(f"🔍 [DASHBOARD] Executando query para CLIENTE")
                cur.execute("""
                    SELECT s.ID, s.CODIGO_REFERENCIA, s.TITULO, s.DESCRICAO, s.ID_CLIENTE, 
                           s.ID_CATEGORIA, s.ID_PRIORIDADE, s.ID_STATUS, s.SISTEMA, 
                           s.PRAZO_RESOLUCAO, s.DTHR_CRIACAO, s.DTHR_ATUALIZACAO,
                           c.NOME as NOME_CATEGORIA, c.COR as COR_CATEGORIA,
                           p.NOME as NOME_PRIORIDADE, p.COR as COR_PRIORIDADE,
                           st.NOME as NOME_STATUS, st.COR as COR_STATUS,
                           u.NOME as NOME_CLIENTE
                    FROM SOLICITACOES s
                    LEFT JOIN CATEGORIAS c ON s.ID_CATEGORIA = c.ID
                    LEFT JOIN PRIORIDADES p ON s.ID_PRIORIDADE = p.ID
                    LEFT JOIN STATUS st ON s.ID_STATUS = st.ID
                    LEFT JOIN USUARIOS u ON s.ID_CLIENTE = u.ID
                                         WHERE s.ID_CLIENTE = ?
                     ORDER BY s.DTHR_CRIACAO DESC
                     ROWS 10
                """, (usuario_id,))
            elif usuario_tipo == 'TECNICO':
                # Técnico vê solicitações que ele criou ou está responsável
                print(f"🔍 [DASHBOARD] Executando query para TECNICO")
                cur.execute("""
                    SELECT s.ID, s.CODIGO_REFERENCIA, s.TITULO, s.DESCRICAO, s.ID_CLIENTE, 
                           s.ID_CATEGORIA, s.ID_PRIORIDADE, s.ID_STATUS, s.SISTEMA, 
                           s.PRAZO_RESOLUCAO, s.DTHR_CRIACAO, s.DTHR_ATUALIZACAO,
                           c.NOME as NOME_CATEGORIA, c.COR as COR_CATEGORIA,
                           p.NOME as NOME_PRIORIDADE, p.COR as COR_PRIORIDADE,
                           st.NOME as NOME_STATUS, st.COR as COR_STATUS,
                           u.NOME as NOME_CLIENTE
                    FROM SOLICITACOES s
                    LEFT JOIN CATEGORIAS c ON s.ID_CATEGORIA = c.ID
                    LEFT JOIN PRIORIDADES p ON s.ID_PRIORIDADE = p.ID
                    LEFT JOIN STATUS st ON s.ID_STATUS = st.ID
                    LEFT JOIN USUARIOS u ON s.ID_CLIENTE = u.ID
                                         WHERE s.ID_CLIENTE = ?
                     ORDER BY s.DTHR_CRIACAO DESC
                     ROWS 10
                """, (usuario_id,))
            else:  # ADMIN
                # Admin vê todas as solicitações - query simplificada para debug
                print(f"🔍 [DASHBOARD] Executando query para ADMIN")
                cur.execute("""
                    SELECT s.ID, s.CODIGO_REFERENCIA, s.TITULO, s.DESCRICAO, s.ID_CLIENTE, 
                           s.ID_CATEGORIA, s.ID_PRIORIDADE, s.ID_STATUS, s.SISTEMA, 
                           s.PRAZO_RESOLUCAO, s.DTHR_CRIACAO, s.DTHR_ATUALIZACAO,
                           c.NOME as NOME_CATEGORIA, c.COR as COR_CATEGORIA,
                           p.NOME as NOME_PRIORIDADE, p.COR as COR_PRIORIDADE,
                           st.NOME as NOME_STATUS, st.COR as COR_STATUS,
                           u.NOME as NOME_CLIENTE
                    FROM SOLICITACOES s
                    LEFT JOIN CATEGORIAS c ON s.ID_CATEGORIA = c.ID
                    LEFT JOIN PRIORIDADES p ON s.ID_PRIORIDADE = p.ID
                    LEFT JOIN STATUS st ON s.ID_STATUS = st.ID
                    LEFT JOIN USUARIOS u ON s.ID_CLIENTE = u.ID
                                         ORDER BY s.DTHR_CRIACAO DESC
                     ROWS 10
                """)
            
            solicitacoes = []
            rows = cur.fetchall()
            print(f"🔍 [DASHBOARD] Encontradas {len(rows)} solicitações")
            
            for row in rows:
                print(f"🔍 [DASHBOARD] Row: {row}")
                solicitacao = {
                    'ID': row[0],
                    'CODIGO_REFERENCIA': row[1],
                    'TITULO': row[2],
                    'DESCRICAO': row[3].decode('utf-8') if row[3] else '',
                    'ID_CLIENTE': row[4],
                    'ID_CATEGORIA': row[5],
                    'ID_PRIORIDADE': row[6],
                    'ID_STATUS': row[7],
                    'SISTEMA': row[8],
                    'PRAZO_RESOLUCAO': row[9],
                    'DTHR_CRIACAO': row[10],
                    'DTHR_ATUALIZACAO': row[11],
                    'NOME_CATEGORIA': row[12],
                    'COR_CATEGORIA': row[13],
                    'NOME_PRIORIDADE': row[14],
                    'COR_PRIORIDADE': row[15],
                    'NOME_STATUS': row[16],
                    'COR_STATUS': row[17],
                    'NOME_CLIENTE': row[18]
                }
                solicitacoes.append(solicitacao)
            
            # Buscar estatísticas do usuário
            if usuario_tipo == 'CLIENTE':
                cur.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN s.ID_STATUS = 2 THEN 1 ELSE 0 END) as em_andamento,
                        SUM(CASE WHEN p.NOME = 'Urgente' THEN 1 ELSE 0 END) as urgentes,
                        SUM(CASE WHEN s.ID_STATUS = 4 THEN 1 ELSE 0 END) as resolvidas
                    FROM SOLICITACOES s
                    LEFT JOIN PRIORIDADES p ON s.ID_PRIORIDADE = p.ID
                    WHERE s.ID_CLIENTE = ?
                """, (usuario_id,))
            elif usuario_tipo == 'TECNICO':
                cur.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN s.ID_STATUS = 2 THEN 1 ELSE 0 END) as em_andamento,
                        SUM(CASE WHEN p.NOME = 'Urgente' THEN 1 ELSE 0 END) as urgentes,
                        SUM(CASE WHEN s.ID_STATUS = 4 THEN 1 ELSE 0 END) as resolvidas
                    FROM SOLICITACOES s
                    LEFT JOIN PRIORIDADES p ON s.ID_PRIORIDADE = p.ID
                                         WHERE s.ID_CLIENTE = ?
                """, (usuario_id,))
            else:  # ADMIN
                cur.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN s.ID_STATUS = 2 THEN 1 ELSE 0 END) as em_andamento,
                        SUM(CASE WHEN p.NOME = 'Urgente' THEN 1 ELSE 0 END) as urgentes,
                        SUM(CASE WHEN s.ID_STATUS = 4 THEN 1 ELSE 0 END) as resolvidas
                    FROM SOLICITACOES s
                    LEFT JOIN PRIORIDADES p ON s.ID_PRIORIDADE = p.ID
                """)
            
            stats = cur.fetchone()
            print(f"🔍 [DASHBOARD] Estatísticas: {stats}")
            estatisticas = {
                'total': stats[0] or 0,
                'em_andamento': stats[1] or 0,
                'urgentes': stats[2] or 0,
                'resolvidas': stats[3] or 0
            }
            print(f"🔍 [DASHBOARD] Estatísticas processadas: {estatisticas}")
            
    except Exception as e:
        print(f"Erro ao carregar dashboard: {e}")
        solicitacoes = []
        estatisticas = {'total': 0, 'em_andamento': 0, 'urgentes': 0, 'resolvidas': 0}
    
    return render_template('dashboard.html', 
                         solicitacoes=solicitacoes, 
                         estatisticas=estatisticas,
                         usuario_tipo=usuario_tipo)

@dashboard_bp.route('/admin')
@admin_required
def admin():
    """Área de administração"""
    return render_template('admin.html')

@dashboard_bp.route('/admin/templates')
@admin_required
def admin_templates():
    """Gerenciamento de templates de email"""
    print("🔍 [ADMIN_TEMPLATES] Acessando página de templates...")
    print("🔍 [ADMIN_TEMPLATES] Usuário logado:", session.get('usuario_id'), session.get('usuario_tipo'))
    return render_template('admin_templates.html')
