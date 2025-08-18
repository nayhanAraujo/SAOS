#!/usr/bin/env python3
"""
Script para verificar usuários no banco de dados
Execute: python scripts/check_users.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import db_connection
import hashlib

def hash_senha(senha):
    """Gera hash da senha"""
    return hashlib.sha256(senha.encode()).hexdigest()

def verificar_usuarios():
    """Verifica todos os usuários no banco"""
    print("🔍 Verificando usuários no banco de dados...")
    print("=" * 60)
    
    try:
        with db_connection() as con:
            cur = con.cursor()
            
            # Busca todos os usuários
            cur.execute("""
                SELECT ID, NOME, EMAIL, CPF_CNPJ, TIPO_USUARIO, ATIVO, SENHA, DTHR_CRIACAO
                FROM USUARIOS 
                ORDER BY ID
            """)
            
            usuarios = cur.fetchall()
            
            if not usuarios:
                print("❌ Nenhum usuário encontrado no banco!")
                return
            
            print(f"✅ Encontrados {len(usuarios)} usuário(s):")
            print()
            
            for usuario in usuarios:
                id_user, nome, email, cpf_cnpj, tipo, ativo, senha_hash, criacao = usuario
                
                print(f"👤 Usuário ID: {id_user}")
                print(f"   Nome: {nome}")
                print(f"   Email: {email}")
                print(f"   CPF/CNPJ: {cpf_cnpj}")
                print(f"   Tipo: {tipo}")
                print(f"   Ativo: {ativo}")
                print(f"   Criado em: {criacao}")
                
                if senha_hash:
                    print(f"   Senha (hash): {senha_hash[:20]}...")
                    
                    # Testa senha "123456"
                    senha_teste = "123456"
                    hash_teste = hash_senha(senha_teste)
                    senha_valida = (hash_teste == senha_hash)
                    
                    print(f"   Senha '123456' válida: {senha_valida}")
                    print(f"   Hash da senha '123456': {hash_teste[:20]}...")
                else:
                    print(f"   Senha: NÃO CADASTRADA")
                
                print("-" * 40)
            
            # Testa login específico
            print("\n🧪 Testando login específico...")
            email_teste = "nayhan@medware.com.br"
            senha_teste = "123456"
            
            print(f"Email: {email_teste}")
            print(f"Senha: {senha_teste}")
            
            # Busca usuário
            cur.execute("""
                SELECT ID, NOME, EMAIL, TIPO_USUARIO, ATIVO, SENHA
                FROM USUARIOS 
                WHERE EMAIL = ?
            """, (email_teste,))
            
            usuario_teste = cur.fetchone()
            
            if usuario_teste:
                id_user, nome, email, tipo, ativo, senha_hash = usuario_teste
                print(f"✅ Usuário encontrado: {nome}")
                print(f"   Tipo: {tipo}")
                print(f"   Ativo: {ativo}")
                
                if senha_hash:
                    hash_digitada = hash_senha(senha_teste)
                    senha_correta = (hash_digitada == senha_hash)
                    print(f"   Senha correta: {senha_correta}")
                    print(f"   Hash digitada: {hash_digitada[:20]}...")
                    print(f"   Hash banco: {senha_hash[:20]}...")
                else:
                    print("   Senha não cadastrada no banco")
            else:
                print(f"❌ Usuário {email_teste} não encontrado!")
            
    except Exception as e:
        print(f"❌ Erro ao verificar usuários: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_usuarios()
