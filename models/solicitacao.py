from models.base import BaseModel
from datetime import datetime, timedelta
import json

class SolicitacaoModel(BaseModel):
    def __init__(self):
        super().__init__()
        self.table_name = 'SOLICITACOES'
    
    def criar_solicitacao(self, dados):
        """Cria uma nova solicitação com validações"""
        # Validações básicas
        campos_obrigatorios = ['TITULO', 'DESCRICAO', 'ID_CLIENTE', 'ID_CATEGORIA', 'ID_PRIORIDADE']
        for campo in campos_obrigatorios:
            if not dados.get(campo):
                raise ValueError(f"Campo obrigatório não informado: {campo}")
        
        # Define status inicial
        dados['ID_STATUS'] = 1  # Status "Aberto"
        
        # Calcula prazo baseado na prioridade
        prazo_horas = self._get_prazo_prioridade(dados['ID_PRIORIDADE'])
        dados['PRAZO_RESOLUCAO'] = datetime.now() + timedelta(hours=prazo_horas)
        
        # Calcula prazo de escalonamento
        escalonamento_horas = self._get_escalonamento_prioridade(dados['ID_PRIORIDADE'])
        dados['PRAZO_ESCALONAMENTO'] = datetime.now() + timedelta(hours=escalonamento_horas)
        
        # Gera código de referência
        dados['CODIGO_REFERENCIA'] = self._gerar_codigo_referencia()
        
        # Insere no banco
        solicitacao_id = self.create(dados)
        
        # Registra no histórico
        self._registrar_historico(solicitacao_id, dados.get('ID_TECNICO_CRIADOR', dados['ID_CLIENTE']), 
                                'CRIACAO', 'Solicitação criada')
        
        return solicitacao_id
    
    def atualizar_status(self, solicitacao_id, novo_status_id, tecnico_id, comentario=None):
        """Atualiza o status de uma solicitação"""
        solicitacao = self.get_by_id(solicitacao_id)
        if not solicitacao:
            raise ValueError("Solicitação não encontrada")
        
        # Atualiza o status
        dados_update = {
            'ID_STATUS': novo_status_id,
            'ID_TECNICO_RESPONSAVEL': tecnico_id,
            'DTHR_ATUALIZACAO': datetime.now()
        }
        
        # Se foi resolvida, marca data de resolução
        if self._is_status_finalizado(novo_status_id):
            dados_update['DTHR_RESOLUCAO'] = datetime.now()
        
        # Se foi fechada, marca data de fechamento
        if novo_status_id == 7:  # Status "Fechado"
            dados_update['DTHR_FECHAMENTO'] = datetime.now()
        
        self.update(solicitacao_id, dados_update)
        
        # Registra no histórico
        descricao = f"Status alterado para {self._get_nome_status(novo_status_id)}"
        if comentario:
            descricao += f" - {comentario}"
        
        self._registrar_historico(solicitacao_id, tecnico_id, 'MUDANCA_STATUS', descricao)
        
        return True
    
    def buscar_por_cliente(self, cliente_id, limit=None):
        """Busca solicitações de um cliente específico"""
        return self.get_all(
            where="ID_CLIENTE = ?",
            params=(cliente_id,),
            order_by="DTHR_CRIACAO DESC",
            limit=limit
        )
    
    def buscar_por_tecnico(self, tecnico_id, limit=None):
        """Busca solicitações atribuídas a um técnico"""
        return self.get_all(
            where="ID_TECNICO_RESPONSAVEL = ?",
            params=(tecnico_id,),
            order_by="DTHR_CRIACAO DESC",
            limit=limit
        )
    
    def buscar_por_status(self, status_id, limit=None):
        """Busca solicitações por status"""
        return self.get_all(
            where="ID_STATUS = ?",
            params=(status_id,),
            order_by="DTHR_CRIACAO DESC",
            limit=limit
        )
    
    def buscar_por_prioridade(self, prioridade_id, limit=None):
        """Busca solicitações por prioridade"""
        return self.get_all(
            where="ID_PRIORIDADE = ?",
            params=(prioridade_id,),
            order_by="DTHR_CRIACAO DESC",
            limit=limit
        )
    
    def buscar_urgentes(self, limit=None):
        """Busca solicitações urgentes (próximas do prazo)"""
        prazo_limite = datetime.now() + timedelta(hours=24)
        return self.get_all(
            where="PRAZO_RESOLUCAO <= ? AND ID_STATUS NOT IN (6, 7, 8)",
            params=(prazo_limite,),
            order_by="PRAZO_RESOLUCAO ASC",
            limit=limit
        )
    
    def buscar_vencidas(self, limit=None):
        """Busca solicitações vencidas"""
        return self.get_all(
            where="PRAZO_RESOLUCAO < ? AND ID_STATUS NOT IN (6, 7, 8)",
            params=(datetime.now(),),
            order_by="PRAZO_RESOLUCAO ASC",
            limit=limit
        )
    
    def buscar_por_periodo(self, data_inicio, data_fim, limit=None):
        """Busca solicitações criadas em um período"""
        return self.get_all(
            where="DTHR_CRIACAO BETWEEN ? AND ?",
            params=(data_inicio, data_fim),
            order_by="DTHR_CRIACAO DESC",
            limit=limit
        )
    
    def get_dashboard_data(self):
        """Retorna dados para o dashboard"""
        with db_connection() as con:
            cur = con.cursor()
            
            # Total de solicitações
            cur.execute("SELECT COUNT(*) FROM SOLICITACOES")
            total = cur.fetchone()[0]
            
            # Por status
            cur.execute("""
                SELECT s.NOME, COUNT(sol.ID) 
                FROM STATUS s 
                LEFT JOIN SOLICITACOES sol ON s.ID = sol.ID_STATUS 
                WHERE s.ATIVO = TRUE
                GROUP BY s.ID, s.NOME
                ORDER BY s.ORDEM
            """)
            por_status = dict(cur.fetchall())
            
            # Por prioridade
            cur.execute("""
                SELECT p.NOME, COUNT(sol.ID) 
                FROM PRIORIDADES p 
                LEFT JOIN SOLICITACOES sol ON p.ID = sol.ID_PRIORIDADE 
                WHERE p.ATIVO = TRUE
                GROUP BY p.ID, p.NOME
                ORDER BY p.ORDEM
            """)
            por_prioridade = dict(cur.fetchall())
            
            # Urgentes
            cur.execute("""
                SELECT COUNT(*) FROM SOLICITACOES 
                WHERE PRAZO_RESOLUCAO <= ? AND ID_STATUS NOT IN (6, 7, 8)
            """, (datetime.now() + timedelta(hours=24),))
            urgentes = cur.fetchone()[0]
            
            # Vencidas
            cur.execute("""
                SELECT COUNT(*) FROM SOLICITACOES 
                WHERE PRAZO_RESOLUCAO < ? AND ID_STATUS NOT IN (6, 7, 8)
            """, (datetime.now(),))
            vencidas = cur.fetchone()[0]
            
            return {
                'total': total,
                'por_status': por_status,
                'por_prioridade': por_prioridade,
                'urgentes': urgentes,
                'vencidas': vencidas
            }
    
    def _get_prazo_prioridade(self, prioridade_id):
        """Obtém o prazo em horas para uma prioridade"""
        with db_connection() as con:
            cur = con.cursor()
            cur.execute("SELECT PRAZO_HORAS FROM PRIORIDADES WHERE ID = ?", (prioridade_id,))
            result = cur.fetchone()
            return result[0] if result else 72  # Padrão 72 horas
    
    def _get_escalonamento_prioridade(self, prioridade_id):
        """Obtém o prazo de escalonamento em horas para uma prioridade"""
        with db_connection() as con:
            cur = con.cursor()
            cur.execute("SELECT ESCALONAMENTO_HORAS FROM PRIORIDADES WHERE ID = ?", (prioridade_id,))
            result = cur.fetchone()
            return result[0] if result else 48  # Padrão 48 horas
    
    def _gerar_codigo_referencia(self):
        """Gera um código de referência único"""
        data_atual = datetime.now()
        codigo = f"OS{data_atual.strftime('%Y%m%d')}"
        
        # Busca o próximo número sequencial
        with db_connection() as con:
            cur = con.cursor()
            cur.execute("""
                SELECT COUNT(*) FROM SOLICITACOES 
                WHERE CODIGO_REFERENCIA LIKE ?
            """, (f"{codigo}%",))
            count = cur.fetchone()[0]
        
        return f"{codigo}{str(count + 1).zfill(4)}"
    
    def _is_status_finalizado(self, status_id):
        """Verifica se um status é finalizado"""
        with db_connection() as con:
            cur = con.cursor()
            cur.execute("SELECT FINALIZADO FROM STATUS WHERE ID = ?", (status_id,))
            result = cur.fetchone()
            return result[0] if result else False
    
    def _get_nome_status(self, status_id):
        """Obtém o nome de um status"""
        with db_connection() as con:
            cur = con.cursor()
            cur.execute("SELECT NOME FROM STATUS WHERE ID = ?", (status_id,))
            result = cur.fetchone()
            return result[0] if result else "Desconhecido"
    
    def _registrar_historico(self, solicitacao_id, usuario_id, tipo_acao, descricao):
        """Registra uma ação no histórico"""
        from models.historico import HistoricoModel
        
        historico = HistoricoModel()
        historico.create({
            'ID_SOLICITACAO': solicitacao_id,
            'ID_USUARIO': usuario_id,
            'TIPO_ACAO': tipo_acao,
            'DESCRICAO': descricao,
            'DTHR_ACAO': datetime.now()
        })
