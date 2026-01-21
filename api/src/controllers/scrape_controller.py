from litestar import Controller, post
from src.services.scraper_service import ScraperService
from src.services.pgvector_service import VectorStoreService
from src.models.scrape_model import ScrapeRequest, ScrapeResponse
from src.logging_config import get_logger

logger = get_logger("scrape_controller")


class ScrapeController(Controller):
    """Controller para scraping de páginas web."""

    path = "/scrape"

    @post()
    async def handle_scrape(
        self,
        data: ScrapeRequest,
        scraper_service: ScraperService,
        vector_store_service: VectorStoreService,
    ) -> ScrapeResponse:
        """
        Realiza scraping de uma URL e armazena o conteúdo no vector store.

        Verifica se a URL já foi processada anteriormente para evitar duplicação.
        Atualmente otimizado para páginas da Wikipedia.

        Args:
            data: Request contendo URL opcional (usa default se não informada).
            scraper_service: Serviço de scraping e chunking.
            vector_store_service: Serviço de armazenamento vetorial.

        Returns:
            ScrapeResponse: Status da operação com quantidade de chunks gerados.
        """
        target_url = data.url or scraper_service.default_url
        logger.info("Scrape request received | url=%s", target_url)

        if vector_store_service.document_exists(target_url):
            logger.info("Scrape skipped (already exists) | url=%s", target_url)
            return ScrapeResponse(
                status="success",
                message="O scraping deste site já foi realizado anteriormente.",
                source=target_url,
            )

        chunks = await scraper_service.scrape_and_chunk(url=target_url)
        logger.info("Scrape completed | url=%s | chunks=%d", target_url, len(chunks))

        vector_store_service.add_documents(chunks)
        logger.info("Documents added to vector store | chunks=%d", len(chunks))

        return ScrapeResponse(
            status="success",
            message="Scraping realizado com sucesso!",
            chunks_added=len(chunks),
            source=target_url,
        )
