# Fluxo de Trabalho - SAOS

## 🔄 Diagrama do Fluxo Principal

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLIENTE       │    │   SISTEMA       │    │   TÉCNICO       │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │ 1. Acessa Sistema     │                       │
         │──────────────────────▶│                       │
         │                       │                       │
         │ 2. Preenche Formulário│                       │
         │──────────────────────▶│                       │
         │                       │                       │
         │                       │ 3. Valida Dados       │
         │                       │◀───────────────────────│
         │                       │                       │
         │                       │ 4. Gera Código Único  │
         │                       │◀───────────────────────│
         │                       │                       │
         │                       │ 5. Calcula Prazos     │
         │                       │◀───────────────────────│
         │                       │                       │
         │                       │ 6. Salva Solicitação  │
         │                       │◀───────────────────────│
         │                       │                       │
         │ 7. Confirma Criação   │                       │
         │◀──────────────────────│                       │
         │                       │                       │
         │ 8. Email Confirmação  │                       │
         │◀──────────────────────│                       │
         │                       │                       │
         │                       │ 9. Notifica Técnicos  │
         │                       │──────────────────────▶│
         │                       │                       │
         │                       │                       │ 10. Visualiza Dashboard
         │                       │                       │◀───────────────────────│
         │                       │                       │
         │                       │                       │ 11. Atribui Responsável
         │                       │                       │◀───────────────────────│
         │                       │                       │
         │                       │ 12. Atualiza Status   │
         │                       │◀───────────────────────│
         │                       │                       │
         │ 13. Email Atualização │                       │
         │◀──────────────────────│                       │
         │                       │                       │
         │                       │                       │ 14. Trabalha Solicitação
         │                       │                       │◀───────────────────────│
         │                       │                       │
         │                       │                       │ 15. Adiciona Comentários
         │                       │                       │◀───────────────────────│
         │                       │                       │
         │                       │                       │ 16. Atualiza Progresso
         │                       │                       │◀───────────────────────│
         │                       │                       │
         │ 17. Email Progresso   │                       │
         │◀──────────────────────│                       │
         │                       │                       │
         │                       │                       │ 18. Marca como Resolvida
         │                       │                       │◀───────────────────────│
         │                       │                       │
         │ 19. Email Resolução   │                       │
         │◀──────────────────────│                       │
         │                       │                       │
         │ 20. Avalia Serviço    │                       │
         │──────────────────────▶│                       │
         │                       │                       │
         │                       │ 21. Registra Avaliação│
         │                       │◀───────────────────────│
         │                       │                       │
         │                       │ 22. Fecha Solicitação │
         │                       │◀───────────────────────│
         │                       │                       │
```

## 📋 Detalhamento das Etapas

### Fase 1: Abertura da Solicitação
1. **Cliente acessa o sistema**
   - URL: `http://localhost:5001/`
   - Interface: Formulário de abertura

2. **Preenche formulário**
   - Campos obrigatórios: Título, Descrição, Categoria, Prioridade
   - Campos opcionais: Sistema, Módulo, Anexos

3. **Sistema valida dados**
   - Verifica campos obrigatórios
   - Valida formato de email
   - Verifica tamanho de anexos

4. **Gera código único**
   - Formato: OS + YYYYMMDD + 6 dígitos sequenciais
   - Exemplo: OS2024120100001

5. **Calcula prazos**
   - Baseado na prioridade selecionada
   - Prazo de resolução
   - Prazo de escalonamento

6. **Salva solicitação**
   - Insere no banco de dados
   - Registra no histórico
   - Status inicial: "Aberto"

7. **Confirma criação**
   - Retorna código de referência
   - Exibe mensagem de sucesso

8. **Envia email de confirmação**
   - Template: `confirmacao_abertura`
   - Inclui todos os detalhes da solicitação

### Fase 2: Triagem e Atribuição
9. **Notifica técnicos**
   - Solicitação aparece no dashboard
   - Notificação para técnicos disponíveis

10. **Técnico visualiza dashboard**
    - Lista de solicitações pendentes
    - Filtros por categoria, prioridade, status

11. **Atribui responsável**
    - Técnico se auto-atribui ou é atribuído
    - Baseado em especialidade/categoria

12. **Atualiza status**
    - Novo status: "Em Análise"
    - Registra no histórico
    - Atualiza timestamp

13. **Envia email de atualização**
    - Template: `atualizacao_status`
    - Informa novo status e responsável

### Fase 3: Resolução
14. **Técnico trabalha solicitação**
    - Analisa problema
    - Identifica solução
    - Executa correções

15. **Adiciona comentários**
    - Comentários públicos (cliente vê)
    - Comentários internos (apenas técnicos)
    - Registra progresso

16. **Atualiza progresso**
    - Status: "Em Progresso"
    - Adiciona detalhes técnicos
    - Registra tempo gasto

17. **Envia email de progresso**
    - Template: `atualizacao_status`
    - Informa progresso realizado

18. **Marca como resolvida**
    - Status: "Resolvido"
    - Registra solução aplicada
    - Marca data/hora de resolução

19. **Envia email de resolução**
    - Template: `resolucao_concluida`
    - Inclui solução e link para avaliação

### Fase 4: Avaliação e Fechamento
20. **Cliente avalia serviço**
    - Acessa link de avaliação
    - Nota de 1 a 5 estrelas
    - Comentário opcional

21. **Sistema registra avaliação**
    - Salva avaliação no banco
    - Calcula média de satisfação
    - Registra no histórico

22. **Fecha solicitação**
    - Status: "Fechado"
    - Marca data/hora de fechamento
    - Solicitação arquivada

## 🔄 Fluxos Alternativos

### Fluxo: Solicitação de Informações Adicionais
```
Técnico → Status "Aguardando Cliente" → Email solicitação → Cliente responde → Continua fluxo normal
```

### Fluxo: Escalonamento
```
Prazo vencido → Sistema notifica → Escalona para supervisor → Novo responsável → Continua fluxo normal
```

### Fluxo: Cancelamento
```
Cliente/Técnico → Status "Cancelado" → Registra motivo → Solicitação arquivada
```

## ⏱️ Prazos por Prioridade

| Prioridade | Prazo Resolução | Prazo Escalonamento |
|------------|-----------------|-------------------|
| Baixa      | 5 dias úteis    | 4 dias úteis      |
| Média      | 3 dias úteis    | 2 dias úteis      |
| Alta       | 24 horas        | 12 horas          |
| Urgente    | 4 horas         | 2 horas           |

## 📧 Templates de Email

### 1. Confirmação de Abertura
- **Trigger**: Solicitação criada
- **Destinatário**: Cliente
- **Conteúdo**: Código, título, categoria, prioridade, prazo

### 2. Atualização de Status
- **Trigger**: Status alterado
- **Destinatário**: Cliente
- **Conteúdo**: Novo status, responsável, comentário

### 3. Solicitação de Informações
- **Trigger**: Status "Aguardando Cliente"
- **Destinatário**: Cliente
- **Conteúdo**: Informações necessárias, link para resposta

### 4. Resolução Concluída
- **Trigger**: Status "Resolvido"
- **Destinatário**: Cliente
- **Conteúdo**: Solução, tempo de resolução, link para avaliação

## 🎯 Pontos de Controle

### Controle de Qualidade
- Validação de dados de entrada
- Verificação de prazos
- Monitoramento de SLA
- Avaliação de satisfação

### Controle de Acesso
- Autenticação de usuários
- Controle por perfil
- Auditoria de ações
- Log de atividades

### Controle de Performance
- Tempo médio de resolução
- Taxa de satisfação
- Volume de solicitações
- Performance por técnico

## 📊 Métricas e KPIs

### Métricas de Volume
- Total de solicitações por período
- Solicitações por categoria
- Solicitações por prioridade

### Métricas de Tempo
- Tempo médio de resolução
- Tempo médio de primeira resposta
- Tempo médio por prioridade

### Métricas de Qualidade
- Taxa de satisfação
- Taxa de resolução no prazo
- Taxa de reincidência

### Métricas de Eficiência
- Solicitações por técnico
- Produtividade por período
- Utilização de recursos

---

**Versão**: 1.0  
**Data**: Dezembro 2024  
**Última Atualização**: Dezembro 2024
