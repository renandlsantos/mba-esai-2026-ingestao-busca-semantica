# Tasks: Consulta fundamentada em PDF

Input: spec.md, plan.md, research.md, data-model.md, contracts/cli.md. Testes exigidos pela especificação.

## Phase 1: Setup
- [X] T001 Configurar dependências de teste e ignores em requirements-dev.txt, .gitignore e .dockerignore.
- [X] T002 Isolar PostgreSQL em docker-compose.yml e documentar .env.example.

## Phase 2: Foundational
- [X] T003 Testar configuração inválida e segredos ausentes em tests/test_rag.py (FR-008).
- [X] T004 Implementar Settings e clientes em src/config.py (FR-008).

## Phase 3: User Story 1 — MVP de ingestão
Objetivo/teste independente: extrair PDF e verificar conteúdo, limite 1000/overlap 150, IDs e persistência repetida.
- [X] T005 [US1] Testar PDF ausente, vazio, inválido, split e IDs em tests/test_rag.py (FR-001/002/003).
- [X] T006 [US1] Implementar extração, metadados e upsert em src/ingest.py (FR-001/002/003).
- [X] T007 [US1] Testar banco real com collection exclusiva em tests/test_pgvector.py (SC-001/002).

## Phase 4: User Story 2 — Perguntas fundamentadas
Objetivo/teste independente: inspecionar prompt, k=10, contexto vazio e saída vazia.
- [X] T008 [US2] Testar recuperação e prompt com doubles em tests/test_rag.py (FR-004/005/006).
- [X] T009 [US2] Implementar retrieval e geração em src/search.py (FR-004/005/006).
- [X] T010 [US2] Criar avaliação opt-in de perguntas cobertas/ausentes em scripts/evaluate_live.py (SC-004).

## Phase 5: User Story 3 — CLI
Objetivo/teste independente: duas perguntas, entradas vazias, saída e falha.
- [X] T011 [US3] Testar diálogo e códigos de saída em tests/test_rag.py (FR-007/008).
- [X] T012 [US3] Implementar loop terminal em src/chat.py (FR-007/008).

## Phase 6: Polish
- [X] T013 [P] Documentar execução, referências de aulas e rastreabilidade em README.md e docs/ (FR-009).
- [X] T014 Validar testes, Compose, diff e registrar evidência em docs/VALIDACAO.md.
- [ ] T015 Executar avaliação real e registrar respostas em docs/VALIDACAO.md (SC-004; depende de credencial fornecida pelo operador).

## Dependencies & Execution Order
T001→T002→T003/T004→US1→US2→US3→validação. Testes escritos antes do código de cada história. T013 pode ocorrer em paralelo após contratos; US1 e US2 podem usar doubles independentes após T004, porém integração exige ambas. MVP: US1; entrega completa exige US2/US3 e gate real SC-004.

## Implementation Strategy
Entregar primeiro extração e persistência, depois resposta e CLI. Não marcar T015 quando só doubles tiverem sido executados. Cada etapa mantém o próximo comando reproduzível.

## Phase 7: Convergence

Revisão de 2026-09-19: 9 FR, 4 SC, três histórias, cinco princípios e decisões do plano. Um achado HIGH, partial: SC-004/T015 não tem evidência com provedor real; nenhum gap de código identificado. A execução permanece bloqueada por credencial não fornecida, sem resultado simulado.

- [ ] T016 Registrar avaliação real revisada em docs/VALIDACAO.md conforme SC-004 e US2/AC3 (partial; continuidade de T015 após configuração pelo operador).
