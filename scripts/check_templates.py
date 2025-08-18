#!/usr/bin/env python3
"""
Script para verificar templates de email no banco de dados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import db_connection

def verificar_templates():
    """Verifica se existem templates no banco de dados"""
    try:
        with db_connection() as con:
            cur = con.cursor()
            
            # Verificar se a tabela existe
            cur.execute("""
                SELECT COUNT(*) 
                FROM RDB$RELATIONS 
                WHERE RDB$RELATION_NAME = 'TEMPLATES_EMAIL'
            """)
            
            tabela_existe = cur.fetchone()[0] > 0
            print(f"🔍 Tabela TEMPLATES_EMAIL existe: {tabela_existe}")
            
            if not tabela_existe:
                print("❌ Tabela TEMPLATES_EMAIL não existe!")
                return
            
            # Contar templates
            cur.execute("SELECT COUNT(*) FROM TEMPLATES_EMAIL")
            total = cur.fetchone()[0]
            print(f"🔍 Total de templates: {total}")
            
            if total == 0:
                print("❌ Nenhum template encontrado!")
                return
            
            # Listar todos os templates
            cur.execute("""
                SELECT ID, NOME, ASSUNTO, ATIVO, DTHR_CRIACAO, DTHR_ATUALIZACAO
                FROM TEMPLATES_EMAIL 
                ORDER BY NOME
            """)
            
            templates = cur.fetchall()
            print(f"🔍 Templates encontrados:")
            
            for template in templates:
                print(f"  - ID: {template[0]}")
                print(f"    Nome: {template[1]}")
                print(f"    Assunto: {template[2]}")
                print(f"    Ativo: {template[3]}")
                print(f"    Criação: {template[4]}")
                print(f"    Atualização: {template[5]}")
                print()
            
    except Exception as e:
        print(f"❌ Erro ao verificar templates: {e}")

if __name__ == "__main__":
    print("🔍 Verificando templates de email no banco de dados...")
    verificar_templates()
