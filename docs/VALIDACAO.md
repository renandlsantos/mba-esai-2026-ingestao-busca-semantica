# Evidências de validação — 2026-09-19

## Executado

- Ambiente isolado `.venv`, CPython 3.12.14, dependências do starter preservadas; pytest 8.4.2 e Ruff 0.13.2.
- TDD: primeira coleta falhou por ausência de `config`, módulo ainda não implementado; após implementação, 16 testes passaram. Novos casos de integração e CLI elevaram a suíte a 21.
- `RUN_DB_TESTS=1 .venv/bin/python -m pytest -q`: **21 passed in 1.09s**.
- `.venv/bin/ruff check src tests scripts`: **All checks passed!**.
- `docker compose up -d --wait`: sucesso após simplificação do serviço de inicialização; PostgreSQL saudável em 127.0.0.1:55433, projeto mba-esai-293.
- Integração usa PGVector real: 12 documentos inseridos duas vezes mantêm 12 registros; busca k=10 retorna dez e o texto idêntico vem primeiro; PDF original é ingerido duas vezes sem aumento indevido. Apenas a collection com UUID criada pelo teste foi excluída.
- PDF original: 34 páginas extraídas, conteúdo textual presente.
- Estrutura obrigatória e prompt original preservados; mensagens verificadas por doubles; erros do CLI retornam 1 sem imprimir segredos.
- Spec Kit: resolução de templates, setup-plan, setup-tasks e check-prerequisites executados; checklist de requisitos 8/8 revisados; nenhum hook de extensão configurado.

## Incidente resolvido

Compose original tinha bootstrap de execução única: terminava com código 0, mas `up --wait` reportava falha por o container estar encerrado. Removido serviço redundante porque PGVector cria a extensão. Container temporário dessa tentativa removido por nome; nenhum volume apagado. Banco ficou saudável e testes posteriores passaram. Após os testes, o container próprio foi parado com `docker compose stop`; o volume foi preservado.

## Pendente antes de entregar

**SC-004 / T015:** não foi usada chave de OpenAI nem executada avaliação de modelo real. Rodar ingestão com provedor configurado e `python scripts/evaluate_live.py`; revisar resposta coberta e três recusas, registrar modelos/data/resultados. Os embeddings de teste não medem semântica. Não foi feita submissão ou merge para main.

## Dependências

O advisory Endor acionou uma revisão package-risk de pytest==8.4.2 e ruff==0.13.2. Não há ferramenta MCP Endor de risco acessível neste ambiente; resultado **UNKNOWN**, lacuna `endor_mcp_package_risk_unavailable`. Não representa aprovação nem evidência de vulnerabilidade. A instalação local é parte do desenvolvimento autorizado; nenhum segredo/configuração Endor foi consultado.


## Execução real Spark — 20/09/2026

Fonte: [JSON da avaliação](avaliacao-spark-2026-09-20.json). API compatível com OpenAI;
modelos `spark/code` e `spark/embed`. O probe autenticado confirmou chat, listagem de modelos
e embeddings com 1024 dimensões. Credencial carregada do arquivo externo indicado pelo operador,
sem copiar a chave para .env ou Git. O .env local referencia LLM_ENV_FILE e foi criado com modo600.

Ingestão real: **67 trechos** do PDF original em PostgreSQL/pgVector, banco/volume Compose
`mba-esai-293-spark` separado na porta55434. Não reutiliza nem apaga dados do ambiente anterior.

| Pergunta | Resposta real | Revisão do coordenador |
|---|---|---|
| Faturamento SuperTechIABrazil | R$ 10.000.000,00 | Coincide com PDF; sem afirmação extra |
| Capital da França | Recusa exata exigida | Aprovado |
| Quantos clientes em2024 | Recusa exata exigida | Aprovado |
| Você acha bom ou ruim | Recusa exata exigida | Aprovado |

A recusa foi `Não tenho informações necessárias para responder sua pergunta.`.
O JSON conserva human_review_required=true como característica do script; houve leitura das
quatro respostas pelo coordenador nesta rodada, sem alegar aceite humano do aluno/professor.

Comandos: `.venv/bin/python src/ingest.py` (exit0),
`.venv/bin/python scripts/evaluate_live.py` (exit0),
`RUN_DB_TESTS=1 .venv/bin/python -m pytest -q` (29passed), Ruff aprovado.
Regressões cobrem credencial externa explícita, endpoint compatível, limite de tokens e timeout,
credenciais fora do repr e embeddings enviados como texto sem IDs do tokenizer OpenAI.
A suite de banco usa somente coleção de UUID no banco de testes anterior, independente da
coleção Spark; seu cleanup não remove os dados reais da ingestão.

Limites: o conjunto de aceitação contém quatro perguntas, não um benchmark geral de RAG ou
prova de imunidade a prompt injection. Não houve teste OpenAI nem merge/submissão acadêmica.


Revisão independente corrigiu duas falhas de configuração antes do commit: chave Spark
sem URL agora é recusada e placeholders vazios no .env não ocultam o arquivo externo.
Dois testes reproduzem esses casos com valores sintéticos. A leitura usa dotenv_values,
sem interpolação nem mutação do ambiente global. O CLI real também foi executado com
pergunta de faturamento seguida de sair, exit0: [transcrição](cli-spark-2026-09-20.txt).
