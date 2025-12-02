#!/usr/bin/env python3
"""
Script para adicionar os novos campos na tabela SOLICITACOES
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import db_connection

def adicionar_campos_solicitacoes():
    """Adiciona os novos campos na tabela SOLICITACOES"""
    
    print("🔧 Adicionando novos campos na tabela SOLICITACOES...")
    
    try:
        with db_connection() as con:
            cur = con.cursor()
            
            # Verifica se os campos já existem
            cur.execute("""
                SELECT RDB$FIELD_NAME 
                FROM RDB$RELATION_FIELDS 
                WHERE RDB$RELATION_NAME = 'SOLICITACOES'
            """)
            campos_existentes = [row[0].strip() for row in cur.fetchall()]
            
            print(f"Campos existentes: {campos_existentes}")
            
            # Adiciona campo TELEFONE_CLIENTE se não existir
            if 'TELEFONE_CLIENTE' not in campos_existentes:
                print("   ➕ Adicionando campo TELEFONE_CLIENTE...")
                cur.execute("""
                    ALTER TABLE SOLICITACOES 
                    ADD TELEFONE_CLIENTE VARCHAR(20)
                """)
                print("   ✅ Campo TELEFONE_CLIENTE adicionado")
            else:
                print("   ✅ Campo TELEFONE_CLIENTE já existe")
            
            # Adiciona campo EMAIL_CONTATO se não existir
            if 'EMAIL_CONTATO' not in campos_existentes:
                print("   ➕ Adicionando campo EMAIL_CONTATO...")
                cur.execute("""
                    ALTER TABLE SOLICITACOES 
                    ADD EMAIL_CONTATO VARCHAR(100)
                """)
                print("   ✅ Campo EMAIL_CONTATO adicionado")
            else:
                print("   ✅ Campo EMAIL_CONTATO já existe")
            
            # Adiciona campo RESPONSAVEL_TECNICO se não existir
            if 'RESPONSAVEL_TECNICO' not in campos_existentes:
                print("   ➕ Adicionando campo RESPONSAVEL_TECNICO...")
                cur.execute("""
                    ALTER TABLE SOLICITACOES 
                    ADD RESPONSAVEL_TECNICO VARCHAR(100)
                """)
                print("   ✅ Campo RESPONSAVEL_TECNICO adicionado")
            else:
                print("   ✅ Campo RESPONSAVEL_TECNICO já existe")
            
            con.commit()
            print("\n🎉 Campos adicionados com sucesso na tabela SOLICITACOES!")
            
            # Mostra a estrutura atual da tabela
            print("\n📋 Estrutura atual da tabela SOLICITACOES:")
            cur.execute("""
                SELECT RDB$FIELD_NAME, RDB$FIELD_TYPE, RDB$FIELD_LENGTH
                FROM RDB$RELATION_FIELDS rf
                JOIN RDB$FIELDS f ON rf.RDB$FIELD_SOURCE = f.RDB$FIELD_NAME
                WHERE rf.RDB$RELATION_NAME = 'SOLICITACOES'
                ORDER BY rf.RDB$FIELD_POSITION
            """)
            
            for row in cur.fetchall():
                nome_campo = row[0].strip()
                tipo_campo = row[1]
                tamanho = row[2]
                print(f"   {nome_campo}: Tipo {tipo_campo}, Tamanho {tamanho}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro ao adicionar campos: {str(e)}")
        return False

def criar_categoria_script():
    """Cria a categoria Script se não existir"""
    
    print("\n🔧 Verificando categoria Script...")
    
    try:
        with db_connection() as con:
            cur = con.cursor()
            
            # Verifica se a categoria já existe
            cur.execute("SELECT ID FROM CATEGORIAS WHERE NOME = 'Script'")
            categoria = cur.fetchone()
            
            if not categoria:
                print("   ➕ Criando categoria Script...")
                cur.execute("""
                    INSERT INTO CATEGORIAS (NOME, DESCRICAO, COR, ICONE, ATIVO, DTHR_CRIACAO, DTHR_ATUALIZACAO)
                    VALUES ('Script', ?, '#0056b3', 'fas fa-code', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, ('Solicitações de Script'.encode('utf-8'),))
                con.commit()
                print("   ✅ Categoria Script criada")
            else:
                print("   ✅ Categoria Script já existe")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro ao criar categoria: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Atualizando estrutura do banco de dados...")
    
    # Adiciona os novos campos
    if adicionar_campos_solicitacoes():
        print("\n✅ Campos adicionados com sucesso")
        
        # Cria a categoria Script
        if criar_categoria_script():
            print("\n✅ Categoria Script criada/verificada")
            print("\n🎉 Atualização do banco concluída com sucesso!")
        else:
            print("\n❌ Erro ao criar categoria Script")
    else:
        print("\n❌ Erro ao adicionar campos")
        sys.exit(1)
