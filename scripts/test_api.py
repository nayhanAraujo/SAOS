#!/usr/bin/env python3
"""
Script para testar a API de templates de email
"""

import requests
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def testar_api_templates():
    """Testa a API de templates"""
    base_url = "http://localhost:5001"
    
    print("🔍 Testando API de templates...")
    
    try:
        # Testar endpoint de listagem
        print("📡 Fazendo requisição GET /api/v1/templates-email...")
        response = requests.get(f"{base_url}/api/v1/templates-email")
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Resposta: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data.get('success'):
                templates = data.get('templates', [])
                print(f"✅ Encontrados {len(templates)} templates")
            else:
                print(f"❌ Erro na API: {data.get('message', 'Erro desconhecido')}")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"📄 Conteúdo: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão: Servidor não está rodando")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    testar_api_templates()
