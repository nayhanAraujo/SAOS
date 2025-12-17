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
            if row:
                columns = [description[0] for description in cur.description]
                return self._row_to_dict(row, columns)
            return None
    
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
            if rows:
                columns = [description[0] for description in cur.description]
                return [self._row_to_dict(row, columns) for row in rows]
            return []
    
    def create(self, data):
        """Cria um novo registro"""
        fields = list(data.keys())
        placeholders = ', '.join(['?' for _ in fields])
        field_names = ', '.join(fields)
        values = list(data.values())
        
        with db_connection() as con:
            cur = con.cursor()
            
            # Tenta usar RETURNING primeiro (Firebird 3.0+)
            try:
                query = f"INSERT INTO {self.table_name} ({field_names}) VALUES ({placeholders}) RETURNING {self.primary_key}"
                cur.execute(query, values)
                result = cur.fetchone()
                con.commit()
                if result and result[0] is not None:
                    return result[0]
                # Se RETURNING não retornou resultado, o INSERT já foi feito, então busca o ID
            except Exception as e:
                # Se RETURNING não funcionar, faz INSERT normal
                query = f"INSERT INTO {self.table_name} ({field_names}) VALUES ({placeholders})"
                cur.execute(query, values)
                con.commit()
            
            # Busca o ID usando os campos fornecidos (fallback ou quando RETURNING não retorna)
            where_clauses = []
            where_values = []
            
            # Usa os campos fornecidos para buscar o registro recém-criado
            for key, value in data.items():
                if value is not None:
                    where_clauses.append(f"{key} = ?")
                    where_values.append(value)
            
            if where_clauses:
                where_clause = " AND ".join(where_clauses)
                select_query = f"SELECT {self.primary_key} FROM {self.table_name} WHERE {where_clause} ORDER BY {self.primary_key} DESC"
                cur.execute(select_query, where_values)
                result = cur.fetchone()
                if result and result[0] is not None:
                    return result[0]
            
            # Se não conseguir obter o ID, retorna None
            return None
    
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
    
    def _row_to_dict(self, row, columns=None):
        """Converte uma linha do banco em dicionário"""
        if not row:
            return None
        
        # Se as colunas não foram fornecidas, obtém do banco (fallback)
        if columns is None:
            with db_connection() as con:
                cur = con.cursor()
                cur.execute(f"SELECT * FROM {self.table_name} WHERE 1=0")
                columns = [description[0] for description in cur.description]
        
        # Cria o dicionário
        result = {}
        for i, column in enumerate(columns):
            value = row[i]
            
            # Converte tipos especiais
            if value is None:
                result[column] = None
            elif isinstance(value, bytes):
                # Converte bytes para string (UTF-8)
                try:
                    value = value.decode('utf-8')
                except UnicodeDecodeError:
                    # Se não conseguir decodificar como UTF-8, tenta latin-1
                    try:
                        value = value.decode('latin-1')
                    except:
                        # Se falhar, converte para string hexadecimal
                        value = value.hex()
            elif isinstance(value, datetime):
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
