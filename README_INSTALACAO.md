# 🚀 SAOS - Sistema de Abertura de OS

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Firebird Database Server
- pip (gerenciador de pacotes Python)

## 🔧 Instalação

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd SAOS
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados
Certifique-se de que o Firebird está rodando e atualize a conexão em `database/connection.py`:

```python
con = fbd.connect(
    r'seu_host/seu_port:C:\caminho\para\SAOS.FDB',
    user='SYSDBA',
    password='masterkey',
    charset='UTF8'
)
```

### 5. Execute o script de inicialização
```bash
python scripts/init_database.py
```

Este script irá criar:
- ✅ Usuários iniciais
- ✅ Categorias de solicitação
- ✅ Prioridades
- ✅ Status
- ✅ Templates de email

### 6. Execute o sistema
```bash
python app.py
```

O sistema estará disponível em: `http://localhost:5001`

## 👤 Dados de Acesso

Após executar o script de inicialização, você terá acesso aos seguintes usuários:

### Administradores
- **Email:** `admin@medware.com.br` | **Senha:** `admin123`
- **Email:** `nayhan@medware.com.br` | **Senha:** `123456`

### Técnico
- **Email:** `suporte@medware.com.br` | **Senha:** `123456`

### Cliente
- **Email:** `cliente@teste.com.br` | **Senha:** `123456`
- **CPF:** `333.333.333-33` | **Senha:** `123456`

## 🔐 Como Fazer Login

### Para Técnicos/Administradores:
1. Acesse `http://localhost:5001/login`
2. Selecione "Técnico"
3. Digite o email e senha

### Para Clientes:
1. Acesse `http://localhost:5001/login`
2. Selecione "Cliente"
3. Digite o CPF/CNPJ e senha

## 📁 Estrutura do Projeto

```
SAOS/
├── app.py                 # Aplicação principal
├── config.py             # Configurações
├── requirements.txt      # Dependências Python
├── database/
│   ├── connection.py     # Conexão com Firebird
│   ├── schema.sql        # Estrutura do banco
│   └── SAOS.FDB         # Banco de dados
├── models/               # Modelos de dados
├── routes/               # Rotas da aplicação
├── templates/            # Templates HTML
├── utils/                # Utilitários
├── scripts/              # Scripts de manutenção
└── uploads/              # Arquivos enviados
```

## 🛠️ Funcionalidades

### Para Clientes:
- ✅ Login com CPF/CNPJ
- ✅ Abertura de solicitações
- ✅ Upload de arquivos
- ✅ Acompanhamento de status

### Para Técnicos:
- ✅ Login com email
- ✅ Dashboard com estatísticas
- ✅ Gestão de solicitações
- ✅ Atualização de status

### Para Administradores:
- ✅ Todas as funcionalidades de técnico
- ✅ Gestão de usuários
- ✅ Gestão de categorias
- ✅ Gestão de status
- ✅ Gestão de templates de email

## 🔧 Configurações Adicionais

### Email (Opcional)
Para configurar o envio de emails, edite `utils/email_service.py`:

```python
# Configurações do Office 365
SMTP_SERVER = 'smtp.office365.com'
SMTP_PORT = 587
EMAIL_USER = 'seu-email@empresa.com'
EMAIL_PASSWORD = 'sua-senha'
```

### Personalização
- **Cores:** Edite as variáveis CSS em `static/css/styles.css`
- **Logo:** Substitua o ícone no header dos templates
- **Empresa:** Atualize o nome da empresa nos templates

## 🚨 Solução de Problemas

### Erro de Conexão com Banco
```
Erro ao conectar ao banco de dados
```
**Solução:** Verifique se o Firebird está rodando e se as credenciais estão corretas.

### Erro de Módulo não Encontrado
```
ModuleNotFoundError: No module named 'firebird'
```
**Solução:** Instale o driver correto:
```bash
pip install firebird-driver==1.10.10
```

### Erro de Permissão
```
PermissionError: [Errno 13] Permission denied
```
**Solução:** Verifique as permissões da pasta `uploads/` e `logs/`.

## 📞 Suporte

Para suporte técnico, entre em contato:
- **Email:** suporte@medware.com.br
- **Telefone:** (11) 99999-9999

## 📝 Logs

Os logs do sistema são salvos em:
- `logs/app.log` - Logs da aplicação
- `logs/error.log` - Logs de erro

## 🔄 Atualizações

Para atualizar o sistema:
1. Faça backup do banco de dados
2. Atualize o código
3. Execute `python scripts/init_database.py` para novos dados
4. Reinicie a aplicação

---

**Desenvolvido por Medware** 🏢
