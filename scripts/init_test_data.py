#!/usr/bin/env python3
"""
Script para inicializar dados de teste no banco de dados SAOS
"""

import sys
import os
from datetime import datetime, timedelta

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import db_connection
from routes.auth import hash_senha

def inserir_dados_teste():
    """Insere dados de teste no banco de dados"""
    
    try:
        with db_connection() as con:
            cur = con.cursor()
            
            print("🔄 Inserindo dados de teste...")
            
            # 1. Inserir usuários de teste
            usuarios_teste = [
                ('João Silva', 'joao@empresa.com.br', hash_senha('123456'), 'CLIENTE', '12345678901', True),
                ('Maria Santos', 'maria@empresa.com.br', hash_senha('123456'), 'CLIENTE', '98765432100', True),
                ('Pedro Costa', 'pedro@medware.com.br', hash_senha('123456'), 'TECNICO', None, True),
                ('Ana Oliveira', 'ana@medware.com.br', hash_senha('123456'), 'TECNICO', None, True),
                ('Carlos Admin', 'admin@medware.com.br', hash_senha('123456'), 'ADMIN', None, True),
            ]
            
            for usuario in usuarios_teste:
                cur.execute("""
                    INSERT INTO USUARIOS (NOME, EMAIL, SENHA, TIPO, CPF_CNPJ, ATIVO, DTHR_CRIACAO)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, usuario)
            
            print("✅ Usuários de teste inseridos")
            
            # 2. Buscar IDs dos usuários inseridos
            cur.execute("SELECT ID, EMAIL FROM USUARIOS WHERE EMAIL IN (?, ?, ?, ?, ?)", 
                       ('joao@empresa.com.br', 'maria@empresa.com.br', 'pedro@medware.com.br', 'ana@medware.com.br', 'admin@medware.com.br'))
            usuarios = {row[1]: row[0] for row in cur.fetchall()}
            
            # 3. Inserir solicitações de teste
            solicitacoes_teste = [
                # Solicitações do João
                ('OS-2024-001', 'Problema no login do sistema', 'Não consigo fazer login no sistema principal'.encode('utf-8'), 
                 usuarios['joao@empresa.com.br'], 1, 2, 1, 'Sistema Principal', datetime.now() - timedelta(days=5)),
                
                ('OS-2024-002', 'Relatório não está gerando', 'O relatório de vendas não está sendo gerado corretamente'.encode('utf-8'), 
                 usuarios['joao@empresa.com.br'], 2, 1, 2, 'Sistema de Relatórios', datetime.now() - timedelta(days=3)),
                
                # Solicitações da Maria
                ('OS-2024-003', 'Erro na impressão', 'Documentos não estão sendo impressos'.encode('utf-8'), 
                 usuarios['maria@empresa.com.br'], 1, 3, 1, 'Sistema de Impressão', datetime.now() - timedelta(days=2)),
                
                ('OS-2024-004', 'Nova funcionalidade solicitada', 'Gostaria de uma nova tela para cadastro de produtos'.encode('utf-8'), 
                 usuarios['maria@empresa.com.br'], 2, 2, 1, 'Sistema de Cadastros', datetime.now() - timedelta(days=1)),
                
                # Solicitações urgentes
                ('OS-2024-005', 'Sistema fora do ar', 'Sistema completamente inacessível'.encode('utf-8'), 
                 usuarios['joao@empresa.com.br'], 1, 4, 1, 'Sistema Principal', datetime.now() - timedelta(hours=2)),
            ]
            
            for solicitacao in solicitacoes_teste:
                cur.execute("""
                    INSERT INTO SOLICITACOES (
                        CODIGO_REFERENCIA, TITULO, DESCRICAO, ID_CLIENTE, ID_CATEGORIA, 
                        ID_PRIORIDADE, ID_STATUS, SISTEMA, DTHR_CRIACAO, DTHR_ATUALIZACAO
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, solicitacao + (solicitacao[8],))  # DTHR_ATUALIZACAO = DTHR_CRIACAO
            
            print("✅ Solicitações de teste inseridas")
            
            # 4. Inserir histórico para as solicitações
            cur.execute("SELECT ID, CODIGO_REFERENCIA FROM SOLICITACOES WHERE CODIGO_REFERENCIA LIKE 'OS-2024-%'")
            solicitacoes_ids = cur.fetchall()
            
            for solicitacao_id, codigo in solicitacoes_ids:
                # Histórico de criação
                cur.execute("""
                    INSERT INTO HISTORICO (ID_SOLICITACAO, ID_USUARIO, TIPO_ACAO, DESCRICAO, DTHR_ACAO)
                    VALUES (?, ?, 'CRIACAO', ?, CURRENT_TIMESTAMP)
                """, (solicitacao_id, usuarios['joao@empresa.com.br'], 'Solicitação criada pelo cliente'.encode('utf-8')))
                
                # Histórico de análise (para algumas solicitações)
                if codigo in ['OS-2024-001', 'OS-2024-003']:
                    cur.execute("""
                        INSERT INTO HISTORICO (ID_SOLICITACAO, ID_USUARIO, TIPO_ACAO, DESCRICAO, DTHR_ACAO)
                        VALUES (?, ?, 'ANALISE', ?, CURRENT_TIMESTAMP)
                    """, (solicitacao_id, usuarios['pedro@medware.com.br'], 'Solicitação em análise técnica'.encode('utf-8')))
            
            print("✅ Histórico de solicitações inserido")
            
            con.commit()
            print("🎉 Dados de teste inseridos com sucesso!")
            
            # Mostrar resumo
            print("\n📊 Resumo dos dados inseridos:")
            print(f"   • {len(usuarios_teste)} usuários")
            print(f"   • {len(solicitacoes_teste)} solicitações")
            print(f"   • Histórico para todas as solicitações")
            
            print("\n👥 Usuários criados:")
            for email, user_id in usuarios.items():
                print(f"   • {email} (ID: {user_id})")
            
            print("\n🔑 Senhas padrão: 123456")
            
    except Exception as e:
        print(f"❌ Erro ao inserir dados de teste: {e}")
        raise

if __name__ == "__main__":
    print("🚀 Iniciando inserção de dados de teste...")
    inserir_dados_teste()
    print("✅ Concluído!")
