from models.base import BaseModel
from datetime import datetime

class ComentarioModel(BaseModel):
    def __init__(self):
        super().__init__()
        self.table_name = 'COMENTARIOS'
    
    def buscar_por_solicitacao(self, solicitacao_id, limit=None):
        """Busca comentários de uma solicitação específica"""
        return self.get_all(
            where="ID_SOLICITACAO = ?",
            params=(solicitacao_id,),
            order_by="DTHR_CRIACAO DESC",
            limit=limit
        )
    
    def buscar_por_usuario(self, usuario_id, limit=None):
        """Busca comentários de um usuário"""
        return self.get_all(
            where="ID_USUARIO = ?",
            params=(usuario_id,),
            order_by="DTHR_CRIACAO DESC",
            limit=limit
        )
    
    def buscar_publicos(self, solicitacao_id, limit=None):
        """Busca apenas comentários públicos (não internos)"""
        return self.get_all(
            where="ID_SOLICITACAO = ? AND INTERNO = FALSE",
            params=(solicitacao_id,),
            order_by="DTHR_CRIACAO DESC",
            limit=limit
        )
    
    def buscar_internos(self, solicitacao_id, limit=None):
        """Busca apenas comentários internos"""
        return self.get_all(
            where="ID_SOLICITACAO = ? AND INTERNO = TRUE",
            params=(solicitacao_id,),
            order_by="DTHR_CRIACAO DESC",
            limit=limit
        )
