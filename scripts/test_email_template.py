#!/usr/bin/env python3
"""
Script para testar o envio de email usando o template1.html
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.email_service import EmailService
from database.connection import db_connection
from datetime import datetime, timedelta

def test_email_template():
    """Testa o envio de email usando template1.html"""
    
    print("🧪 Testando envio de email com template1.html...")
    
    try:
        # Cria uma solicitação de teste
        with db_connection() as con:
            cur = con.cursor()
            
            # Busca um usuário de teste
            cur.execute("SELECT FIRST 1 ID, NOME, EMAIL FROM USUARIOS WHERE TIPO_USUARIO = 'CLIENTE'")
            usuario = cur.fetchone()
            
            if not usuario:
                print("❌ Nenhum usuário cliente encontrado no banco")
                return False
            
            usuario_id, nome_cliente, email_cliente = usuario
            
            # Cria uma solicitação de teste
            codigo_teste = f"TEST{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            cur.execute("""
                INSERT INTO SOLICITACOES (
                    CODIGO_REFERENCIA, TITULO, DESCRICAO, ID_CLIENTE, ID_CATEGORIA, 
                    ID_PRIORIDADE, ID_STATUS, SISTEMA, PRAZO_RESOLUCAO, 
                    DTHR_CRIACAO, DTHR_ATUALIZACAO
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (
                codigo_teste, 
                "Teste de Email Template1", 
                "Esta é uma solicitação de teste para verificar o template1.html".encode('utf-8'),
                usuario_id, 
                1,  # Categoria padrão
                2,  # Prioridade média
                1,  # Status aberto
                "Sistema de Teste",
                datetime.now() + timedelta(hours=72)  # Prazo de 72 horas
            ))
            
            # Busca o ID da solicitação criada
            cur.execute("SELECT ID FROM SOLICITACOES WHERE CODIGO_REFERENCIA = ?", (codigo_teste,))
            solicitacao_id = cur.fetchone()[0]
            
            con.commit()
            
            print(f"✅ Solicitação de teste criada: {codigo_teste} (ID: {solicitacao_id})")
            
            # Testa o envio de email
            email_service = EmailService()
            
            print(f"📧 Enviando email para: {email_cliente}")
            
            # Testa o método principal
            resultado = email_service.enviar_confirmacao_abertura(solicitacao_id)
            
            if resultado:
                print("✅ Email enviado com sucesso usando template1.html!")
                print(f"📧 Destinatário: {email_cliente}")
                print(f"📋 Código da solicitação: {codigo_teste}")
            else:
                print("❌ Falha ao enviar email")
                return False
            
            # Limpa a solicitação de teste
            cur.execute("DELETE FROM SOLICITACOES WHERE CODIGO_REFERENCIA = ?", (codigo_teste,))
            con.commit()
            
            print("🧹 Solicitação de teste removida")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        return False

def test_template_variables():
    """Testa a substituição de variáveis no template"""
    
    print("\n🧪 Testando substituição de variáveis...")
    
    try:
        email_service = EmailService()
        
        # Variáveis de teste
        variaveis_teste = {
            'nome_cliente': 'Dr. João Silva',
            'codigo_referencia': 'OS20241201001',
            'data_hora': '01/12/2024 - 14:30',
            'tipo_solicitacao': 'Problema de Acesso',
            'sistema': 'Sistema Principal',
            'prazo_estimado': '3 dias úteis',
            'link_acompanhamento': 'http://localhost:5001/acompanhar/OS20241201001'
        }
        
        # Gera o HTML do template
        html_gerado = email_service.get_template1_html(variaveis_teste)
        
        # Verifica se as variáveis foram substituídas
        for chave, valor in variaveis_teste.items():
            if valor not in html_gerado:
                print(f"❌ Variável '{chave}' não foi substituída corretamente")
                return False
        
        print("✅ Todas as variáveis foram substituídas corretamente")
        
        # Salva o HTML gerado para inspeção
        with open('test_template_output.html', 'w', encoding='utf-8') as f:
            f.write(html_gerado)
        
        print("📄 HTML gerado salvo em 'test_template_output.html'")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar variáveis: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando testes do template de email...")
    
    # Testa substituição de variáveis
    if test_template_variables():
        print("✅ Teste de variáveis passou")
    else:
        print("❌ Teste de variáveis falhou")
        sys.exit(1)
    
    # Testa envio de email
    if test_email_template():
        print("✅ Teste de envio passou")
    else:
        print("❌ Teste de envio falhou")
        sys.exit(1)
    
    print("\n🎉 Todos os testes passaram com sucesso!")
    print("📧 O template1.html está funcionando corretamente")
