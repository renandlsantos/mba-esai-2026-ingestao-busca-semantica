# Modelo de dados

Documento: `sha256` dos bytes, `source` nome do PDF (sem caminho privado).
Trecho: `page_content` não vazio de até 1000 caracteres; metadata `page` inteiro base zero, `chunk_index` inteiro, `document_sha256`, `source`, `embedding_model`. ID: SHA256 de collection + hash PDF + índice.
PGVector gerencia collection e embedding em suas tabelas padrão, com metadados JSONB. Não há migração destrutiva.
Estado: arquivo validado → páginas extraídas → chunks → embeddings → upsert. Falha na rede pode deixar carga parcial: reexecutar o mesmo PDF completa por IDs estáveis. Troca de PDF/modelo deve usar novo banco/collection conforme README, sem excluir dados antigos automaticamente.
Consulta: texto não vazio → top 10 documentos com score → contexto → resposta. Sem documentos/sem saída textual → recusa exata.
