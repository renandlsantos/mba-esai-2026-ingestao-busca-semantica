# Ingestão e Busca Semântica Constitution

## Core Principles

### I. Evidência antes da resposta
A aplicação MUST responder somente a partir dos trechos recuperados. Contexto vazio MUST produzir a recusa exigida sem chamar o modelo. Testes com doubles MUST ser identificados e não apresentados como qualidade comprovada da LLM.

### II. Fidelidade ao enunciado
O projeto MUST preservar os caminhos src/ingest.py, src/search.py, src/chat.py, document.pdf e docker-compose.yml. Python, LangChain, PostgreSQL e pgVector são obrigatórios; chunks usam tamanho 1000, overlap 150 e busca k=10.

### III. Reprodutibilidade e isolamento
Dependências MUST ter versões fixadas. Testes MUST isolar suas collections; comandos automáticos não podem apagar volumes ou collections do usuário. Repetição da mesma ingestão MUST evitar duplicação.

### IV. Privacidade e falhas explícitas
Segredos e transcrições privadas MUST ficar fora do Git. Erros de serviços MUST encerrar com status não zero sem imprimir credenciais ou afirmar sucesso.

### V. Rastreabilidade
Cada requisito MUST apontar para código, teste ou cenário manual. Decisões, limitações externas e validações executadas MUST ser documentadas antes da entrega.

## Additional Constraints
Escopo: PDF textual local e chat terminal de um único operador. Sem OCR, interface web ou submissão automática à plataforma. OpenAI é o provedor inicial configurável; não adicionar Gemini sem necessidade.

## Development Workflow
Executar constitution → specify → plan → tasks → implement → converge. Revisar artefatos em cada etapa. Testes locais são obrigatórios antes de commit; integração externa permanece pendente se faltarem credenciais. Publicar somente branch feature, sem merge automático.

## Governance
Alterações exigem justificativa registrada no plano e revisão de impacto. Mudanças incompatíveis elevam major, novos princípios minor, esclarecimentos patch. A revisão final verifica estes cinco princípios e registra desvios explicitamente.

**Version**: 1.0.0 | **Ratified**: 2026-09-19 | **Last Amended**: 2026-09-19
