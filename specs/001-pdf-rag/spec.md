# Feature Specification: Consulta fundamentada em PDF

**Feature Branch**: `feature/sdd-fase-293`
**Created**: 2026-09-19
**Status**: Revisada para implementação
**Input**: Fase 293 do MBA: ingerir um PDF e permitir perguntas no terminal fundamentadas apenas nele.

## User Scenarios & Testing

### User Story 1 - Preparar documento (Priority: P1)
Como estudante, quero indexar meu PDF textual para consultá-lo posteriormente.
**Why this priority**: Sem documento indexado não há evidência para responder.
**Independent Test**: Ingerir PDF de exemplo, consultar quantidade e origem dos trechos; repetir e verificar que não duplica.
**Acceptance Scenarios**:
1. **Given** PDF textual válido, **When** executo ingestão, **Then** trechos e origem ficam persistidos.
2. **Given** arquivo inexistente, inválido ou sem texto, **When** executo ingestão, **Then** recebo erro e nenhum sucesso é anunciado.
3. **Given** o mesmo PDF já indexado, **When** repito, **Then** IDs estáveis evitam duplicação.

### User Story 2 - Perguntar com evidência (Priority: P1)
Como estudante, quero receber uma resposta baseada no documento e recusa para informação ausente.
**Why this priority**: É o objetivo central do desafio.
**Independent Test**: Com recuperação controlada, verificar contexto e pergunta enviados; com modelo real executar perguntas cobertas e fora do contexto.
**Acceptance Scenarios**:
1. **Given** documento indexado, **When** pergunto algo coberto, **Then** a aplicação recupera dez candidatos e monta o prompt exigido.
2. **Given** nenhuma evidência, **When** pergunto, **Then** responde exatamente "Não tenho informações necessárias para responder sua pergunta.".
3. **Given** pergunta fora do contexto, **When** o modelo responde, **Then** deve usar a mesma recusa; a qualidade desse comportamento exige avaliação real.

### User Story 3 - Operar pelo terminal (Priority: P2)
Como estudante, quero fazer várias perguntas e encerrar sem rastros de erro.
**Why this priority**: Permite demonstrar e avaliar o entregável.
**Independent Test**: Alimentar entrada vazia, duas perguntas e sair/EOF; simular falha do provedor e verificar código de saída.
**Acceptance Scenarios**:
1. **Given** CLI iniciado, **When** envio duas perguntas, **Then** cada uma produz RESPOSTA e continua até sair.
2. **Given** configuração inválida ou serviço indisponível, **When** inicio/consulto, **Then** recebo diagnóstico seguro em stderr e status não zero.

### Edge Cases
PDF criptografado, PDF sem texto, pergunta vazia, banco sem trechos, resposta vazia do modelo, credencial ausente, troca de embedding e ingestão interrompida. PDF atualizado deve usar nova collection para não misturar versões; não há exclusão automática de dados.

## Requirements

### Functional Requirements
- **FR-001** Ler PDF local textual e rejeitar entrada ausente/inválida/vazia.
- **FR-002** Dividir em trechos de até 1000 caracteres, configurando sobreposição de 150; preservar página e identidade do documento.
- **FR-003** Gerar embeddings e persistir trechos em PostgreSQL com pgVector; repetir ingestão sem duplicação.
- **FR-004** Vetorizar a pergunta e recuperar os dez resultados mais relevantes, ou todos quando houver menos.
- **FR-005** Concatenar os resultados e executar integralmente o prompt exigido pelo enunciado, sem conhecimento externo.
- **FR-006** Usar a recusa exata para informação ausente; contexto vazio não deve chamar o modelo.
- **FR-007** Expor ingestão e chat CLI com saída legível, múltiplas perguntas e encerramento por sair, EOF ou Ctrl-C.
- **FR-008** Configurar credenciais, modelos, PDF e banco por ambiente, com diagnóstico seguro de falhas.
- **FR-009** Preservar estrutura do starter, Docker Compose, instruções reproduzíveis e testes automatizados.

### Key Entities
- Documento: PDF identificado por hash de conteúdo e nome.
- Trecho: texto, página, índice, hash do PDF e ID estável.
- Consulta: pergunta, candidatos recuperados e resposta ou recusa.

## Success Criteria

### Measurable Outcomes
- **SC-001** Ingestão repetida mantém a mesma quantidade de trechos para o mesmo PDF.
- **SC-002** Todos os trechos têm até 1000 caracteres e são rastreáveis à página.
- **SC-003** Casos vazios, saída do terminal e indisponibilidade são cobertos por testes sem credenciais.
- **SC-004** Antes da submissão, um operador demonstra uma pergunta coberta e três ausentes com o modelo real, registrando modelo, data e resultados sem segredos.

## Assumptions
Operação monousuário e PDF textual fornecido no starter. Sem OCR. Modelos e credenciais são responsabilidade do operador. A arquitetura não garante ausência absoluta de alucinação; testes reais são um gate de entrega, não substituídos por mocks. Tecnologias obrigatórias do enunciado são restrições do plano, não escolhas abertas.
