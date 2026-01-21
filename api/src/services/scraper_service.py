import os
from anyio import to_thread
import requests
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.logging_config import get_logger

logger = get_logger("scraper_service")


class ScraperService:
    """Serviço de scraping de páginas web."""

    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, separators=["\n\n", "\n", " ", ""]
        )
        self.default_url = os.getenv("SCRAPE_URL")
        logger.info("ScraperService initialized | default_url=%s", self.default_url)

    async def scrape_and_chunk(self, url: str | None = None) -> list[Document]:
        """
        Realiza scraping de uma URL e retorna conteúdo em chunks.

        Atualmente otimizado para páginas da Wikipedia.

        Args:
            url: URL para scraping. Usa default_url se não informada.

        Returns:
            list[Document]: Lista de chunks prontos para vetorização.

        Raises:
            RequestException: Se falhar ao buscar a URL.
            ValueError: Se não conseguir extrair conteúdo.
        """
        target_url = url or self.default_url
        logger.info("Starting scrape | url=%s", target_url)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        }

        def fetch_url():
            resp = requests.get(target_url, headers=headers, timeout=10)
            resp.raise_for_status()
            return resp.text

        try:
            html_content = await to_thread.run_sync(fetch_url)
            logger.debug("Fetched HTML | url=%s | length=%d", target_url, len(html_content))
        except requests.RequestException as e:
            logger.error("Failed to fetch URL | url=%s | error=%s", target_url, str(e))
            raise

        try:
            text_content = self._parse_wikipedia(html_content)

            if not text_content:
                logger.error("No content extracted | url=%s", target_url)
                raise ValueError("Não foi possível extrair conteúdo da página.")

            logger.debug(
                "Parsed content | url=%s | text_length=%d", target_url, len(text_content)
            )

            raw_doc = Document(
                page_content=text_content,
                metadata={
                    "source": target_url,
                    "location": "Wikipedia",
                    "type": "web_scrape",
                },
            )

            chunks = self.text_splitter.split_documents([raw_doc])
            logger.info("Scrape completed | url=%s | chunks=%d", target_url, len(chunks))

            return chunks
        except Exception as e:
            logger.error("Scraping failed | url=%s | error=%s", target_url, str(e))
            raise

    def _parse_wikipedia(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")

        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()

        content_div = soup.find("div", {"id": "bodyContent"})
        if not content_div:
            logger.warning("bodyContent not found, using body as fallback")
            content_div = soup.body

        for ref in content_div.find_all("sup", class_="reference"):
            ref.decompose()
        text = content_div.get_text(separator="\n", strip=True)

        return text

