# Referências e relação com as aulas

Consultadas em 2026-09-19 no acervo local autorizado. Apenas títulos, links e decisões próprias são públicos; transcrições, capturas e resumos privados não foram copiados.

- [18411 — Arquitetura do RAG: ingestão, índice, retrieval e geração](https://plataforma.fullcycle.com.br/courses/a091b0fe-a5c6-4287-a3d3-1ec61defcfd3/413/224/291/conteudos?capitulo=291&conteudo=18411): motivou separar as etapas em funções testáveis.
- [18415 — Indexando chunks no Postgres com pgvector](https://plataforma.fullcycle.com.br/courses/a091b0fe-a5c6-4287-a3d3-1ec61defcfd3/413/224/291/conteudos?capitulo=291&conteudo=18415): motivou identidade estável e metadados para rastrear a origem; escolhemos upsert sem recriar tabelas.
- [18416 — Retrieval onde o RAG ganha ou perde](https://plataforma.fullcycle.com.br/courses/a091b0fe-a5c6-4287-a3d3-1ec61defcfd3/413/224/291/conteudos?capitulo=291&conteudo=18416): motivou testes de recuperação separados da geração e explicitação de que similaridade não garante resposta correta.
- [Enunciado fase 293](https://plataforma.fullcycle.com.br/courses/a091b0fe-a5c6-4287-a3d3-1ec61defcfd3/413/224/266/conteudos?projeto=70&fase=293): fonte dos parâmetros 1000/150, k=10, prompt e estrutura.
- [Spec Kit oficial](https://github.com/github/spec-kit): workflow instalado, versão 1.0.8.
- [OpenAI embeddings](https://developers.openai.com/api/docs/models/text-embedding-3-small), [modelo de chat](https://developers.openai.com/api/docs/models/gpt-4.1-mini) e [PGVector](https://reference.langchain.com/python/langchain-postgres/vectorstores/PGVector): seleção e contratos técnicos.
