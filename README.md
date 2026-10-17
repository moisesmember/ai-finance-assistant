# Assistente Inteligente de Analise Financeira Pessoal

## Visão de portfólio

**Problema:** transformar transações importadas em indicadores compreensíveis, mantendo os cálculos separados da geração de texto.

**Diferencial de arquitetura:** o domínio calcula os indicadores; a porta de LLM permite explicar os resultados sem colocar os cálculos financeiros sob responsabilidade do modelo.

### Escopo atual

| Capacidade | Situação documentada |
| --- | --- |
| Importação CSV, contas e transações | Implementada no MVP |
| Categorização | Regras por palavras-chave |
| Indicadores e resumo | Cálculo determinístico |
| Explicação em linguagem natural | Provider simulado por padrão; adaptador opcional para LangChain |
| ML supervisionado, SHAP, RAG e Open Finance | Não implementados |
| Autenticação real e isolamento multiusuário | Próximos passos |

### Demonstração local

Siga a instalação abaixo, importe [data/sample_transactions.csv](data/sample_transactions.csv) e compare os endpoints de resumo e explicação. A resposta simulada permite testar o fluxo, mas não mede qualidade de uma LLM real.

Consulte os [testes](tests) para os cenários de importação, classificação e geração de insights.

Backend MVP em Python/FastAPI para importar transacoes financeiras via CSV, consolidar historico por conta/cartao, categorizar lancamentos por palavras-chave, gerar insights financeiros basicos e produzir explicacoes em linguagem natural a partir dos dados ja calculados.

O projeto ainda nao implementa ML, SHAP, RAG ou Open Finance. A arquitetura deixa portas explicitas para esses componentes futuros sem acoplar o MVP a ferramentas de IA. A camada de LLM atual e simples e usa um provider fake por padrao para testes locais.

## Arquitetura

O codigo segue uma arquitetura limpa/hexagonal simples:

- `app/domain`: entidades, contratos de repositorio e servicos de dominio.
- `app/application/use_cases`: casos de uso orquestrando regras sem depender de FastAPI ou SQLAlchemy.
- `app/infrastructure/database`: sessao, base declarativa e modelos SQLAlchemy 2.0 async.
- `app/infrastructure/repositories`: adaptadores SQLAlchemy para as portas do dominio.
- `app/infrastructure/api`: rotas FastAPI e schemas HTTP.
- `app/infrastructure/llm`: providers de LLM, incluindo fake local e estrutura opcional para LangChain.
- `tests`: testes automatizados de importacao, categorizacao e insights.

Pontos de extensao para IA futura estao em `app/domain/services/ai_extension_ports.py`.

## Camada de LLM

A camada de LLM do MVP tem uma responsabilidade limitada: transformar o resumo financeiro estruturado em uma explicacao clara e educativa.

Ela nao calcula metricas financeiras. As metricas continuam sendo calculadas pelo dominio em `BasicInsightGenerator`; a LLM apenas interpreta agregacoes e insights ja produzidos pelo sistema.

Componentes principais:

- `app/domain/services/llm_provider.py`: porta `LLMProvider` com `generate_response(prompt: str) -> str`.
- `app/domain/services/financial_explanation_service.py`: orquestra resumo financeiro, prompt e provider.
- `app/domain/services/financial_explanation_prompt.py`: centraliza o prompt usado para explicacoes financeiras.
- `app/infrastructure/llm/fake_llm_provider.py`: provider fake usado por padrao no MVP.
- `app/infrastructure/llm/langchain_provider.py`: adaptador reutilizavel para chains/runnables do LangChain.
- `app/infrastructure/llm/langchain_factory.py`: factories opcionais para criar providers com LangChain.

Por privacidade, o prompt de explicacao nao envia transacoes brutas completas, descricoes de compras ou nomes reais de contas. Ele usa apenas agregacoes como totais, variacoes, categoria principal, despesas por conta anonimizada e insights calculados.

LangChain e opcional. O codigo de integracao so importa `langchain_core` dentro da factory, quando ela e usada. O endpoint segue usando `FakeLLMProvider` por padrao.

## Requisitos

- Python 3.11+
- Docker e Docker Compose
- PostgreSQL, quando rodar fora do Compose

## Como executar com Docker Compose

```bash
docker compose up --build
```

Em outro terminal, execute as migrations:

```bash
docker compose exec app alembic upgrade head
```

A API ficara disponivel em:

- Swagger: `http://localhost:8000/docs`
- Healthcheck: `http://localhost:8000/health`

## Execucao local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

No Linux/macOS, use `source .venv/bin/activate` em vez do comando de ativacao do Windows.

## Exemplo de CSV

Arquivo: `data/sample_transactions.csv`

```csv
date,description,amount,account_name,institution,account_type
2026-05-03,Salario Empresa XPTO,8500.00,Santander Conta,Santander,checking_account
2026-05-04,Supermercado Mercado Livre,-610.25,Santander Conta,Santander,checking_account
2026-05-06,Spotify Premium,-21.90,Nubank Cartao,Nubank,credit_card
```

Colunas obrigatorias:

- `date`
- `description`
- `amount`
- `account_name`
- `institution`
- `account_type`

Tipos de conta aceitos:

- `checking_account`
- `savings_account`
- `credit_card`

Valores negativos sao tratados como debito. Valores positivos sao tratados como credito. O valor e persistido como absoluto e o tipo fica em `transaction_type`.

## Endpoints

### Criar conta

```bash
curl -X POST http://localhost:8000/accounts \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Nubank Cartao\",\"institution\":\"Nubank\",\"type\":\"credit_card\"}"
```

### Listar contas

```bash
curl http://localhost:8000/accounts
```

### Importar transacoes

```bash
curl -X POST "http://localhost:8000/transactions/import?user_id=default-user" \
  -F "file=@data/sample_transactions.csv"
```

### Listar transacoes com filtros

```bash
curl "http://localhost:8000/transactions?start_date=2026-05-01&end_date=2026-05-31&transaction_type=debit"
```

Filtros disponiveis:

- `start_date`
- `end_date`
- `category`
- `account_id`
- `transaction_type`
- `user_id`

### Gerar resumo financeiro

```bash
curl "http://localhost:8000/insights/summary?month=2026-05-01&user_id=default-user"
```

O resumo inclui:

- total de receitas no mes
- total de despesas no mes
- saldo consolidado
- maior categoria de gasto
- comparacao com mes anterior
- top 5 maiores gastos
- gastos por conta/cartao
- percentual de uso de cartao
- mensagens de insight

### Gerar explicacao financeira em linguagem natural

```bash
curl "http://localhost:8000/insights/explanation?month=2026-05-01&user_id=default-user"
```

O endpoint:

- busca o mesmo resumo financeiro usado em `/insights/summary`
- monta um prompt estruturado com agregacoes financeiras
- chama o provider configurado pela porta `LLMProvider`
- retorna uma explicacao em linguagem natural

Exemplo de resposta:

```json
{
  "month": "2026-05",
  "explanation": "Esta e uma explicacao simulada para testes locais..."
}
```

## Categorias iniciais

- Alimentacao
- Transporte
- Moradia
- Saude
- Educacao
- Mercado
- Assinaturas
- Lazer
- Transferencia
- Outros

O classificador atual usa palavras-chave e pode ser substituido por uma implementacao supervisionada sem alterar os casos de uso.

## Testes

```bash
pytest
```

Os testes cobrem:

- importacao CSV
- categorizacao por palavras-chave
- geracao de insights basicos
- geracao de prompt financeiro sem expor transacoes brutas
- adaptador reutilizavel para LangChain

## Proximos passos

- Deduplicacao configuravel de transacoes importadas.
- Autenticacao real e isolamento multiusuario.
- Filtros agregados por periodo e por conta.
- Classificador supervisionado usando historico rotulado.
- Embeddings para descricoes financeiras.
- Explicabilidade com SHAP para modelos futuros.
- Providers reais de LLM para OpenAI, Ollama ou LangChain.
- Analise temporal avancada para sazonalidade e anomalias.
