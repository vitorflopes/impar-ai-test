import os
from langchain_core.documents import Document
from langchain_postgres import PGVector
from langchain_huggingface import HuggingFaceEmbeddings
from sqlalchemy import text
from src.logging_config import get_logger

logger = get_logger("pgvector_service")


class VectorStoreService:
    """Serviço de armazenamento e busca vetorial usando PGVector."""

    def __init__(self):
        self.connection_string = os.getenv("PGVECTOR_DATABASE_URL")
        self.collection_name = os.getenv("PGVECTOR_COLLECTION_NAME")

        logger.info(
            "Initializing VectorStoreService | collection=%s", self.collection_name
        )

        self.embeddings = HuggingFaceEmbeddings(
            model_name=os.getenv("HUGGINGFACE_MODEL_NAME")
        )

        self.store = PGVector(
            embeddings=self.embeddings,
            collection_name=self.collection_name,
            connection=self.connection_string,
            use_jsonb=True,
            create_extension=False,
        )

    def add_documents(self, documents: list[Document]):
        """
        Adiciona documentos ao vector store.

        Args:
            documents: Lista de documentos a serem adicionados.

        Raises:
            ValueError: Se a lista de documentos estiver vazia.
            Exception: Se falhar ao adicionar documentos.
        """
        if not documents:
            logger.debug("add_documents called with empty list, skipping")
            return

        try:
            self.store.add_documents(documents)
            logger.info("Documents added to vector store | count=%d", len(documents))
        except Exception as e:
            logger.error("Failed to add documents | error=%s", str(e))
            raise

    def search(
        self, query: str, k: int = 4, filter_by_file: str | None = None
    ) -> list[Document]:
        """
        Realiza busca por similaridade no vector store.

        Args:
            query: Texto de busca.
            k: Número de resultados a retornar.
            filter_by_file: Filtrar por fonte específica.

        Returns:
            list[Document]: Documentos mais similares à query.
        """
        try:
            filter_dict = None
            if filter_by_file:
                filter_dict = {"source": filter_by_file}

            docs = self.store.similarity_search(query, k=k, filter=filter_dict)
            logger.debug(
                "Search completed | query=%s | k=%d | filter=%s | results=%d",
                query[:50],
                k,
                filter_by_file,
                len(docs),
            )
            return docs
        except Exception as e:
            logger.error(
                "Search failed | query=%s | error=%s", query[:50], str(e)
            )
            raise

    def list_files(self) -> list[str]:
        """
        Lista todas as fontes (arquivos/URLs) armazenadas.

        Returns:
            list[str]: Lista de nomes de fontes únicas.
        """
        try:
            with self.store.session_maker() as session:
                collection = self.store.get_collection(session)

                if not collection:
                    logger.warning("No collection found")
                    return []

                query = text("""
                    SELECT DISTINCT cmetadata ->> 'source' as source
                    FROM langchain_pg_embedding
                    WHERE collection_id = :collection_id
                      AND cmetadata ->> 'source' IS NOT NULL
                """)

                result = session.execute(query, {"collection_id": collection.uuid})
                files = [row[0] for row in result.fetchall()]
                logger.debug("Listed files | count=%d", len(files))
                return files
        except Exception as e:
            logger.error("Failed to list files | error=%s", str(e))
            raise

    def document_exists(self, source: str) -> bool:
        """
        Verifica se uma fonte já existe no vector store.

        Args:
            source: Nome da fonte (arquivo ou URL).

        Returns:
            bool: True se existe, False caso contrário.
        """
        try:
            with self.store.session_maker() as session:
                collection = self.store.get_collection(session)
                if not collection:
                    return False

                query = text("""
                    SELECT 1
                    FROM langchain_pg_embedding
                    WHERE collection_id = :collection_id
                      AND cmetadata ->> 'source' = :source
                    LIMIT 1
                """)

                result = session.execute(
                    query, {"collection_id": collection.uuid, "source": source}
                )
                exists = bool(result.scalar())
                logger.debug("Document exists check | source=%s | exists=%s", source, exists)
                return exists
        except Exception as e:
            logger.error("Failed to check document exists | source=%s | error=%s", source, str(e))
            raise

