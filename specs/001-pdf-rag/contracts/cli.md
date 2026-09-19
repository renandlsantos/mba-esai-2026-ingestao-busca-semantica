# Contrato CLI

`python src/ingest.py`: usa PDF_PATH (default document.pdf); sucesso stdout contém quantidade de trechos e status 0. Falha stderr seguro, status 1.
`python src/chat.py`: imprime Faça sua pergunta e PERGUNTA; ignora linhas vazias; RESPOSTA por pergunta; sair/exit/quit/EOF/Ctrl-C encerram com 0. Falha de configuração, banco ou provedor encerra com 1.
`python src/search.py "pergunta"`: consulta única para inspeção; saída resposta, status 0; pergunta vazia/erro status 1.
Configuração: OPENAI_API_KEY obrigatória; OPENAI_EMBEDDING_MODEL e OPENAI_CHAT_MODEL; DATABASE_URL postgresql+psycopg; PG_VECTOR_COLLECTION_NAME; PDF_PATH. Nenhuma credencial em logs.
Recusa: Não tenho informações necessárias para responder sua pergunta.
