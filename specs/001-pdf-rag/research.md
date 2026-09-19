# Pesquisa e decisões — 2026-09-19

## Provedor
Decisão: OpenAI, embeddings `text-embedding-3-small` e chat `gpt-4.1-mini`, ambos configuráveis. Fontes oficiais verificadas: https://developers.openai.com/api/docs/models/text-embedding-3-small e https://developers.openai.com/api/docs/models/gpt-4.1-mini. Alternativa: Gemini, permitido mas não obrigatório. Um provedor reduz superfície e credenciais. Disponibilidade na conta ainda requer teste real.

## Persistência
Decisão: PGVector da versão 0.0.15 fixada pelo starter, driver psycopg3, JSONB e IDs derivados de collection/hash/índice. Referência: https://reference.langchain.com/python/langchain-postgres/vectorstores/PGVector e fonte https://github.com/langchain-ai/langchain-postgres/blob/main/langchain_postgres/vectorstores.py . Não migrar para PGVectorStore v2 neste desafio porque o starter e enunciado recomendam a API atual do projeto. Reingestão é upsert do mesmo conteúdo; PDF alterado usa collection nova, sem limpeza automática.

## Grounding
Decisão: preservar integralmente o prompt obrigatório e usar mensagem system para tratar documentos/perguntas como dados. Contexto vazio recusa localmente. Alternativa de limiar semântico rejeitada: sem dataset calibrado seria um número arbitrário. Prompt não prova ausência de alucinação; avaliação real coberta/fora do contexto é gate da entrega.

## Aulas consultadas
Aulas 18411 (pipeline RAG), 18415 (indexação/identidade dos chunks), 18416 (recuperação como evidência). Referências em docs/REFERENCIAS.md, sem conteúdo privado copiado. Aplicação: separar ingestão/retrieval/geração e manter identidade para depuração.
