# SAOS - Sistema de Abertura de OS

## 📋 Visão Geral

O SAOS (Sistema de Abertura de OS) é uma solução completa para gerenciamento de solicitações de suporte técnico, desenvolvida para permitir que clientes e técnicos abram, acompanhem e gerenciem solicitações de forma eficiente.

## 🚀 Funcionalidades Principais

### ✅ Funcionalidades Implementadas

1. **Gestão de Solicitações**
   - Criação de solicitações com código único
   - Categorização por tipo de problema
   - Sistema de prioridades (Baixa, Média, Alta, Urgente)
   - Controle de status (Aberto, Em Análise, Em Progresso, etc.)
   - Prazo de resolução automático baseado na prioridade

2. **Sistema de Usuários**
   - Suporte a clientes e técnicos
   - Perfis diferenciados (CLIENTE, TECNICO, ADMIN)
   - Controle de acesso baseado em perfil

3. **Comunicação Automática**
   - Templates de email personalizáveis
   - Notificações automáticas de status
   - Confirmação de abertura
   - Solicitação de informações adicionais
   - Notificação de resolução

4. **Dashboard e Relatórios**
   - Dashboard em tempo real
   - Gráficos de status e prioridades
   - Lista de solicitações recentes
   - Indicadores de urgência e vencimento

5. **API RESTful**
   - Endpoints completos para todas as operações
   - Suporte a filtros e paginação
   - Respostas padronizadas em JSON

6. **Histórico e Auditoria**
   - Registro completo de todas as ações
   - Histórico de mudanças de status
   - Sistema de comentários (públicos e internos)

## 🏗️ Arquitetura do Sistema

### Estrutura de Banco de Dados

```sql
-- Tabelas Principais
USUARIOS          -- Clientes e técnicos
CATEGORIAS        -- Tipos de solicitação
PRIORIDADES       -- Níveis de urgência
STATUS            -- Estados da solicitação
SOLICITACOES      -- Solicitações principais
HISTORICO         -- Log de ações
COMENTARIOS       -- Comentários das solicitações
ANEXOS            -- Arquivos anexados
TEMPLATES_EMAIL   -- Templates de comunicação
CONFIGURACOES     -- Configurações do sistema
NOTIFICACOES      -- Sistema de notificações
KNOWLEDGE_BASE    -- Base de conhecimento
```

### Estrutura de Arquivos

```
SAOS/
├── app.py                    # Aplicação principal
├── config.py                 # Configurações
├── requirements.txt          # Dependências
├── database/
│   ├── connection.py         # Conexão com banco
│   ├── schema.sql           # Schema completo
│   └── SAOS.FDB             # Banco Firebird
├── models/                   # Modelos de dados
│   ├── base.py              # Modelo base
│   ├── solicitacao.py       # Modelo de solicitações
│   ├── historico.py         # Modelo de histórico
│   └── comentario.py        # Modelo de comentários
├── routes/                   # Rotas da aplicação
│   ├── formulario.py        # Formulário original
│   ├── api.py               # API REST
│   └── dashboard.py         # Dashboard
├── utils/                    # Utilitários
│   ├── email_service.py     # Serviço de email
│   └── email_sender.py      # Envio de email (legado)
├── templates/                # Templates HTML
│   ├── form.html            # Formulário original
│   └── dashboard.html       # Dashboard moderno
└── static/                   # Arquivos estáticos
    ├── css/
    └── js/
```

## 🔧 Instalação e Configuração

### Pré-requisitos

- Python 3.8+
- Firebird Database
- pip (gerenciador de pacotes Python)

### Passos de Instalação

1. **Clone o repositório**
   ```bash
   git clone <repository-url>
   cd SAOS
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure o banco de dados**
   - Crie um banco Firebird
   - Execute o script `database/schema.sql`
   - Configure a conexão em `database/connection.py`

4. **Configure o email**
   - Edite as configurações em `utils/email_service.py`
   - Configure SMTP do Office 365

5. **Execute a aplicação**
   ```bash
   python app.py
   ```

### Configurações Importantes

#### Banco de Dados
```python
# database/connection.py
DATABASE_CONFIG = {
    'host': 'localhost',
    'database': 'path/to/SAOS.FDB',
    'user': 'SYSDBA',
    'password': 'masterkey'
}
```

#### Email (Office 365)
```python
# Configurações no banco CONFIGURACOES
EMAIL_SMTP_HOST = 'smtp.office365.com'
EMAIL_SMTP_PORT = '587'
EMAIL_SMTP_USER = 'seu-email@empresa.com.br'
EMAIL_SMTP_PASS = 'sua-senha-app'
```

## 📡 API REST

### Endpoints Principais

#### Solicitações
- `GET /api/v1/solicitacoes` - Lista solicitações
- `POST /api/v1/solicitacoes` - Cria nova solicitação
- `GET /api/v1/solicitacoes/{id}` - Obtém solicitação específica
- `PUT /api/v1/solicitacoes/{id}` - Atualiza solicitação
- `PUT /api/v1/solicitacoes/{id}/status` - Atualiza status

#### Dashboard
- `GET /api/v1/dashboard` - Dados do dashboard
- `GET /api/v1/solicitacoes/urgentes` - Solicitações urgentes
- `GET /api/v1/solicitacoes/vencidas` - Solicitações vencidas

#### Catálogos
- `GET /api/v1/categorias` - Lista categorias
- `GET /api/v1/prioridades` - Lista prioridades
- `GET /api/v1/status` - Lista status

### Exemplo de Uso da API

#### Criar Nova Solicitação
```bash
curl -X POST http://localhost:5001/api/v1/solicitacoes \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Problema de Login",
    "descricao": "Não consigo acessar o sistema",
    "id_cliente": 1,
    "id_categoria": 2,
    "id_prioridade": 2
  }'
```

#### Atualizar Status
```bash
curl -X PUT http://localhost:5001/api/v1/solicitacoes/1/status \
  -H "Content-Type: application/json" \
  -d '{
    "novo_status_id": 3,
    "tecnico_id": 2,
    "comentario": "Iniciando análise do problema"
  }'
```

## 📧 Sistema de Email

### Templates Disponíveis

1. **confirmacao_abertura**
   - Enviado quando uma solicitação é criada
   - Inclui código, título, categoria, prioridade e prazo

2. **atualizacao_status**
   - Enviado quando o status é alterado
   - Inclui novo status, responsável e comentário

3. **solicitacao_informacoes**
   - Enviado quando mais informações são necessárias
   - Inclui lista de informações solicitadas

4. **resolucao_concluida**
   - Enviado quando a solicitação é resolvida
   - Inclui solução e link para avaliação

### Personalização de Templates

Os templates são armazenados no banco de dados e podem ser editados via SQL:

```sql
UPDATE TEMPLATES_EMAIL 
SET CORPO_HTML = 'novo template HTML'
WHERE NOME = 'confirmacao_abertura';
```

## 🎨 Interface do Usuário

### Dashboard Moderno
- Interface responsiva com Tailwind CSS
- Gráficos interativos com Chart.js
- Atualização em tempo real
- Modal para criação de solicitações

### Formulário Original
- Mantido para compatibilidade
- Interface simples e direta
- Upload de arquivos

## 🔄 Fluxo de Trabalho

### 1. Abertura de Solicitação
1. Cliente acessa o sistema
2. Preenche formulário com dados da solicitação
3. Sistema gera código único
4. Email de confirmação é enviado
5. Solicitação aparece no dashboard

### 2. Triagem e Atribuição
1. Técnico visualiza solicitações no dashboard
2. Atribui responsável baseado na categoria
3. Atualiza status para "Em Análise"
4. Email de atualização é enviado

### 3. Resolução
1. Técnico trabalha na solicitação
2. Atualiza status conforme progresso
3. Adiciona comentários e anexos
4. Marca como resolvida quando concluído
5. Email de resolução é enviado

### 4. Avaliação
1. Cliente recebe email de resolução
2. Acessa link para avaliar o serviço
3. Avaliação é registrada no sistema

## 📊 Relatórios e Métricas

### Dashboard em Tempo Real
- Total de solicitações
- Solicitações por status
- Solicitações por prioridade
- Solicitações urgentes
- Solicitações vencidas

### Relatórios Disponíveis
- Solicitações por período
- Performance por técnico
- Tempo médio de resolução
- Satisfação do cliente
- Categorias mais solicitadas

## 🔐 Segurança

### Controle de Acesso
- Autenticação por perfil de usuário
- Controle de acesso baseado em roles
- Registro de todas as ações (auditoria)

### Validações
- Validação de dados de entrada
- Sanitização de conteúdo
- Controle de upload de arquivos
- Validação de tipos de arquivo

## 🚀 Melhorias Futuras

### Funcionalidades Planejadas
1. **Sistema de Notificações Push**
   - Notificações em tempo real
   - Integração com WebSockets

2. **Mobile App**
   - Aplicativo nativo para iOS/Android
   - Notificações push

3. **Integração com Calendário**
   - Sincronização com Outlook/Google
   - Lembretes automáticos

4. **Knowledge Base**
   - Base de conhecimento integrada
   - Sugestões automáticas de soluções

5. **Relatórios Avançados**
   - Exportação para Excel/PDF
   - Dashboards personalizáveis

6. **Automação**
   - Escalonamento automático
   - Atribuição inteligente
   - Lembretes automáticos

## 🛠️ Manutenção

### Backup
- Backup regular do banco Firebird
- Backup dos arquivos de upload
- Versionamento do código

### Monitoramento
- Logs de erro
- Monitoramento de performance
- Alertas de sistema

### Atualizações
- Atualizações de segurança
- Melhorias de performance
- Novas funcionalidades

## 📞 Suporte

Para suporte técnico ou dúvidas sobre o sistema, entre em contato:

- **Email**: suporte@empresa.com.br
- **Telefone**: (11) 99999-9999
- **Documentação**: Este arquivo e comentários no código

## 📄 Licença

Este sistema foi desenvolvido para uso interno da empresa. Todos os direitos reservados.

---

**Versão**: 2.0.0  
**Data**: Dezembro 2024  
**Desenvolvedor**: Equipe de TI
