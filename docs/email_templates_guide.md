# 📧 Guia de Templates de Email - SAOS

## Visão Geral

O sistema SAOS utiliza templates de email personalizados para enviar notificações aos clientes. O template padrão para confirmação de abertura de solicitações é baseado no arquivo `template1.html`.

## 🎨 Template Padrão (template1.html)

### Características
- **Design responsivo** com CSS inline
- **Cores da Medware** (azul #0056b3)
- **Fonte Roboto** para melhor legibilidade
- **Layout profissional** com header, conteúdo e footer

### Variáveis Disponíveis

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `{nome_cliente}` | Nome do cliente | "Dr. João Silva" |
| `{codigo_referencia}` | Código da solicitação | "OS20241201001" |
| `{data_hora}` | Data e hora da criação | "01/12/2024 - 14:30" |
| `{tipo_solicitacao}` | Tipo da solicitação | "Problema de Acesso" |
| `{sistema}` | Sistema relacionado | "Sistema Principal" |
| `{prazo_estimado}` | Prazo estimado | "3 dias úteis" |
| `{link_acompanhamento}` | Link para acompanhar | "http://localhost:5001/acompanhar/..." |

### Estrutura do Email

```
┌─────────────────────────────────────┐
│           MEDWARE SISTEMAS          │
│         Solicitação Registrada      │
├─────────────────────────────────────┤
│ Olá, [Nome do Cliente],             │
│                                     │
│ Sua solicitação foi recebida...     │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ Nº da Solicitação: OS2024...   │ │
│ │ Status Atual: Em análise       │ │
│ │ Data/Hora: 01/12/2024 - 14:30  │ │
│ │ Tipo: Problema de Acesso       │ │
│ │ Sistema: Sistema Principal     │ │
│ │ Prazo Estimado: 3 dias úteis   │ │
│ └─────────────────────────────────┘ │
│                                     │
│ [Acompanhar Solicitação] [WhatsApp] │
│                                     │
│ Atenciosamente,                     │
│ Equipe de Suporte Medware           │
├─────────────────────────────────────┤
│ Canais de Atendimento               │
│ www.medware.com.br                  │
│ (61) 3301 6575                      │
└─────────────────────────────────────┘
```

## 🔧 Implementação Técnica

### Classe EmailService

O template é implementado na classe `EmailService` no arquivo `utils/email_service.py`:

```python
def get_template1_html(self, variaveis):
    """Retorna o template template1.html com as variáveis substituídas"""
    template_html = '''<!DOCTYPE html>
    <html lang="pt-BR">
    <!-- Template HTML completo -->
    </html>'''
    
    return self._substituir_variaveis(template_html, variaveis)

def enviar_confirmacao_abertura(self, solicitacao_id):
    """Envia email de confirmação usando template1.html"""
    # Busca dados da solicitação
    # Prepara variáveis
    # Gera HTML com template1.html
    # Envia email
```

### Fluxo de Envio

1. **Cliente submete formulário** (`form.html`)
2. **Sistema cria solicitação** no banco de dados
3. **Função `enviar_email_confirmacao()`** é chamada
4. **EmailService** busca dados da solicitação
5. **Template1.html** é processado com variáveis
6. **Email é enviado** para o cliente

### Configuração de Email Corporativo

O sistema está configurado para usar o servidor de email corporativo da Medware:

**Configurações padrão:**
- `EMAIL_SMTP_HOST`: smtp.medware.com.br
- `EMAIL_SMTP_PORT`: 587
- `EMAIL_SMTP_USER`: medware@medware.com.br
- `EMAIL_SMTP_PASS`: Medware!111096
- `EMAIL_FROM`: medware@medware.com.br
- `EMAIL_ENABLE_SSL`: false
- `EMAIL_USE_DEFAULT_CREDENTIALS`: false

**Para configurar:**
```bash
python scripts/configurar_email.py
```

**Configurações no banco:**
```sql
SELECT CHAVE, VALOR FROM CONFIGURACOES WHERE CHAVE LIKE 'EMAIL_%'
```

## 🧪 Testes

### Script de Teste

Execute o script de teste para verificar se o template está funcionando:

```bash
python scripts/test_email_template.py
```

O script irá:
1. Criar uma solicitação de teste
2. Enviar email usando template1.html
3. Verificar substituição de variáveis
4. Gerar arquivo HTML de exemplo

### Verificação Manual

1. **Acesse o sistema** e crie uma nova solicitação
2. **Verifique o email** recebido
3. **Confirme se o layout** está correto
4. **Teste os links** de acompanhamento

## 🎨 Personalização

### Alterando Cores

Para alterar as cores do template, edite as variáveis CSS no método `get_template1_html()`:

```css
.header {
    background-color: #0056b3; /* Cor principal */
}

.primary {
    background-color: #0056b3; /* Botão primário */
}
```

### Alterando Conteúdo

Para alterar o conteúdo, modifique o HTML no template:

```html
<div class="header">
    <p>SUA EMPRESA</p>  <!-- Nome da empresa -->
    <h1>Solicitação Registrada</h1>
</div>
```

### Adicionando Novas Variáveis

1. **Adicione a variável** no template HTML
2. **Inclua no dicionário** de variáveis
3. **Atualize a documentação**

```python
variaveis = {
    'nova_variavel': 'valor',
    # ... outras variáveis
}
```

## 🔄 Fallback

Se o template1.html falhar, o sistema usa:

1. **Template do banco de dados** (se disponível)
2. **Email simples** como último recurso

### Logs de Erro

Os erros são registrados no console:

```
✅ Email enviado com sucesso usando template1.html para solicitação OS20241201001
❌ Erro no email moderno: [detalhes do erro]
❌ Erro no email simples: [detalhes do erro]
```

## 📱 Responsividade

O template é responsivo e funciona em:
- **Desktop** (largura máxima: 600px)
- **Tablet** (ajuste automático)
- **Mobile** (padding reduzido)

### Media Queries

```css
@media (max-width: 600px) {
    .email-container {
        margin: 10px;
    }
    
    .content {
        padding: 20px;
    }
}
```

## 🔗 Links Importantes

- **Acompanhamento**: Link para acompanhar a solicitação
- **WhatsApp**: Contato direto via WhatsApp
- **Website**: Site da empresa

### Configuração de Links

```python
link_acompanhamento = f"{base_url}/acompanhar/{codigo_referencia}"
whatsapp_link = "https://wa.me/556133016575"
website_link = "https://www.medware.com.br"
```

## 📊 Monitoramento

### Métricas de Email

- **Taxa de entrega**: % de emails entregues
- **Taxa de abertura**: % de emails abertos
- **Taxa de clique**: % de cliques nos links

### Logs de Sistema

```python
print(f"📧 Email enviado: {destinatario}")
print(f"📋 Solicitação: {codigo_referencia}")
print(f"⏰ Timestamp: {datetime.now()}")
```

---

**Versão**: 1.0  
**Última atualização**: Dezembro 2024  
**Responsável**: Equipe de Desenvolvimento SAOS
