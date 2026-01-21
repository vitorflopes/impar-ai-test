from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage
import os

from .prompt import SYSTEM_PROMPT_BASE
from .tools import search_documents


model = ChatOllama(
    model=os.getenv("OLLAMA_MODEL"),
    temperature=os.getenv("OLLAMA_TEMP"),
    base_url=os.getenv("OLLAMA_HOST"),
    reasoning=True,
)
checkpointer = InMemorySaver()


def dynamic_prompt(state, config):
    """
    Constrói o prompt do sistema dinamicamente com a lista de arquivos disponíveis.

    Injeta a lista de fontes da base de conhecimento no prompt base,
    permitindo que o agente saiba quais documentos estão disponíveis para consulta.

    Args:
        state: Estado atual do agente contendo mensagens.
        config: Configuração com acesso ao vector_store via configurable.

    Returns:
        list: Lista de mensagens começando com SystemMessage seguido das mensagens do usuário.
    """
    vector_store = config.get("configurable").get("vector_store")

    files = vector_store.list_files()
    files_section = (
        "\n".join(f"- {f}" for f in files) if files else "Nenhuma fonte disponível."
    )

    dynamic_prompt_text = SYSTEM_PROMPT_BASE.format(available_files=files_section)

    return [SystemMessage(content=dynamic_prompt_text)] + state["messages"]


agent = create_react_agent(
    model=model,
    tools=[search_documents],
    prompt=dynamic_prompt,
    checkpointer=checkpointer,
)
