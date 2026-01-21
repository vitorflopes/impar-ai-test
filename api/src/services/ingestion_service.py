import io
import pdfplumber
import platform
import pytesseract
from PIL import Image
import pandas as pd
from litestar.datastructures import UploadFile
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from markitdown import MarkItDown
from src.logging_config import get_logger

logger = get_logger("ingestion_service")

MARKITDOWN_EXTENSIONS = {
    ".docx",
    ".pptx",
    ".html",
    ".json",
    ".txt",
    ".text",
    ".md",
    ".markdown",
}


class IngestionService:
    """Serviço de ingestão e extração de conteúdo de arquivos."""

    def __init__(self) -> None:
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, separators=["\n\n", "\n", " ", ""]
        )
        self.markitdown = MarkItDown()
        if platform.system() == "Windows":
            logger.info("Setting Tesseract path for Windows")
            pytesseract.pytesseract.tesseract_cmd = (
                r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            )

    async def process_file(self, files_data: list[UploadFile]) -> list[Document]:
        """
        Processa lista de arquivos e extrai conteúdo como Documents.

        Suporta: PDF, CSV, Excel, Word, PowerPoint, HTML, JSON, TXT, Markdown e Imagens (OCR).

        Args:
            files_data: Lista de arquivos UploadFile.

        Returns:
            list[Document]: Lista de chunks prontos para vetorização.

        Raises:
            ValueError: Se formato de arquivo não é suportado.
        """
        all_raw_documents = []

        for file_data in files_data:
            content = await file_data.read()
            filename = file_data.filename.lower()
            logger.info("Processing file | filename=%s", filename)

            try:
                if filename.endswith(".pdf"):
                    all_raw_documents.extend(self._extract_from_pdf(content, filename))
                elif filename.endswith(".csv"):
                    all_raw_documents.extend(self._extract_from_csv(content, filename))
                elif filename.endswith(".xlsx") or filename.endswith(".xls"):
                    all_raw_documents.extend(
                        self._extract_from_excel(content, filename)
                    )
                elif filename.endswith((".png", ".jpg", ".jpeg", ".tiff", ".bmp")):
                    all_raw_documents.extend(
                        self._extract_from_image(content, filename)
                    )
                elif any(filename.endswith(ext) for ext in MARKITDOWN_EXTENSIONS):
                    all_raw_documents.extend(
                        self._extract_with_markitdown(content, filename)
                    )
                else:
                    logger.error("Unsupported file format | filename=%s", filename)
                    raise ValueError(f"Formato de arquivo não suportado: {filename}")
            except Exception as e:
                logger.error(
                    "Failed to process file | filename=%s | error=%s", filename, str(e)
                )
                raise

        chunks = self.text_splitter.split_documents(all_raw_documents)
        logger.info(
            "Chunking completed | documents=%d | chunks=%d",
            len(all_raw_documents),
            len(chunks),
        )

        return chunks

    def _extract_from_pdf(self, file_bytes: bytes, filename: str) -> list[Document]:
        try:
            docs = []
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        doc = Document(
                            page_content=page_text,
                            metadata={
                                "source": filename,
                                "location": "página " + str(i + 1),
                                "type": "pdf",
                            },
                        )
                        docs.append(doc)
            logger.debug("PDF extracted | filename=%s | pages=%d", filename, len(docs))
            return docs
        except Exception as e:
            logger.error("PDF extraction failed | filename=%s | error=%s", filename, str(e))
            raise

    def _extract_from_csv(self, file_bytes: bytes, filename: str) -> list[Document]:
        try:
            df = pd.read_csv(io.BytesIO(file_bytes))
            docs = self._process_dataframe(df, filename, "csv")
            logger.debug("CSV extracted | filename=%s | rows=%d", filename, len(docs))
            return docs
        except Exception as e:
            logger.error("CSV extraction failed | filename=%s | error=%s", filename, str(e))
            raise

    def _extract_from_excel(self, file_bytes: bytes, filename: str) -> list[Document]:
        try:
            df = pd.read_excel(io.BytesIO(file_bytes))
            docs = self._process_dataframe(df, filename, "excel")
            logger.debug("Excel extracted | filename=%s | rows=%d", filename, len(docs))
            return docs
        except Exception as e:
            logger.error("Excel extraction failed | filename=%s | error=%s", filename, str(e))
            raise

    def _process_dataframe(
        self, df: pd.DataFrame, filename: str, file_type: str
    ) -> list[Document]:
        df = df.fillna("")

        docs = []

        rows = df.to_dict(orient="records")

        for i, row in enumerate(rows):
            content_parts = []
            for col, val in row.items():
                if val != "":
                    content_parts.append(f"{col}: {val}")

            page_content = "\n".join(content_parts)

            if page_content.strip():
                doc = Document(
                    page_content=page_content,
                    metadata={
                        "source": filename,
                        "location": "linha " + str(i + 1),
                        "type": file_type,
                    },
                )
                docs.append(doc)

        return docs

    def _extract_from_image(self, file_bytes: bytes, filename: str) -> list[Document]:
        try:
            image = Image.open(io.BytesIO(file_bytes))
            text = pytesseract.image_to_string(image, lang="por+eng")

            if not text.strip():
                logger.warning("OCR returned empty text | filename=%s", filename)
                return []

            logger.debug(
                "Image OCR completed | filename=%s | text_length=%d",
                filename,
                len(text),
            )
            return [
                Document(
                    page_content=text,
                    metadata={
                        "source": filename,
                        "location": "imagem completa",
                        "type": "image_ocr",
                    },
                )
            ]
        except Exception as e:
            logger.error("Image OCR failed | filename=%s | error=%s", filename, str(e))
            return []

    def _extract_with_markitdown(
        self, file_bytes: bytes, filename: str
    ) -> list[Document]:
        try:
            ext = "." + filename.rsplit(".", 1)[-1] if "." in filename else ""

            stream = io.BytesIO(file_bytes)
            result = self.markitdown.convert_stream(stream, file_extension=ext)

            markdown_content = result.text_content

            if not markdown_content or not markdown_content.strip():
                logger.warning("MarkItDown returned empty content | filename=%s", filename)
                return []

            logger.debug(
                "MarkItDown converted | filename=%s | content_length=%d",
                filename,
                len(markdown_content),
            )
            return [
                Document(
                    page_content=markdown_content,
                    metadata={
                        "source": filename,
                        "location": "documento completo",
                        "type": ext.lstrip("."),
                    },
                )
            ]
        except Exception as e:
            logger.error(
                "MarkItDown conversion failed | filename=%s | error=%s", filename, str(e)
            )
            raise

