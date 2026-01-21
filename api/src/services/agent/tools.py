from typing import TYPE_CHECKING
from langchain.tools import tool
from langchain_core.runnables import RunnableConfig
from src.logging_config import get_logger

if TYPE_CHECKING:
    from src.services.pgvector_service import VectorStoreService

logger = get_logger("agent.tools")


@tool
def search_documents(
    query: str, k: int, config: RunnableConfig, file_name: str | None = None
) -> str:
    """
    Busca informações relevantes na base de conhecimento do usuário (RAG).

    **Propósito Principal:**
    Realiza uma busca semântica no banco vetorial para encontrar trechos
    que sejam mais relevantes para responder à pergunta do usuário.

    **Argumentos:**
    - query (str): A pergunta ou termo de busca para encontrar informações.
    - k (int): O número de trechos (chunks) a serem recuperados.
               Recomendado: 4 a 6.
    - file_name (str | None): Opcional. Nome da fonte para restringir a busca.

    **Retorno:**
    - str: Uma string contendo os trechos encontrados, formatados com metadados:
           "--- Fonte: {nome} | Localização: {contexto} ---"
           seguido pelo conteúdo do trecho.
           Se nada for encontrado, retorna uma mensagem indicando isso.

    **Cenários de Uso:**
    - **Busca Geral:** O usuário pergunta sobre um tema.
        -> `search_documents("lucro líquido 2023", k=4)`
    - **Busca Filtrada:** O usuário quer buscar em uma fonte específica.
        -> `search_documents("cláusulas rescisão", k=4, file_name="contrato.pdf")`

    **Notas Importantes:**
    - O conteúdo retornado é o "contexto" que você deve usar para formular sua resposta ao usuário.
    """
    logger.debug(
        "search_documents called | query=%s | k=%d | file_name=%s",
        query[:50],
        k,
        file_name,
    )

    try:
        vector_store: "VectorStoreService" = config["configurable"].get("vector_store")
        if not vector_store:
            logger.error("VectorStoreService not available in config")
            return "Serviço de busca indisponível."

        if file_name and not vector_store.document_exists(file_name):
            available_files = vector_store.list_files()
            files_list = (
                ", ".join(available_files)
                if available_files
                else "nenhuma fonte disponível"
            )
            logger.warning(
                "File not found | file_name=%s | available=%s", file_name, files_list
            )
            return (
                f"❌ Fonte '{file_name}' não encontrada na base de conhecimento. "
                f"Verifique se o nome está correto. "
                f"Fontes disponíveis: {files_list}"
            )

        docs = vector_store.search(query, k=k, filter_by_file=file_name)

        if not docs:
            logger.info("No documents found | query=%s | file_name=%s", query[:50], file_name)
            return "Nenhuma informação relevante encontrada nos documentos."

        logger.info(
            "Documents found | query=%s | results=%d", query[:50], len(docs)
        )

        results = []
        for doc in docs:
            source = doc.metadata.get("source")
            page = doc.metadata.get("location")

            location = f"{page}" if page else "Contexto Geral"

            results.append(
                f"--- Documento: {source} | Localização: {location} ---\n{doc.page_content}"
            )

        return "\n\n".join(results)

    except Exception as e:
        logger.error("search_documents failed | query=%s | error=%s", query[:50], str(e))
        return f"Erro ao buscar documentos: {str(e)}"

