#!/usr/bin/env python3
"""
Script para configurar as configurações de email corporativo no banco de dados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import db_connection

def configurar_email_corporativo():
    """Configura as configurações de email corporativo no banco"""
    
    print("🔧 Configurando email corporativo Medware...")
    
    # Configurações do servidor corporativo
    configs = {
        'EMAIL_SMTP_HOST': 'smtp.medware.com.br',
        'EMAIL_SMTP_PORT': '587',
        'EMAIL_SMTP_USER': 'medware@medware.com.br',
        'EMAIL_SMTP_PASS': 'Medware!111096',
        'EMAIL_FROM': 'demandas@medware.com.br',
        'EMAIL_ENABLE_SSL': 'false',
        'EMAIL_USE_DEFAULT_CREDENTIALS': 'false',
        'SISTEMA_NOME': 'SAOS - Sistema de Abertura de OS',
        'SISTEMA_URL': 'https://saos.medware.com.br'
    }
    
    try:
        with db_connection() as con:
            cur = con.cursor()
            
            for chave, valor in configs.items():
                # Verifica se a configuração já existe
                cur.execute("SELECT ID FROM CONFIGURACOES WHERE CHAVE = ?", (chave,))
                existing = cur.fetchone()
                
                if existing:
                    # Atualiza configuração existente
                    cur.execute("""
                        UPDATE CONFIGURACOES 
                        SET VALOR = ?, DTHR_ATUALIZACAO = CURRENT_TIMESTAMP 
                        WHERE CHAVE = ?
                    """, (valor.encode('utf-8'), chave))
                    print(f"   ✅ Atualizado: {chave} = {valor}")
                else:
                    # Insere nova configuração
                    cur.execute("""
                        INSERT INTO CONFIGURACOES (CHAVE, VALOR, DESCRICAO, TIPO, DTHR_CRIACAO, DTHR_ATUALIZACAO)
                        VALUES (?, ?, ?, 'TEXTO', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """, (
                        chave, 
                        valor.encode('utf-8'), 
                        f'Configuração de email corporativo - {chave}'.encode('utf-8')
                    ))
                    print(f"   ➕ Inserido: {chave} = {valor}")
            
            con.commit()
            print("\n🎉 Configurações de email corporativo configuradas com sucesso!")
            
            # Mostra as configurações atuais
            print("\n📋 Configurações atuais:")
            cur.execute("SELECT CHAVE, VALOR FROM CONFIGURACOES WHERE CHAVE LIKE 'EMAIL_%' OR CHAVE LIKE 'SISTEMA_%' ORDER BY CHAVE")
            for row in cur.fetchall():
                chave, valor = row
                if isinstance(valor, bytes):
                    valor = valor.decode('utf-8')
                print(f"   {chave}: {valor}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro ao configurar email: {str(e)}")
        return False

def testar_conexao_email():
    """Testa a conexão com o servidor de email"""
    
    print("\n🧪 Testando conexão com servidor de email...")
    
    try:
        from utils.email_service import EmailService
        email_service = EmailService()
        
        # Testa envio de email simples
        resultado = email_service.enviar_email(
            destinatario="teste@medware.com.br",
            assunto="Teste de Conexão - SAOS",
            corpo_html="<h1>Teste de Conexão</h1><p>Este é um teste de conexão com o servidor de email corporativo.</p>",
            corpo_texto="Teste de Conexão - Este é um teste de conexão com o servidor de email corporativo."
        )
        
        if resultado:
            print("✅ Conexão com servidor de email testada com sucesso!")
            return True
        else:
            print("❌ Falha na conexão com servidor de email")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar conexão: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Configurando sistema de email corporativo...")
    
    # Configura as configurações
    if configurar_email_corporativo():
        print("\n✅ Configurações salvas no banco de dados")
        
        # Testa a conexão
        if testar_conexao_email():
            print("\n🎉 Sistema de email configurado e testado com sucesso!")
        else:
            print("\n⚠️  Configurações salvas, mas teste de conexão falhou")
            print("   Verifique as credenciais e configurações do servidor")
    else:
        print("\n❌ Falha ao configurar email")
        sys.exit(1)
