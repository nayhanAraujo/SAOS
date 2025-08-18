from database.connection import db_connection
from datetime import datetime
import json

class BaseModel:
    """Classe base para todos os modelos do sistema"""
    
    def __init__(self):
        self.table_name = None
        self.primary_key = 'ID'
    
    def get_by_id(self, id):
        """Busca um registro pelo ID"""
        with db_connection() as con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM {self.table_name} WHERE {self.primary_key} = ?", (id,))
            row = cur.fetchone()
            return self._row_to_dict(row) if row else None
    
    def get_all(self, where=None, params=None, order_by=None, limit=None):
        """Busca todos os registros com filtros opcionais"""
        query = f"SELECT * FROM {self.table_name}"
        
        if where:
            query += f" WHERE {where}"
        
        if order_by:
            query += f" ORDER BY {order_by}"
        
        if limit:
            query += f" FIRST {limit}"
        
        with db_connection() as con:
            cur = con.cursor()
            cur.execute(query, params or ())
            rows = cur.fetchall()
            return [self._row_to_dict(row) for row in rows]
    
    def create(self, data):
        """Cria um novo registro"""
        fields = list(data.keys())
        placeholders = ', '.join(['?' for _ in fields])
        field_names = ', '.join(fields)
        
        query = f"INSERT INTO {self.table_name} ({field_names}) VALUES ({placeholders})"
        
        with db_connection() as con:
            cur = con.cursor()
            cur.execute(query, list(data.values()))
            con.commit()
            return cur.lastrowid
    
    def update(self, id, data):
        """Atualiza um registro existente"""
        fields = list(data.keys())
        set_clause = ', '.join([f"{field} = ?" for field in fields])
        
        query = f"UPDATE {self.table_name} SET {set_clause} WHERE {self.primary_key} = ?"
        
        with db_connection() as con:
            cur = con.cursor()
            values = list(data.values()) + [id]
            cur.execute(query, values)
            con.commit()
            return cur.rowcount > 0
    
    def delete(self, id):
        """Remove um registro"""
        query = f"DELETE FROM {self.table_name} WHERE {self.primary_key} = ?"
        
        with db_connection() as con:
            cur = con.cursor()
            cur.execute(query, (id,))
            con.commit()
            return cur.rowcount > 0
    
    def count(self, where=None, params=None):
        """Conta registros com filtro opcional"""
        query = f"SELECT COUNT(*) FROM {self.table_name}"
        
        if where:
            query += f" WHERE {where}"
        
        with db_connection() as con:
            cur = con.cursor()
            cur.execute(query, params or ())
            return cur.fetchone()[0]
    
    def _row_to_dict(self, row):
        """Converte uma linha do banco em dicionário"""
        if not row:
            return None
        
        # Obtém os nomes das colunas
        with db_connection() as con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM {self.table_name} WHERE 1=0")
            columns = [description[0] for description in cur.description]
        
        # Cria o dicionário
        result = {}
        for i, column in enumerate(columns):
            value = row[i]
            
            # Converte tipos especiais
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, str) and value and value.startswith('{'):
                try:
                    value = json.loads(value)
                except:
                    pass
            
            result[column] = value
        
        return result
    
    def _dict_to_row(self, data):
        """Converte um dicionário em valores para inserção/atualização"""
        result = {}
        for key, value in data.items():
            if isinstance(value, dict) or isinstance(value, list):
                result[key] = json.dumps(value)
            else:
                result[key] = value
        return result
