#!/usr/bin/env python3
"""
Exemplos práticos de uso dos Templates de Email no Sistema SAOS
Demonstra como integrar os templates em diferentes cenários do sistema
"""

from utils.email_template_manager import EmailTemplateManager
from utils.email_service import EmailService
from database.connection import db_connection
import json

class EmailTemplatesExamples:
    """Exemplos de uso dos templates de email"""
    
    def __init__(self):
        self.template_manager = EmailTemplateManager()
        self.email_service = EmailService()
    
    def exemplo_confirmacao_abertura(self, solicitacao_id):
        """
        Exemplo 1: Enviar email de confirmação quando uma nova solicitação é criada
        """
        print("📧 Exemplo 1: Email de Confirmação de Abertura")
        
        # Buscar dados da solicitação
        solicitacao = self._get_solicitacao_completa(solicitacao_id)
        if not solicitacao:
            print("❌ Solicitação não encontrada")
            return False
        
        # Preparar variáveis para o template
        variaveis = {
            'codigo_referencia': solicitacao['CODIGO_REFERENCIA'],
            'nome_cliente': solicitacao['NOME_CLIENTE'],
            'titulo': solicitacao['TITULO'],
            'categoria': solicitacao['NOME_CATEGORIA'],
            'prioridade': solicitacao['NOME_PRIORIDADE'],
            'prazo_estimado': self._formatar_prazo(solicitacao['PRAZO_RESOLUCAO']),
            'descricao': solicitacao['DESCRICAO'],
            'link_acompanhamento': f"http://localhost:5001/acompanhar/{solicitacao['CODIGO_REFERENCIA']}"
        }
        
        # Enviar email usando template
        sucesso = self.template_manager.enviar_email_com_template(
            nome_template='confirmacao_abertura',
            destinatario=solicitacao['EMAIL_CLIENTE'],
            variaveis=variaveis
        )
        
        if sucesso:
            print(f"✅ Email enviado para {solicitacao['EMAIL_CLIENTE']}")
            return True
        else:
            print("❌ Erro ao enviar email")
            return False
    
    def exemplo_atualizacao_status(self, solicitacao_id, novo_status_id, comentario=None):
        """
        Exemplo 2: Enviar email quando o status da solicitação é alterado
        """
        print("📧 Exemplo 2: Email de Atualização de Status")
        
        # Buscar dados da solicitação
        solicitacao = self._get_solicitacao_completa(solicitacao_id)
        if not solicitacao:
            print("❌ Solicitação não encontrada")
            return False
        
        # Buscar dados do novo status
        novo_status = self._get_status(novo_status_id)
        if not novo_status:
            print("❌ Status não encontrado")
            return False
        
        # Buscar dados do técnico responsável
        tecnico = self._get_usuario(solicitacao['ID_TECNICO_RESPONSAVEL'])
        
        # Preparar variáveis para o template
        variaveis = {
            'codigo_referencia': solicitacao['CODIGO_REFERENCIA'],
            'nome_cliente': solicitacao['NOME_CLIENTE'],
            'novo_status': novo_status['NOME'],
            'cor_status': novo_status['COR'],
            'responsavel': tecnico['NOME'] if tecnico else 'Sistema',
            'data_atualizacao': self._formatar_data_atual(),
            'comentario': comentario or 'Nenhum comentário adicional',
            'link_acompanhamento': f"http://localhost:5001/acompanhar/{solicitacao['CODIGO_REFERENCIA']}"
        }
        
        # Enviar email usando template
        sucesso = self.template_manager.enviar_email_com_template(
            nome_template='atualizacao_status',
            destinatario=solicitacao['EMAIL_CLIENTE'],
            variaveis=variaveis
        )
        
        if sucesso:
            print(f"✅ Email de atualização enviado para {solicitacao['EMAIL_CLIENTE']}")
            return True
        else:
            print("❌ Erro ao enviar email de atualização")
            return False
    
    def exemplo_solicitacao_informacoes(self, solicitacao_id, informacoes_necessarias):
        """
        Exemplo 3: Enviar email solicitando informações adicionais do cliente
        """
        print("📧 Exemplo 3: Email Solicitando Informações")
        
        # Buscar dados da solicitação
        solicitacao = self._get_solicitacao_completa(solicitacao_id)
        if not solicitacao:
            print("❌ Solicitação não encontrada")
            return False
        
        # Buscar dados do técnico responsável
        tecnico = self._get_usuario(solicitacao['ID_TECNICO_RESPONSAVEL'])
        
        # Preparar variáveis para o template
        variaveis = {
            'codigo_referencia': solicitacao['CODIGO_REFERENCIA'],
            'nome_cliente': solicitacao['NOME_CLIENTE'],
            'titulo': solicitacao['TITULO'],
            'responsavel': tecnico['NOME'] if tecnico else 'Sistema',
            'informacoes_necessarias': informacoes_necessarias,
            'link_atualizacao': f"http://localhost:5001/atualizar/{solicitacao['CODIGO_REFERENCIA']}"
        }
        
        # Enviar email usando template
        sucesso = self.template_manager.enviar_email_com_template(
            nome_template='solicitacao_informacoes',
            destinatario=solicitacao['EMAIL_CLIENTE'],
            variaveis=variaveis
        )
        
        if sucesso:
            print(f"✅ Email solicitando informações enviado para {solicitacao['EMAIL_CLIENTE']}")
            return True
        else:
            print("❌ Erro ao enviar email solicitando informações")
            return False
    
    def exemplo_resolucao_concluida(self, solicitacao_id, solucao):
        """
        Exemplo 4: Enviar email quando a solicitação é resolvida
        """
        print("📧 Exemplo 4: Email de Resolução Concluída")
        
        # Buscar dados da solicitação
        solicitacao = self._get_solicitacao_completa(solicitacao_id)
        if not solicitacao:
            print("❌ Solicitação não encontrada")
            return False
        
        # Buscar dados do técnico responsável
        tecnico = self._get_usuario(solicitacao['ID_TECNICO_RESPONSAVEL'])
        
        # Calcular tempo de resolução
        tempo_resolucao = self._calcular_tempo_resolucao(
            solicitacao['DTHR_CRIACAO'], 
            solicitacao['DTHR_RESOLUCAO']
        )
        
        # Preparar variáveis para o template
        variaveis = {
            'codigo_referencia': solicitacao['CODIGO_REFERENCIA'],
            'nome_cliente': solicitacao['NOME_CLIENTE'],
            'titulo': solicitacao['TITULO'],
            'solucao': solucao,
            'responsavel': tecnico['NOME'] if tecnico else 'Sistema',
            'data_resolucao': self._formatar_data(solicitacao['DTHR_RESOLUCAO']),
            'tempo_resolucao': tempo_resolucao,
            'link_avaliacao': f"http://localhost:5001/avaliar/{solicitacao['CODIGO_REFERENCIA']}"
        }
        
        # Enviar email usando template
        sucesso = self.template_manager.enviar_email_com_template(
            nome_template='resolucao_concluida',
            destinatario=solicitacao['EMAIL_CLIENTE'],
            variaveis=variaveis
        )
        
        if sucesso:
            print(f"✅ Email de resolução enviado para {solicitacao['EMAIL_CLIENTE']}")
            return True
        else:
            print("❌ Erro ao enviar email de resolução")
            return False
    
    def exemplo_lembrete_prazo(self, solicitacao_id):
        """
        Exemplo 5: Enviar email de lembrete quando o prazo está próximo
        """
        print("📧 Exemplo 5: Email de Lembrete de Prazo")
        
        # Buscar dados da solicitação
        solicitacao = self._get_solicitacao_completa(solicitacao_id)
        if not solicitacao:
            print("❌ Solicitação não encontrada")
            return False
        
        # Buscar dados do técnico responsável
        tecnico = self._get_usuario(solicitacao['ID_TECNICO_RESPONSAVEL'])
        
        # Calcular tempo restante
        tempo_restante = self._calcular_tempo_restante(solicitacao['PRAZO_RESOLUCAO'])
        
        # Preparar variáveis para o template
        variaveis = {
            'codigo_referencia': solicitacao['CODIGO_REFERENCIA'],
            'nome_cliente': solicitacao['NOME_CLIENTE'],
            'titulo': solicitacao['TITULO'],
            'prazo_limite': self._formatar_prazo(solicitacao['PRAZO_RESOLUCAO']),
            'tempo_restante': tempo_restante,
            'responsavel': tecnico['NOME'] if tecnico else 'Sistema',
            'link_acompanhamento': f"http://localhost:5001/acompanhar/{solicitacao['CODIGO_REFERENCIA']}"
        }
        
        # Enviar email usando template
        sucesso = self.template_manager.enviar_email_com_template(
            nome_template='lembrete_prazo',
            destinatario=solicitacao['EMAIL_CLIENTE'],
            variaveis=variaveis
        )
        
        if sucesso:
            print(f"✅ Email de lembrete enviado para {solicitacao['EMAIL_CLIENTE']}")
            return True
        else:
            print("❌ Erro ao enviar email de lembrete")
            return False
    
    def exemplo_escalacao_tecnico(self, solicitacao_id, tecnico_id):
        """
        Exemplo 6: Enviar email para técnico quando uma solicitação é atribuída
        """
        print("📧 Exemplo 6: Email de Escalação para Técnico")
        
        # Buscar dados da solicitação
        solicitacao = self._get_solicitacao_completa(solicitacao_id)
        if not solicitacao:
            print("❌ Solicitação não encontrada")
            return False
        
        # Buscar dados do técnico
        tecnico = self._get_usuario(tecnico_id)
        if not tecnico:
            print("❌ Técnico não encontrado")
            return False
        
        # Preparar variáveis para o template
        variaveis = {
            'codigo_referencia': solicitacao['CODIGO_REFERENCIA'],
            'nome_cliente': solicitacao['NOME_CLIENTE'],
            'titulo': solicitacao['TITULO'],
            'categoria': solicitacao['NOME_CATEGORIA'],
            'prioridade': solicitacao['NOME_PRIORIDADE'],
            'descricao': solicitacao['DESCRICAO'],
            'prazo_limite': self._formatar_prazo(solicitacao['PRAZO_RESOLUCAO']),
            'link_solicitacao': f"http://localhost:5001/solicitacao/{solicitacao['ID']}"
        }
        
        # Enviar email usando template
        sucesso = self.template_manager.enviar_email_com_template(
            nome_template='escalacao_tecnico',
            destinatario=tecnico['EMAIL'],
            variaveis=variaveis
        )
        
        if sucesso:
            print(f"✅ Email de escalação enviado para {tecnico['EMAIL']}")
            return True
        else:
            print("❌ Erro ao enviar email de escalação")
            return False
    
    def exemplo_criar_template_personalizado(self):
        """
        Exemplo 7: Criar um template personalizado programaticamente
        """
        print("📧 Exemplo 7: Criando Template Personalizado")
        
        # Dados do template personalizado
        dados_template = {
            'nome': 'boas_vindas_cliente',
            'assunto': 'Bem-vindo ao SAOS - {nome_cliente}',
            'corpo_html': """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Bem-vindo ao SAOS</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #3B82F6; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
            <h1 style="margin: 0;">SAOS - Sistema de Abertura de OS</h1>
        </div>
        
        <div style="background: #f9f9f9; padding: 20px; border-radius: 0 0 8px 8px;">
            <h2 style="color: #3B82F6;">Bem-vindo, {nome_cliente}!</h2>
            
            <p>Seja bem-vindo ao nosso sistema de suporte técnico.</p>
            
            <p>A partir de agora você pode:</p>
            <ul>
                <li>Abrir solicitações de suporte</li>
                <li>Acompanhar o status das suas solicitações</li>
                <li>Receber atualizações por email</li>
                <li>Avaliar nossos serviços</li>
            </ul>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{link_dashboard}" style="background: #3B82F6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Acessar Dashboard
                </a>
            </div>
            
            <p style="font-size: 12px; color: #666; text-align: center;">
                Este é um email automático. Não responda a esta mensagem.
            </p>
        </div>
    </div>
</body>
</html>
            """,
            'corpo_texto': """
SAOS - Sistema de Abertura de OS

Bem-vindo, {nome_cliente}!

Seja bem-vindo ao nosso sistema de suporte técnico.

A partir de agora você pode:
- Abrir solicitações de suporte
- Acompanhar o status das suas solicitações
- Receber atualizações por email
- Avaliar nossos serviços

Acesse seu dashboard: {link_dashboard}

Este é um email automático. Não responda a esta mensagem.
            """,
            'variaveis': ['nome_cliente', 'link_dashboard'],
            'ativo': True
        }
        
        # Criar o template
        sucesso = self.template_manager.criar_template(dados_template)
        
        if sucesso:
            print("✅ Template personalizado criado com sucesso")
            return True
        else:
            print("❌ Erro ao criar template personalizado")
            return False
    
    def exemplo_uso_template_personalizado(self, email_cliente, nome_cliente):
        """
        Exemplo 8: Usar o template personalizado criado
        """
        print("📧 Exemplo 8: Usando Template Personalizado")
        
        # Preparar variáveis
        variaveis = {
            'nome_cliente': nome_cliente,
            'link_dashboard': f"http://localhost:5001/dashboard"
        }
        
        # Enviar email usando template personalizado
        sucesso = self.template_manager.enviar_email_com_template(
            nome_template='boas_vindas_cliente',
            destinatario=email_cliente,
            variaveis=variaveis
        )
        
        if sucesso:
            print(f"✅ Email de boas-vindas enviado para {email_cliente}")
            return True
        else:
            print("❌ Erro ao enviar email de boas-vindas")
            return False
    
    # Métodos auxiliares
    def _get_solicitacao_completa(self, solicitacao_id):
        """Obtém dados completos de uma solicitação"""
        try:
            with db_connection() as con:
                cur = con.cursor()
                cur.execute("""
                    SELECT 
                        s.*,
                        c.NOME as NOME_CLIENTE,
                        c.EMAIL as EMAIL_CLIENTE,
                        cat.NOME as NOME_CATEGORIA,
                        p.NOME as NOME_PRIORIDADE,
                        st.NOME as NOME_STATUS
                    FROM SOLICITACOES s
                    JOIN USUARIOS c ON s.ID_CLIENTE = c.ID
                    JOIN CATEGORIAS cat ON s.ID_CATEGORIA = cat.ID
                    JOIN PRIORIDADES p ON s.ID_PRIORIDADE = p.ID
                    JOIN STATUS st ON s.ID_STATUS = st.ID
                    WHERE s.ID = ?
                """, (solicitacao_id,))
                
                row = cur.fetchone()
                if row:
                    columns = [description[0] for description in cur.description]
                    return dict(zip(columns, row))
                return None
                
        except Exception as e:
            print(f"Erro ao buscar solicitação: {e}")
            return None
    
    def _get_status(self, status_id):
        """Obtém dados de um status"""
        try:
            with db_connection() as con:
                cur = con.cursor()
                cur.execute("SELECT * FROM STATUS WHERE ID = ?", (status_id,))
                row = cur.fetchone()
                if row:
                    columns = [description[0] for description in cur.description]
                    return dict(zip(columns, row))
                return None
                
        except Exception as e:
            print(f"Erro ao buscar status: {e}")
            return None
    
    def _get_usuario(self, usuario_id):
        """Obtém dados de um usuário"""
        if not usuario_id:
            return None
            
        try:
            with db_connection() as con:
                cur = con.cursor()
                cur.execute("SELECT * FROM USUARIOS WHERE ID = ?", (usuario_id,))
                row = cur.fetchone()
                if row:
                    columns = [description[0] for description in cur.description]
                    return dict(zip(columns, row))
                return None
                
        except Exception as e:
            print(f"Erro ao buscar usuário: {e}")
            return None
    
    def _formatar_prazo(self, prazo):
        """Formata o prazo para exibição"""
        if not prazo:
            return "Não definido"
        
        from datetime import datetime
        if isinstance(prazo, str):
            prazo = datetime.fromisoformat(prazo)
        
        return prazo.strftime('%d/%m/%Y às %H:%M')
    
    def _formatar_data(self, data):
        """Formata uma data para exibição"""
        if not data:
            return "N/A"
        
        from datetime import datetime
        if isinstance(data, str):
            data = datetime.fromisoformat(data)
        
        return data.strftime('%d/%m/%Y %H:%M')
    
    def _formatar_data_atual(self):
        """Retorna a data atual formatada"""
        from datetime import datetime
        return datetime.now().strftime('%d/%m/%Y %H:%M')
    
    def _calcular_tempo_resolucao(self, criacao, resolucao):
        """Calcula o tempo de resolução"""
        if not criacao or not resolucao:
            return "Não disponível"
        
        from datetime import datetime
        if isinstance(criacao, str):
            criacao = datetime.fromisoformat(criacao)
        if isinstance(resolucao, str):
            resolucao = datetime.fromisoformat(resolucao)
        
        diferenca = resolucao - criacao
        dias = diferenca.days
        horas = diferenca.seconds // 3600
        
        if dias > 0:
            return f"{dias} dia(s) e {horas} hora(s)"
        else:
            return f"{horas} hora(s)"
    
    def _calcular_tempo_restante(self, prazo):
        """Calcula o tempo restante até o prazo"""
        if not prazo:
            return "Prazo não definido"
        
        from datetime import datetime
        if isinstance(prazo, str):
            prazo = datetime.fromisoformat(prazo)
        
        agora = datetime.now()
        diferenca = prazo - agora
        
        if diferenca.total_seconds() < 0:
            return "Prazo expirado"
        
        dias = diferenca.days
        horas = diferenca.seconds // 3600
        
        if dias > 0:
            return f"{dias} dia(s) e {horas} hora(s)"
        else:
            return f"{horas} hora(s)"


# Exemplo de uso
if __name__ == "__main__":
    print("🚀 Exemplos de Uso dos Templates de Email - SAOS")
    print("=" * 60)
    
    examples = EmailTemplatesExamples()
    
    # Exemplo 1: Criar template personalizado
    print("\n1. Criando template personalizado...")
    examples.exemplo_criar_template_personalizado()
    
    # Exemplo 2: Usar template personalizado
    print("\n2. Usando template personalizado...")
    examples.exemplo_uso_template_personalizado(
        email_cliente="cliente@exemplo.com",
        nome_cliente="João Silva"
    )
    
    print("\n✅ Exemplos concluídos!")
    print("\n💡 Para usar em produção:")
    print("1. Configure as credenciais de email no banco de dados")
    print("2. Crie os templates necessários via interface administrativa")
    print("3. Integre as chamadas nos pontos apropriados do sistema")
    print("4. Monitore os logs de envio de emails")
