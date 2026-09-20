# MBA ESAI 2026 — Ingestão e busca semântica

**Preferência do autor:** modelos locais no Spark. Geração com `spark/code` e embeddings com `spark/embed`; configuração e credencial externa conforme a seção Spark abaixo.


Implementação da fase 293: PDF → chunks → embeddings → PostgreSQL/pgVector → perguntas no terminal com LangChain.

**Estado:** código, banco e quatro casos de aceitação com Spark real validados em 20/09/2026 (spark/code + spark/embed). A execução com OpenAI não foi realizada; o desafio não fixa modelo. Não foi submetido à plataforma. O desenvolvimento está na branch `feature/sdd-fase-293`.

## Processo SDD

Spec Kit oficial 1.0.8: [constituição](.specify/memory/constitution.md) → [especificação](specs/001-pdf-rag/spec.md) → [plano](specs/001-pdf-rag/plan.md) → [tarefas](specs/001-pdf-rag/tasks.md) → implementação → convergência. [Rastreabilidade](docs/RASTREABILIDADE.md), [referências de aulas](docs/REFERENCIAS.md) e [evidências de validação](docs/VALIDACAO.md).

Para retomar o workflow em um clone novo, selecione explicitamente a feature:

```bash
export SPECIFY_FEATURE_DIRECTORY=specs/001-pdf-rag
.specify/scripts/bash/check-prerequisites.sh --json --require-spec --require-tasks --include-tasks
```

```mermaid
flowchart LR
    PDF[PDF textual] --> Split[Chunks 1000 / overlap 150]
    Split --> Emb[OpenAI embeddings]
    Emb --> DB[(PostgreSQL + pgVector)]
    Q[Pergunta no terminal] --> R[Busca k=10]
    DB --> R
    R --> C[Contexto + prompt obrigatório]
    C --> L[Modelo de chat]
    L --> A[Resposta ou recusa]
```

## Executar

Pré-requisitos: Python 3.12, Docker com Compose, conta OpenAI e acesso aos modelos configurados. A ingestão e as perguntas enviam texto ao provedor e podem gerar cobrança. Não usar documentos confidenciais sem autorização.

```bash
git clone https://github.com/renandlsantos/mba-esai-2026-ingestao-busca-semantica.git
cd mba-esai-2026-ingestao-busca-semantica
git checkout feature/sdd-fase-293
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
```

Preencha `OPENAI_API_KEY` no `.env` local, sem publicá-la. Modelos iniciais: `text-embedding-3-small` e `gpt-4.1-mini`; altere as variáveis se necessário. O código não carrega credenciais na importação dos módulos.

```bash
docker compose up -d --wait
python src/ingest.py
python src/chat.py
```

Exemplo de perguntas para o PDF fornecido no starter:

```text
PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
PERGUNTA: Qual é a capital da França?
PERGUNTA: Quantos clientes temos em 2024?
PERGUNTA: Você acha isso bom ou ruim?
```

A primeira pergunta deve mencionar R$ 10.000.000,00, valor presente no PDF. As outras devem retornar exatamente `Não tenho informações necessárias para responder sua pergunta.`. São resultados esperados, **não evidência de execução com modelo real**.

Digite `sair`, `exit`, `quit`, Ctrl-D ou Ctrl-C para encerrar. Linhas vazias são ignoradas. Consulta única: `python src/search.py "sua pergunta"`.

## Configuração

| Variável | Uso |
|---|---|
| OPENAI_API_KEY | Chave obrigatória, somente no ambiente local |
| OPENAI_EMBEDDING_MODEL | Modelo de embeddings |
| OPENAI_CHAT_MODEL | Modelo de chat |
| DATABASE_URL | URL SQLAlchemy usando postgresql+psycopg |
| PG_VECTOR_COLLECTION_NAME | Collection isolada do documento/modelo |
| PDF_PATH | PDF; caminho relativo à raiz do repositório |
| POSTGRES_PORT | Porta do Compose; manter igual à DATABASE_URL |

O banco usa porta **55433**, escuta apenas em localhost e volume `mba-esai-293_postgres_data`. O PGVector inicializa a extensão e suas tabelas. Credenciais `postgres/postgres` são somente para esse banco didático local. Para parar preservando dados: `docker compose stop`.

## Ingestão e versões

O splitter configura 1000 caracteres e overlap 150; limites por parágrafo/página podem produzir trechos menores e overlap efetivo menor que 150. IDs usam collection + SHA256 do PDF + índice. Reexecutar o **mesmo** PDF faz upsert e completa cargas interrompidas sem duplicá-las. Metadados preservam página, nome e modelo sem armazenar caminhos absolutos pessoais.

Para **outro PDF ou versão alterada**, escolha nova collection. A aplicação não apaga chunks de versões anteriores. Para **outro modelo de embedding**, use outro banco dedicado: modelos diferentes podem ter dimensões incompatíveis nas tabelas compartilhadas do PGVector. Não apague o volume atual automaticamente; preserve-o e reingira no banco novo.

PDFs escaneados sem camada textual e PDFs criptografados não são suportados; falham explicitamente. Erros não imprimem URL/chave/caminho privado. Confira arquivo e `.env`, depois `docker compose ps` e o acesso ao provedor.

## Testar

```bash
python -m pytest -q
ruff check src tests scripts
RUN_DB_TESTS=1 python -m pytest tests/test_pgvector.py -q
```

O teste de banco usa PostgreSQL/pgVector real e **embeddings determinísticos de teste**; cria uma collection com UUID e remove somente essa collection no final. Ele prova persistência, upsert e top-k, não qualidade semântica de uma LLM. `TEST_DATABASE_URL` permite apontar para outro banco exclusivo de testes.

Após configurar chave e ingerir o PDF original, a avaliação real é explícita:

```bash
python scripts/evaluate_live.py > avaliacao-local.json
```

Revise as quatro respostas. O script retorna 1 se a checagem textual detectar falha, mas o retorno 0 também exige revisão humana: ele apenas verifica valor esperado/recusa e não prova ausência de outras afirmações incorretas. Revise o JSON antes de publicá-lo; registre resultados e modelo em `docs/VALIDACAO.md`.

## Limites e entrega

Top-k fornece candidatos, não garantia de evidência. O prompt obrigatório é preservado e documentos são tratados como dados. Contexto vazio recusa sem chamar o modelo. Nenhum mecanismo promete eliminação absoluta de alucinações ou prompt injection; os testes reais de aceitação são necessários antes da entrega.

Estrutura obrigatória preservada: `docker-compose.yml`, `requirements.txt`, `.env.example`, `src/ingest.py`, `src/search.py`, `src/chat.py`, `document.pdf`, `README.md`. Origem: [starter Full Cycle](https://github.com/devfullcycle/mba-ia-desafio-ingestao-busca). A entrega final é a URL HTTPS do repositório público, após revisão, merge autorizado e validação real; nenhuma submissão automática foi realizada.


## Usar servidor local compatível (Spark)

O servidor deve oferecer `/v1/chat/completions` e `/v1/embeddings`. No `.env` local,
configure os modelos e a referência ao arquivo de credenciais; não copie a chave:

```dotenv
LLM_ENV_FILE=~/.config/spark/spark-api.env
OPENAI_CHAT_MODEL=spark/code
OPENAI_EMBEDDING_MODEL=spark/embed
LLM_TIMEOUT_SECONDS=300
LLM_MAX_TOKENS=4096
COMPOSE_PROJECT_NAME=mba-esai-293-spark
POSTGRES_PORT=55434
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:55434/rag
PG_VECTOR_COLLECTION_NAME=mba_esai_293_spark_embed_v1
PDF_PATH=document.pdf
```

O arquivo externo usa SPARK_BASE_URL/SPARK_API_KEY ou OPENAI_BASE_URL/OPENAI_API_KEY.
Prioridade para valores não vazios: ambiente > .env local > arquivo externo.
Campos vazios de templates não ocultam a credencial externa; nenhum segredo é exportado ao ambiente global.
SPARK_* tem preferência sobre aliases OPENAI_*; evite misturar configurações de provedores.
O arquivo externo permanece fora do Git e só é lido quando LLM_ENV_FILE está configurado.
Timeout pode subir até 1500s; max_tokens aceita 400–32768. O perfil inicial usa spark/code
(resposta direta) e 4096 tokens. Não confunda compatibilidade da API com o provedor OpenAI.

```bash
docker compose -p mba-esai-293-spark up -d --wait
python src/ingest.py
python scripts/evaluate_live.py
python src/chat.py
```

Banco/volume separados preservam os vetores anteriores. `spark/embed` foi observado com
1024 dimensões. O cliente envia textos para esse endpoint sem tokenizer OpenAI.
As chamadas passam pelo router; sua observabilidade é administrada pelo operador.
Nenhum reasoning_content ou segredo é incluído nos relatórios do projeto.
