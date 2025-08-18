import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import json
from datetime import datetime
from database.connection import db_connection
from models.base import BaseModel

class EmailService:
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self):
        """Carrega configurações de email do banco"""
        with db_connection() as con:
            cur = con.cursor()
            cur.execute("SELECT CHAVE, VALOR FROM CONFIGURACOES WHERE CHAVE LIKE 'EMAIL_%'")
            config = dict(cur.fetchall())
        
        return {
            'smtp_host': config.get('EMAIL_SMTP_HOST', 'smtp.office365.com'),
            'smtp_port': int(config.get('EMAIL_SMTP_PORT', '587')),
            'smtp_user': config.get('EMAIL_SMTP_USER', 'suporte@empresa.com.br'),
            'smtp_pass': config.get('EMAIL_SMTP_PASS', ''),
            'from_email': config.get('EMAIL_FROM', 'suporte@empresa.com.br'),
            'from_name': config.get('SISTEMA_NOME', 'SAOS - Sistema de Abertura de OS')
        }
    
    def get_template(self, nome_template):
        """Obtém um template de email do banco"""
        with db_connection() as con:
            cur = con.cursor()
            cur.execute("""
                SELECT ASSUNTO, CORPO_HTML, CORPO_TEXTO, VARIAVEIS 
                FROM TEMPLATES_EMAIL 
                WHERE NOME = ? AND ATIVO = TRUE
            """, (nome_template,))
            result = cur.fetchone()
            
            if result:
                return {
                    'assunto': result[0],
                    'corpo_html': result[1],
                    'corpo_texto': result[2],
                    'variaveis': json.loads(result[3]) if result[3] else []
                }
            return None
    
    def enviar_template(self, nome_template, destinatario, variaveis, anexos=None):
        """Envia email usando um template"""
        template = self.get_template(nome_template)
        if not template:
            raise ValueError(f"Template '{nome_template}' não encontrado")
        
        # Substitui variáveis no template
        assunto = self._substituir_variaveis(template['assunto'], variaveis)
        corpo_html = self._substituir_variaveis(template['corpo_html'], variaveis)
        corpo_texto = self._substituir_variaveis(template['corpo_texto'], variaveis)
        
        return self.enviar_email(destinatario, assunto, corpo_html, corpo_texto, anexos)
    
    def enviar_confirmacao_abertura(self, solicitacao_id):
        """Envia email de confirmação de abertura"""
        solicitacao = self._get_solicitacao_completa(solicitacao_id)
        if not solicitacao:
            return False
        
        variaveis = {
            'codigo_referencia': solicitacao['CODIGO_REFERENCIA'],
            'nome_cliente': solicitacao['NOME_CLIENTE'],
            'titulo': solicitacao['TITULO'],
            'categoria': solicitacao['NOME_CATEGORIA'],
            'prioridade': solicitacao['NOME_PRIORIDADE'],
            'prioridade_classe': self._get_classe_prioridade(solicitacao['ID_PRIORIDADE']),
            'prazo_estimado': self._formatar_prazo(solicitacao['PRAZO_RESOLUCAO']),
            'descricao': solicitacao['DESCRICAO'],
            'link_acompanhamento': self._gerar_link_acompanhamento(solicitacao['CODIGO_REFERENCIA'])
        }
        
        return self.enviar_template('confirmacao_abertura', solicitacao['EMAIL_CLIENTE'], variaveis)
    
    def enviar_atualizacao_status(self, solicitacao_id, novo_status_id, comentario=None):
        """Envia email de atualização de status"""
        solicitacao = self._get_solicitacao_completa(solicitacao_id)
        if not solicitacao:
            return False
        
        novo_status = self._get_status(novo_status_id)
        tecnico = self._get_usuario(solicitacao['ID_TECNICO_RESPONSAVEL'])
        
        variaveis = {
            'codigo_referencia': solicitacao['CODIGO_REFERENCIA'],
            'nome_cliente': solicitacao['NOME_CLIENTE'],
            'novo_status': novo_status['NOME'],
            'cor_status': novo_status['COR'],
            'responsavel': tecnico['NOME'] if tecnico else 'Sistema',
            'data_atualizacao': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'comentario': comentario or 'Nenhum comentário adicional',
            'link_acompanhamento': self._gerar_link_acompanhamento(solicitacao['CODIGO_REFERENCIA'])
        }
        
        return self.enviar_template('atualizacao_status', solicitacao['EMAIL_CLIENTE'], variaveis)
    
    def enviar_solicitacao_informacoes(self, solicitacao_id, informacoes_necessarias):
        """Envia email solicitando informações adicionais"""
        solicitacao = self._get_solicitacao_completa(solicitacao_id)
        if not solicitacao:
            return False
        
        tecnico = self._get_usuario(solicitacao['ID_TECNICO_RESPONSAVEL'])
        
        variaveis = {
            'codigo_referencia': solicitacao['CODIGO_REFERENCIA'],
            'nome_cliente': solicitacao['NOME_CLIENTE'],
            'titulo': solicitacao['TITULO'],
            'responsavel': tecnico['NOME'] if tecnico else 'Sistema',
            'informacoes_necessarias': informacoes_necessarias,
            'link_atualizacao': self._gerar_link_atualizacao(solicitacao['CODIGO_REFERENCIA'])
        }
        
        return self.enviar_template('solicitacao_informacoes', solicitacao['EMAIL_CLIENTE'], variaveis)
    
    def enviar_resolucao_concluida(self, solicitacao_id, solucao):
        """Envia email de resolução concluída"""
        solicitacao = self._get_solicitacao_completa(solicitacao_id)
        if not solicitacao:
            return False
        
        tecnico = self._get_usuario(solicitacao['ID_TECNICO_RESPONSAVEL'])
        tempo_resolucao = self._calcular_tempo_resolucao(solicitacao['DTHR_CRIACAO'], solicitacao['DTHR_RESOLUCAO'])
        
        variaveis = {
            'codigo_referencia': solicitacao['CODIGO_REFERENCIA'],
            'nome_cliente': solicitacao['NOME_CLIENTE'],
            'titulo': solicitacao['TITULO'],
            'solucao': solucao,
            'responsavel': tecnico['NOME'] if tecnico else 'Sistema',
            'data_resolucao': solicitacao['DTHR_RESOLUCAO'].strftime('%d/%m/%Y %H:%M') if solicitacao['DTHR_RESOLUCAO'] else 'N/A',
            'tempo_resolucao': tempo_resolucao,
            'link_avaliacao': self._gerar_link_avaliacao(solicitacao['CODIGO_REFERENCIA'])
        }
        
        return self.enviar_template('resolucao_concluida', solicitacao['EMAIL_CLIENTE'], variaveis)
    
    def enviar_email(self, destinatario, assunto, corpo_html, corpo_texto=None, anexos=None):
        """Envia email genérico"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = assunto
            msg['From'] = f"{self.config['from_name']} <{self.config['from_email']}>"
            msg['To'] = destinatario
            
            # Corpo do email
            if corpo_html:
                msg.attach(MIMEText(corpo_html, 'html', 'utf-8'))
            
            if corpo_texto:
                msg.attach(MIMEText(corpo_texto, 'plain', 'utf-8'))
            
            # Anexos
            if anexos:
                for anexo in anexos:
                    if os.path.exists(anexo):
                        with open(anexo, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                        
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(anexo))
                        msg.attach(part)
            
            # Envia o email
            with smtplib.SMTP(self.config['smtp_host'], self.config['smtp_port']) as server:
                server.starttls()
                server.login(self.config['smtp_user'], self.config['smtp_pass'])
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Erro ao enviar email: {str(e)}")
            return False
    
    def _substituir_variaveis(self, texto, variaveis):
        """Substitui variáveis no texto do template"""
        if not texto:
            return texto
        
        for chave, valor in variaveis.items():
            placeholder = f"{{{chave}}}"
            texto = texto.replace(placeholder, str(valor))
        
        return texto
    
    def _get_solicitacao_completa(self, solicitacao_id):
        """Obtém dados completos de uma solicitação"""
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
    
    def _get_status(self, status_id):
        """Obtém dados de um status"""
        with db_connection() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM STATUS WHERE ID = ?", (status_id,))
            row = cur.fetchone()
            if row:
                columns = [description[0] for description in cur.description]
                return dict(zip(columns, row))
            return None
    
    def _get_usuario(self, usuario_id):
        """Obtém dados de um usuário"""
        if not usuario_id:
            return None
            
        with db_connection() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM USUARIOS WHERE ID = ?", (usuario_id,))
            row = cur.fetchone()
            if row:
                columns = [description[0] for description in cur.description]
                return dict(zip(columns, row))
            return None
    
    def _get_classe_prioridade(self, prioridade_id):
        """Retorna a classe CSS para a prioridade"""
        classes = {
            1: 'low',      # Baixa
            2: 'medium',   # Média
            3: 'high',     # Alta
            4: 'urgent'    # Urgente
        }
        return classes.get(prioridade_id, 'medium')
    
    def _formatar_prazo(self, prazo):
        """Formata o prazo para exibição"""
        if not prazo:
            return "Não definido"
        
        if isinstance(prazo, str):
            prazo = datetime.fromisoformat(prazo)
        
        return prazo.strftime('%d/%m/%Y às %H:%M')
    
    def _calcular_tempo_resolucao(self, criacao, resolucao):
        """Calcula o tempo de resolução"""
        if not criacao or not resolucao:
            return "Não disponível"
        
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
    
    def _gerar_link_acompanhamento(self, codigo_referencia):
        """Gera link para acompanhamento da solicitação"""
        base_url = self.config.get('SISTEMA_URL', 'http://localhost:5001')
        return f"{base_url}/acompanhar/{codigo_referencia}"
    
    def _gerar_link_atualizacao(self, codigo_referencia):
        """Gera link para atualização da solicitação"""
        base_url = self.config.get('SISTEMA_URL', 'http://localhost:5001')
        return f"{base_url}/atualizar/{codigo_referencia}"
    
    def _gerar_link_avaliacao(self, codigo_referencia):
        """Gera link para avaliação da solicitação"""
        base_url = self.config.get('SISTEMA_URL', 'http://localhost:5001')
        return f"{base_url}/avaliar/{codigo_referencia}"
