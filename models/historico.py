from models.base import BaseModel
from datetime import datetime

class HistoricoModel(BaseModel):
    def __init__(self):
        super().__init__()
        self.table_name = 'HISTORICO'
    
    def buscar_por_solicitacao(self, solicitacao_id, limit=None):
        """Busca histórico de uma solicitação específica"""
        return self.get_all(
            where="ID_SOLICITACAO = ?",
            params=(solicitacao_id,),
            order_by="DTHR_ACAO DESC",
            limit=limit
        )
    
    def buscar_por_usuario(self, usuario_id, limit=None):
        """Busca histórico de ações de um usuário"""
        return self.get_all(
            where="ID_USUARIO = ?",
            params=(usuario_id,),
            order_by="DTHR_ACAO DESC",
            limit=limit
        )
    
    def buscar_por_tipo(self, tipo_acao, limit=None):
        """Busca histórico por tipo de ação"""
        return self.get_all(
            where="TIPO_ACAO = ?",
            params=(tipo_acao,),
            order_by="DTHR_ACAO DESC",
            limit=limit
        )
    
    def buscar_por_periodo(self, data_inicio, data_fim, limit=None):
        """Busca histórico por período"""
        return self.get_all(
            where="DTHR_ACAO BETWEEN ? AND ?",
            params=(data_inicio, data_fim),
            order_by="DTHR_ACAO DESC",
            limit=limit
        )
    
    def registrar_acao(self, solicitacao_id, usuario_id, tipo_acao, descricao, dados_anteriores=None, dados_novos=None):
        """Registra uma nova ação no histórico"""
        return self.create({
            'ID_SOLICITACAO': solicitacao_id,
            'ID_USUARIO': usuario_id,
            'TIPO_ACAO': tipo_acao,
            'DESCRICAO': descricao,
            'DADOS_ANTERIORES': dados_anteriores,
            'DADOS_NOVOS': dados_novos,
            'DTHR_ACAO': datetime.now()
        })
