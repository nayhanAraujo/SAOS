#!/usr/bin/env python3
"""
Script simples para testar a substituição de variáveis no template1.html
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.email_service import EmailService

def test_template_variables():
    """Testa a substituição de variáveis no template"""
    
    print("🧪 Testando substituição de variáveis no template1.html...")
    
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
        
        print("📝 Variáveis de teste:")
        for chave, valor in variaveis_teste.items():
            print(f"   {chave}: {valor}")
        
        # Gera o HTML do template
        print("\n🔄 Gerando HTML do template...")
        html_gerado = email_service.get_template1_html(variaveis_teste)
        
        # Verifica se as variáveis foram substituídas
        print("\n✅ Verificando substituição de variáveis...")
        todas_substituidas = True
        
        for chave, valor in variaveis_teste.items():
            if valor in html_gerado:
                print(f"   ✅ {chave}: '{valor}' - OK")
            else:
                print(f"   ❌ {chave}: '{valor}' - NÃO ENCONTRADO")
                todas_substituidas = False
        
        if todas_substituidas:
            print("\n🎉 Todas as variáveis foram substituídas corretamente!")
        else:
            print("\n⚠️  Algumas variáveis não foram substituídas corretamente")
            return False
        
        # Salva o HTML gerado para inspeção
        arquivo_saida = 'test_template_output.html'
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            f.write(html_gerado)
        
        print(f"\n📄 HTML gerado salvo em '{arquivo_saida}'")
        print(f"📏 Tamanho do arquivo: {len(html_gerado)} caracteres")
        
        # Verifica se o template tem a estrutura básica
        elementos_esperados = [
            'MEDWARE SISTEMAS MÉDICOS',
            'Solicitação Registrada',
            'Olá, Dr. João Silva',
            'OS20241201001',
            'Problema de Acesso',
            'Acompanhar Solicitação',
            'Falar no WhatsApp'
        ]
        
        print("\n🔍 Verificando estrutura do template...")
        for elemento in elementos_esperados:
            if elemento in html_gerado:
                print(f"   ✅ '{elemento}' - Encontrado")
            else:
                print(f"   ❌ '{elemento}' - NÃO ENCONTRADO")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar template: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Iniciando teste simples do template de email...")
    
    if test_template_variables():
        print("\n🎉 Teste concluído com sucesso!")
        print("📧 O template1.html está funcionando corretamente")
        print("\n💡 Para testar o envio real de email, execute:")
        print("   python scripts/test_email_template.py")
    else:
        print("\n❌ Teste falhou!")
        sys.exit(1)
