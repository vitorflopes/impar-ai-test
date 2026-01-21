from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.di import Provide

from src.controllers.chat_controller import ChatController
from src.controllers.scrape_controller import ScrapeController
from src.services.chat_service import ChatService
from src.services.ingestion_service import IngestionService
from src.services.pgvector_service import VectorStoreService
from src.services.scraper_service import ScraperService
from src.logging_config import setup_logging


setup_logging()

cors_config = CORSConfig(allow_origins=["*"])


app = Litestar(
    route_handlers=[ChatController, ScrapeController],
    cors_config=cors_config,
    debug=True,
    dependencies={
        "chat_service": Provide(ChatService),
        "ingestion_service": Provide(IngestionService, sync_to_thread=True),
        "vector_store_service": Provide(VectorStoreService, sync_to_thread=True),
        "scraper_service": Provide(ScraperService),
    },
)
