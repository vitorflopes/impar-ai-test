from litestar import Controller, post
from litestar.response import ServerSentEvent
from litestar.datastructures import UploadFile
from litestar.enums import RequestEncodingType
from litestar.params import Body

from src.services.chat_service import ChatService
from src.services.ingestion_service import IngestionService
from src.services.pgvector_service import VectorStoreService
from src.models.chat_model import UserMessage, UploadResponse
from src.logging_config import get_logger

logger = get_logger("chat_controller")


class ChatController(Controller):
    """Controller para endpoints de chat e upload de arquivos."""

    path = "/chat"

    @post()
    async def handle_chat(
        self,
        data: UserMessage,
        chat_service: ChatService,
        vector_store_service: VectorStoreService,
    ) -> ServerSentEvent:
        """
        Processa mensagens do usuário e retorna resposta via streaming (SSE).

        Args:
            data: Mensagem do usuário contendo content e thread_id.
            chat_service: Serviço de processamento de chat com agente.
            vector_store_service: Serviço de busca vetorial.

        Returns:
            ServerSentEvent: Stream de eventos com a resposta do agente.
        """
        logger.info(
            "Chat request received | thread_id=%s | content_length=%d",
            data.thread_id,
            len(data.content),
        )
        logger.debug(
            "Chat content | thread_id=%s | content=%s",
            data.thread_id,
            data.content[:100],
        )

        async def event_generator():
            chunk_count = 0
            async for chunk in chat_service.process_message(data, vector_store_service):
                chunk_count += 1
                yield chunk.strip()
            logger.info(
                "Chat response completed | thread_id=%s | chunks_sent=%d",
                data.thread_id,
                chunk_count,
            )

        return ServerSentEvent(event_generator())

    @post(path="/upload")
    async def handle_file_upload(
        self,
        ingestion_service: IngestionService,
        vector_store_service: VectorStoreService,
        data: list[UploadFile] = Body(media_type=RequestEncodingType.MULTI_PART),
    ) -> UploadResponse:
        """
        Processa upload de arquivos, extrai conteúdo e armazena no vector store.

        Formatos suportados: PDF, CSV, Excel, Word, PowerPoint, HTML, JSON, TXT, Markdown e Imagens (OCR).

        Args:
            ingestion_service: Serviço de ingestão e extração de conteúdo.
            vector_store_service: Serviço de armazenamento vetorial.
            data: Lista de arquivos enviados via multipart/form-data.

        Returns:
            UploadResponse: Status do processamento com quantidade de chunks gerados.
        """
        file_info = [{"name": f.filename, "type": f.content_type} for f in data]
        logger.info(
            "File upload received | files=%d | details=%s", len(data), file_info
        )

        chunks = await ingestion_service.process_file(files_data=data)
        logger.info(
            "File processing completed | files=%d | chunks_generated=%d",
            len(data),
            len(chunks),
        )

        vector_store_service.add_documents(chunks)
        logger.info("Documents added to vector store | chunks=%d", len(chunks))

        return UploadResponse(
            filename=", ".join([file.filename for file in data]),
            chunks_generated=len(chunks),
            status="Processado e vetorizado com sucesso!",
        )
