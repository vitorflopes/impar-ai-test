from typing import TYPE_CHECKING
import json
from src.models.chat_model import UserMessage
from src.services.agent.agent import agent
from src.logging_config import get_logger

if TYPE_CHECKING:
    from src.services.pgvector_service import VectorStoreService

logger = get_logger("chat_service")


class ChatService:
    """Serviço de processamento de mensagens do chat com agente IA."""

    async def process_message(
        self, data: UserMessage, vector_store_service: "VectorStoreService"
    ):
        """
        Processa mensagem do usuário e gera resposta via streaming.

        Utiliza o agente ReAct para processar a mensagem, executar ferramentas
        quando necessário e retornar a resposta em chunks via SSE.

        Args:
            data: Mensagem do usuário com content e thread_id.
            vector_store_service: Serviço de busca vetorial para RAG.

        Yields:
            str: Chunks JSON com tipos: 'thinking', 'content', 'tool_call', 'tool_response', 'error'.
        """
        logger.debug("Agent stream started | thread_id=%s", data.thread_id)

        try:
            async for event in agent.astream_events(
                {"messages": [{"role": "user", "content": data.content}]},
                config={
                    "configurable": {
                        "thread_id": data.thread_id,
                        "vector_store": vector_store_service,
                    }
                },
                version="v2",
            ):
                kind = event["event"]

                if kind == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]

                    thinking = chunk.additional_kwargs.get("reasoning_content", "")
                    if thinking:
                        yield (
                            json.dumps(
                                {"type": "thinking", "text": thinking},
                                ensure_ascii=False,
                            )
                            + "\n"
                        )

                    content = chunk.content
                    if content:
                        yield (
                            json.dumps(
                                {"type": "content", "text": content}, ensure_ascii=False
                            )
                            + "\n"
                        )

                elif kind == "on_tool_start":
                    tool_name = event["name"]
                    tool_input = event["data"].get("input", {})
                    logger.debug(
                        "Tool call | thread_id=%s | tool=%s | input=%s",
                        data.thread_id,
                        tool_name,
                        tool_input,
                    )
                    yield (
                        json.dumps(
                            {
                                "type": "tool_call",
                                "tool": tool_name,
                                "input": tool_input,
                            },
                            ensure_ascii=False,
                        )
                        + "\n"
                    )

                elif kind == "on_tool_end":
                    tool_name = event["name"]
                    tool_output = event["data"].get("output", "")
                    logger.debug(
                        "Tool response | thread_id=%s | tool=%s | output_length=%d",
                        data.thread_id,
                        tool_name,
                        len(str(tool_output)),
                    )
                    yield (
                        json.dumps(
                            {
                                "type": "tool_response",
                                "tool": tool_name,
                                "output": str(tool_output),
                            },
                            ensure_ascii=False,
                        )
                        + "\n"
                    )

        except Exception as e:
            logger.error(
                "Agent error | thread_id=%s | error=%s", data.thread_id, str(e)
            )
            yield (
                json.dumps({"type": "error", "text": str(e)}, ensure_ascii=False) + "\n"
            )

