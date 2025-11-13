"""
Document ingestion and processing service
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import base64
import tempfile
import requests
from bs4 import BeautifulSoup
import html2text

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from loguru import logger

from app.config import settings
from app.services.vector_store import VectorStoreService


class DocumentService:
    """Service for document ingestion and processing"""

    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        self.vector_store = VectorStoreService.get_instance()

    async def ingest_pdf(
        self,
        document_id: int,
        file_path: Optional[str] = None,
        file_content: Optional[str] = None,
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ingest a PDF document

        Args:
            document_id: Moodle document ID
            file_path: Path to PDF file (if local)
            file_content: Base64 encoded file content
            filename: Original filename

        Returns:
            Ingestion result with chunk count
        """
        logger.info(f"Ingesting PDF document {document_id}")

        try:
            # Handle base64 encoded content
            if file_content:
                content = base64.b64decode(file_content)
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(content)
                    file_path = tmp_file.name

            if not file_path or not Path(file_path).exists():
                raise ValueError("Invalid file path")

            # Load PDF
            loader = PyPDFLoader(file_path)
            documents = loader.load()

            # Extract text and metadata
            texts = []
            metadatas = []

            for i, doc in enumerate(documents):
                texts.append(doc.page_content)
                metadatas.append({
                    'source': filename or Path(file_path).name,
                    'page': i + 1,
                    'type': 'pdf'
                })

            # Split into chunks
            chunks = self.text_splitter.create_documents(texts, metadatas)

            # Prepare for vector store
            chunk_texts = [chunk.page_content for chunk in chunks]
            chunk_metadatas = [chunk.metadata for chunk in chunks]

            # Add to vector store
            num_chunks = await self.vector_store.add_documents(
                texts=chunk_texts,
                metadatas=chunk_metadatas,
                document_id=document_id
            )

            logger.info(f"✓ Successfully ingested PDF: {num_chunks} chunks")

            return {
                'success': True,
                'chunks': num_chunks,
                'pages': len(documents)
            }

        except Exception as e:
            logger.error(f"Failed to ingest PDF: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def ingest_url(
        self,
        document_id: int,
        url: str
    ) -> Dict[str, Any]:
        """
        Ingest content from a URL

        Args:
            document_id: Moodle document ID
            url: URL to ingest

        Returns:
            Ingestion result with chunk count
        """
        logger.info(f"Ingesting URL: {url}")

        try:
            # Fetch URL content
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Convert to markdown
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = True
            text = h.handle(str(soup))

            # Clean up text
            text = '\n'.join([line.strip() for line in text.split('\n') if line.strip()])

            # Split into chunks
            chunks = self.text_splitter.split_text(text)

            # Prepare metadata
            metadatas = [{
                'source': url,
                'type': 'url',
                'title': soup.title.string if soup.title else url
            } for _ in chunks]

            # Add to vector store
            num_chunks = await self.vector_store.add_documents(
                texts=chunks,
                metadatas=metadatas,
                document_id=document_id
            )

            logger.info(f"✓ Successfully ingested URL: {num_chunks} chunks")

            return {
                'success': True,
                'chunks': num_chunks,
                'title': soup.title.string if soup.title else url
            }

        except Exception as e:
            logger.error(f"Failed to ingest URL: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def delete_document(self, document_id: int) -> bool:
        """
        Delete a document from the vector store

        Args:
            document_id: Moodle document ID

        Returns:
            Success status
        """
        logger.info(f"Deleting document {document_id}")
        return await self.vector_store.delete_document(document_id)
