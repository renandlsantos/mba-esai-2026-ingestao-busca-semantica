# Matriz de rastreabilidade

| Requisito | Implementação | Evidência |
|---|---|---|
| FR-001 | ingest.load_pdf | missing_and_invalid_pdf, original_pdf_has_text, empty_document_rejected |
| FR-002 | ingest.chunk_documents | chunk_size_overlap_and_ids, split_overlap_contains_same_characters |
| FR-003 | ingest.ingest_pdf, config.create_store | ingestion_reuses_ids e test_real_pgvector_persistence_upsert_retrieval_and_pdf |
| FR-004 | search.answer_question | retrieval_uses_ten; integração PGVector com 12 documentos retorna 10 |
| FR-005 | search.PROMPT_TEMPLATE | teste inspeciona mensagem, contexto e regra; revisão compara prompt ao starter |
| FR-006 | search.answer_question | contexto/saída vazia; modelo real pendente SC-004 |
| FR-007 | chat.chat_loop | duas perguntas, vazio, sair, EOF/Ctrl-C |
| FR-008 | config.Settings/report_error | configuração inválida e segredos ausentes; erros de CLI sem vazamento |
| FR-009 | README, Compose e tests | Compose saudável, testes e lint; estrutura preservada |

SC-001/002/003 verificados localmente e no banco real. SC-004 depende de credencial e avaliação real antes de entrega. O teste de banco utiliza embeddings de teste e não substitui SC-004.
