# Implementation Plan: Consulta fundamentada em PDF

**Branch**: `feature/sdd-fase-293` | **Date**: 2026-09-19 | **Spec**: [spec.md](spec.md)

## Summary
Implementar o starter com funções pequenas: configuração validada, extração de PDF, split determinístico, PGVector e chat. Preservar prompt obrigatório. Injetar store/model nos testes, sem trocar o comportamento de produção por mocks.

## Technical Context
**Language/Version**: Python 3.12.
**Primary Dependencies**: LangChain 0.3.27 e integrações fixadas no starter; OpenAIEmbeddings, ChatOpenAI, PyPDFLoader, RecursiveCharacterTextSplitter, PGVector.
**Storage**: PostgreSQL 17 + pgvector; Docker Compose isolado mba-esai-293, porta host 55433.
**Testing**: pytest, doubles locais e teste opt-in com banco real/embeddings determinísticos de teste.
**Target Platform**: macOS/Linux com Docker.
**Project Type**: CLI.
**Performance Goals**: sem meta de latência imposta; timeout de API 60s, duas tentativas e dez candidatos limitam chamadas.
**Constraints**: chunks 1000/150, k=10, prompt do enunciado, não apagar dados nem publicar segredos.
**Scale/Scope**: um operador, PDF textual, uma collection por versão/modelo.

## Constitution Check
Pré e pós-design: I PASS (prompt e empty guard); II PASS (stack/caminhos/parâmetros); III PASS (versões/IDs estáveis/collection teste própria); IV PASS (.env ignorado/erros seguros); V PASS (matriz e validação). Sem exceções.

## Project Structure
- `src/config.py`: ambiente, validação e criação de clientes.
- `src/ingest.py`: carregamento, split, IDs e persistência.
- `src/search.py`: prompt obrigatório, retrieval e geração.
- `src/chat.py`: loop terminal e códigos de saída.
- `tests/test_rag.py`: unidade/contratos, doubles claramente nomeados.
- `tests/test_pgvector.py`: persistência e k=10 reais, sem API paga.
- `scripts/evaluate_live.py`: avaliação opt-in com provedor real.
- `docs/`: aulas referenciadas, matriz de requisitos e evidências.
- `specs/001-pdf-rag/`: especificação, pesquisa, modelo, contratos, quickstart, tarefas.

**Structure Decision**: manter a estrutura exigida e apenas um módulo auxiliar de configuração; composição e funções simples evitam abstrações desnecessárias.

## Complexity Tracking
Nenhuma violação. Não acrescentar agente, servidor web ou cache sem requisito.
