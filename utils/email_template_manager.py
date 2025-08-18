#!/usr/bin/env python3
"""
Gerenciador de Templates de Email para o Sistema SAOS
Fornece funcionalidades completas para criação, edição e uso de templates de email
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from database.connection import db_connection
from utils.email_service import EmailService

class EmailTemplateManager:
    """Gerenciador de templates de email"""
    
    def __init__(self):
        self.email_service = EmailService()
    
    def listar_templates(self, ativos_apenas: bool = True) -> List[Dict]:
        """Lista todos os templates de email"""
        try:
            with db_connection() as con:
                cur = con.cursor()
                
                query = """
                    SELECT ID, NOME, ASSUNTO, ATIVO, DTHR_CRIACAO, DTHR_ATUALIZACAO
                    FROM TEMPLATES_EMAIL
                """
                
                if ativos_apenas:
                    query += " WHERE ATIVO = TRUE"
                
                query += " ORDER BY NOME"
                
                cur.execute(query)
                templates = []
                
                for row in cur.fetchall():
                    templates.append({
                        'id': row[0],
                        'nome': row[1],
                        'assunto': row[2],
                        'ativo': row[3],
                        'dthr_criacao': row[4],
                        'dthr_atualizacao': row[5]
                    })
                
                return templates
                
        except Exception as e:
            print(f"Erro ao listar templates: {e}")
            return []
    
    def obter_template(self, template_id: int) -> Optional[Dict]:
        """Obtém um template específico por ID"""
        try:
            with db_connection() as con:
                cur = con.cursor()
                cur.execute("""
                    SELECT ID, NOME, ASSUNTO, CORPO_HTML, CORPO_TEXTO, VARIAVEIS, ATIVO
                    FROM TEMPLATES_EMAIL
                    WHERE ID = ?
                """, (template_id,))
                
                row = cur.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'nome': row[1],
                        'assunto': row[2],
                        'corpo_html': row[3].decode('utf-8') if row[3] else '',
                        'corpo_texto': row[4].decode('utf-8') if row[4] else '',
                        'variaveis': json.loads(row[5]) if row[5] else [],
                        'ativo': row[6]
                    }
                return None
                
        except Exception as e:
            print(f"Erro ao obter template: {e}")
            return None
    
    def obter_template_por_nome(self, nome: str) -> Optional[Dict]:
        """Obtém um template específico por nome"""
        try:
            with db_connection() as con:
                cur = con.cursor()
                cur.execute("""
                    SELECT ID, NOME, ASSUNTO, CORPO_HTML, CORPO_TEXTO, VARIAVEIS, ATIVO
                    FROM TEMPLATES_EMAIL
                    WHERE NOME = ? AND ATIVO = TRUE
                """, (nome,))
                
                row = cur.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'nome': row[1],
                        'assunto': row[2],
                        'corpo_html': row[3].decode('utf-8') if row[3] else '',
                        'corpo_texto': row[4].decode('utf-8') if row[4] else '',
                        'variaveis': json.loads(row[5]) if row[5] else [],
                        'ativo': row[6]
                    }
                return None
                
        except Exception as e:
            print(f"Erro ao obter template por nome: {e}")
            return None
    
    def criar_template(self, dados: Dict) -> bool:
        """Cria um novo template de email"""
        try:
            with db_connection() as con:
                cur = con.cursor()
                cur.execute("""
                    INSERT INTO TEMPLATES_EMAIL (NOME, ASSUNTO, CORPO_HTML, CORPO_TEXTO, VARIAVEIS, ATIVO)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    dados['nome'],
                    dados['assunto'],
                    dados['corpo_html'].encode('utf-8'),
                    dados.get('corpo_texto', '').encode('utf-8'),
                    json.dumps(dados.get('variaveis', [])),
                    dados.get('ativo', True)
                ))
                con.commit()
                return True
                
        except Exception as e:
            print(f"Erro ao criar template: {e}")
            return False
    
    def atualizar_template(self, template_id: int, dados: Dict) -> bool:
        """Atualiza um template existente"""
        try:
            with db_connection() as con:
                cur = con.cursor()
                cur.execute("""
                    UPDATE TEMPLATES_EMAIL 
                    SET NOME = ?, ASSUNTO = ?, CORPO_HTML = ?, CORPO_TEXTO = ?, 
                        VARIAVEIS = ?, ATIVO = ?, DTHR_ATUALIZACAO = CURRENT_TIMESTAMP
                    WHERE ID = ?
                """, (
                    dados['nome'],
                    dados['assunto'],
                    dados['corpo_html'].encode('utf-8'),
                    dados.get('corpo_texto', '').encode('utf-8'),
                    json.dumps(dados.get('variaveis', [])),
                    dados.get('ativo', True),
                    template_id
                ))
                con.commit()
                return True
                
        except Exception as e:
            print(f"Erro ao atualizar template: {e}")
            return False
    
    def excluir_template(self, template_id: int) -> bool:
        """Exclui um template (soft delete)"""
        try:
            with db_connection() as con:
                cur = con.cursor()
                cur.execute("""
                    UPDATE TEMPLATES_EMAIL 
                    SET ATIVO = FALSE, DTHR_ATUALIZACAO = CURRENT_TIMESTAMP
                    WHERE ID = ?
                """, (template_id,))
                con.commit()
                return True
                
        except Exception as e:
            print(f"Erro ao excluir template: {e}")
            return False
    
    def ativar_desativar_template(self, template_id: int, ativo: bool) -> bool:
        """Ativa ou desativa um template"""
        try:
            with db_connection() as con:
                cur = con.cursor()
                cur.execute("""
                    UPDATE TEMPLATES_EMAIL 
                    SET ATIVO = ?, DTHR_ATUALIZACAO = CURRENT_TIMESTAMP
                    WHERE ID = ?
                """, (ativo, template_id))
                con.commit()
                return True
                
        except Exception as e:
            print(f"Erro ao alterar status do template: {e}")
            return False
    
    def extrair_variaveis_template(self, texto: str) -> List[str]:
        """Extrai variáveis do template usando regex"""
        if not texto:
            return []
        
        # Padrão para encontrar variáveis no formato {variavel}
        padrao = r'\{([^}]+)\}'
        variaveis = re.findall(padrao, texto)
        
        # Remove duplicatas e retorna lista única
        return list(set(variaveis))
    
    def validar_template(self, dados: Dict) -> Dict[str, Any]:
        """Valida um template antes de salvar"""
        erros = []
        avisos = []
        
        # Validações obrigatórias
        if not dados.get('nome'):
            erros.append("Nome do template é obrigatório")
        
        if not dados.get('assunto'):
            erros.append("Assunto do email é obrigatório")
        
        if not dados.get('corpo_html'):
            erros.append("Corpo HTML é obrigatório")
        
        # Validações de formato
        if dados.get('nome') and len(dados['nome']) > 100:
            erros.append("Nome do template deve ter no máximo 100 caracteres")
        
        if dados.get('assunto') and len(dados['assunto']) > 200:
            erros.append("Assunto deve ter no máximo 200 caracteres")
        
        # Extrair e validar variáveis
        variaveis_html = self.extrair_variaveis_template(dados.get('corpo_html', ''))
        variaveis_assunto = self.extrair_variaveis_template(dados.get('assunto', ''))
        variaveis_texto = self.extrair_variaveis_template(dados.get('corpo_texto', ''))
        
        todas_variaveis = set(variaveis_html + variaveis_assunto + variaveis_texto)
        
        # Verificar se há variáveis não documentadas
        variaveis_documentadas = set(dados.get('variaveis', []))
        variaveis_nao_documentadas = todas_variaveis - variaveis_documentadas
        
        if variaveis_nao_documentadas:
            avisos.append(f"Variáveis não documentadas: {', '.join(variaveis_nao_documentadas)}")
        
        # Verificar se há variáveis documentadas mas não usadas
        variaveis_nao_usadas = variaveis_documentadas - todas_variaveis
        if variaveis_nao_usadas:
            avisos.append(f"Variáveis documentadas mas não usadas: {', '.join(variaveis_nao_usadas)}")
        
        return {
            'valido': len(erros) == 0,
            'erros': erros,
            'avisos': avisos,
            'variaveis_encontradas': list(todas_variaveis)
        }
    
    def enviar_email_com_template(self, nome_template: str, destinatario: str, 
                                 variaveis: Dict[str, Any], anexos: List[str] = None) -> bool:
        """Envia email usando um template específico"""
        try:
            template = self.obter_template_por_nome(nome_template)
            if not template:
                print(f"Template '{nome_template}' não encontrado ou inativo")
                return False
            
            # Substituir variáveis no template
            assunto = self._substituir_variaveis(template['assunto'], variaveis)
            corpo_html = self._substituir_variaveis(template['corpo_html'], variaveis)
            corpo_texto = self._substituir_variaveis(template['corpo_texto'], variaveis)
            
            # Enviar email usando o serviço
            return self.email_service.enviar_email(destinatario, assunto, corpo_html, corpo_texto, anexos)
            
        except Exception as e:
            print(f"Erro ao enviar email com template: {e}")
            return False
    
    def _substituir_variaveis(self, texto: str, variaveis: Dict[str, Any]) -> str:
        """Substitui variáveis no texto do template"""
        if not texto:
            return texto
        
        for chave, valor in variaveis.items():
            placeholder = f"{{{chave}}}"
            texto = texto.replace(placeholder, str(valor))
        
        return texto
    
    def obter_templates_padrao(self) -> List[Dict]:
        """Retorna lista de templates padrão para criação"""
        return [
            {
                'nome': 'confirmacao_abertura',
                'assunto': 'Sua solicitação #{codigo_referencia} foi registrada com sucesso',
                'descricao': 'Email enviado quando uma nova solicitação é criada',
                'variaveis': [
                    'codigo_referencia', 'nome_cliente', 'titulo', 'categoria', 
                    'prioridade', 'prazo_estimado', 'descricao', 'link_acompanhamento'
                ]
            },
            {
                'nome': 'atualizacao_status',
                'assunto': 'Atualização da solicitação #{codigo_referencia}',
                'descricao': 'Email enviado quando o status da solicitação é alterado',
                'variaveis': [
                    'codigo_referencia', 'nome_cliente', 'novo_status', 'cor_status',
                    'responsavel', 'data_atualizacao', 'comentario', 'link_acompanhamento'
                ]
            },
            {
                'nome': 'solicitacao_informacoes',
                'assunto': 'Informações necessárias - Solicitação #{codigo_referencia}',
                'descricao': 'Email solicitando informações adicionais do cliente',
                'variaveis': [
                    'codigo_referencia', 'nome_cliente', 'titulo', 'responsavel',
                    'informacoes_necessarias', 'link_atualizacao'
                ]
            },
            {
                'nome': 'resolucao_concluida',
                'assunto': 'Sua solicitação #{codigo_referencia} foi resolvida',
                'descricao': 'Email enviado quando a solicitação é resolvida',
                'variaveis': [
                    'codigo_referencia', 'nome_cliente', 'titulo', 'solucao',
                    'responsavel', 'data_resolucao', 'tempo_resolucao', 'link_avaliacao'
                ]
            },
            {
                'nome': 'lembrete_prazo',
                'assunto': 'Lembrete: Prazo da solicitação #{codigo_referencia}',
                'descricao': 'Email de lembrete quando o prazo está próximo',
                'variaveis': [
                    'codigo_referencia', 'nome_cliente', 'titulo', 'prazo_limite',
                    'tempo_restante', 'responsavel', 'link_acompanhamento'
                ]
            },
            {
                'nome': 'escalacao_tecnico',
                'assunto': 'Nova solicitação atribuída: #{codigo_referencia}',
                'descricao': 'Email enviado para técnicos quando uma solicitação é atribuída',
                'variaveis': [
                    'codigo_referencia', 'nome_cliente', 'titulo', 'categoria',
                    'prioridade', 'descricao', 'prazo_limite', 'link_solicitacao'
                ]
            }
        ]
    
    def criar_template_padrao(self, nome_template: str) -> bool:
        """Cria um template padrão baseado no nome"""
        templates_padrao = {t['nome']: t for t in self.obter_templates_padrao()}
        
        if nome_template not in templates_padrao:
            return False
        
        template_info = templates_padrao[nome_template]
        
        # Gerar HTML padrão baseado no tipo de template
        corpo_html = self._gerar_html_padrao(nome_template, template_info['variaveis'])
        corpo_texto = self._gerar_texto_padrao(nome_template, template_info['variaveis'])
        
        dados = {
            'nome': template_info['nome'],
            'assunto': template_info['assunto'],
            'corpo_html': corpo_html,
            'corpo_texto': corpo_texto,
            'variaveis': template_info['variaveis'],
            'ativo': True
        }
        
        return self.criar_template(dados)
    
    def _gerar_html_padrao(self, nome_template: str, variaveis: List[str]) -> str:
        """Gera HTML padrão para o template"""
        if nome_template == 'confirmacao_abertura':
            return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Confirmação de Solicitação</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #3B82F6; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
            <h1 style="margin: 0;">SAOS - Sistema de Abertura de OS</h1>
        </div>
        
        <div style="background: #f9f9f9; padding: 20px; border-radius: 0 0 8px 8px;">
            <h2 style="color: #3B82F6;">Solicitação Registrada com Sucesso!</h2>
            
            <p>Olá <strong>{{nome_cliente}}</strong>,</p>
            
            <p>Sua solicitação foi registrada em nosso sistema com sucesso. Abaixo estão os detalhes:</p>
            
            <div style="background: white; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <p><strong>Código:</strong> {{codigo_referencia}}</p>
                <p><strong>Título:</strong> {{titulo}}</p>
                <p><strong>Categoria:</strong> {{categoria}}</p>
                <p><strong>Prioridade:</strong> <span style="color: #EF4444;">{{prioridade}}</span></p>
                <p><strong>Prazo Estimado:</strong> {{prazo_estimado}}</p>
            </div>
            
            <p><strong>Descrição:</strong></p>
            <div style="background: white; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <p>{{descricao}}</p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{{link_acompanhamento}}" style="background: #3B82F6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Acompanhar Solicitação
                </a>
            </div>
            
            <p style="font-size: 12px; color: #666; text-align: center;">
                Este é um email automático. Não responda a esta mensagem.
            </p>
        </div>
    </div>
</body>
</html>
            """
        
        # Adicionar outros templates conforme necessário
        return f"<p>Template HTML para {nome_template}</p>"
    
    def _gerar_texto_padrao(self, nome_template: str, variaveis: List[str]) -> str:
        """Gera texto plano padrão para o template"""
        if nome_template == 'confirmacao_abertura':
            return f"""
SAOS - Sistema de Abertura de OS

Solicitação Registrada com Sucesso!

Olá {{nome_cliente}},

Sua solicitação foi registrada em nosso sistema com sucesso.

Detalhes da Solicitação:
- Código: {{codigo_referencia}}
- Título: {{titulo}}
- Categoria: {{categoria}}
- Prioridade: {{prioridade}}
- Prazo Estimado: {{prazo_estimado}}

Descrição: {{descricao}}

Para acompanhar sua solicitação, acesse: {{link_acompanhamento}}

Este é um email automático. Não responda a esta mensagem.
            """
        
        return f"Template de texto para {nome_template}"
