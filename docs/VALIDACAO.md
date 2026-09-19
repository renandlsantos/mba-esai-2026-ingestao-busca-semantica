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
