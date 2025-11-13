"""
Qdrant vector store service for RAG
"""
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from loguru import logger
import uuid

from app.config import settings


class VectorStoreService:
    """Singleton service for managing vector store operations"""

    _instance = None

    def __init__(self):
        self.client: Optional[QdrantClient] = None
        self.embeddings: Optional[OpenAIEmbeddings] = None
        self.vector_store: Optional[QdrantVectorStore] = None
        self.initialized = False

    @classmethod
    def get_instance(cls):
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def initialize(self):
        """Initialize Qdrant client and create collection if needed"""
        if self.initialized:
            return

        try:
            # Initialize Qdrant client
            self.client = QdrantClient(
                host=settings.qdrant_host,
                port=settings.qdrant_port,
                api_key=settings.qdrant_api_key,
                timeout=30.0
            )

            # Initialize embeddings
            self.embeddings = OpenAIEmbeddings(
                model=settings.openai_embedding_model,
                openai_api_key=settings.openai_api_key
            )

            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]

            if settings.qdrant_collection_name not in collection_names:
                logger.info(f"Creating collection: {settings.qdrant_collection_name}")
                self.client.create_collection(
                    collection_name=settings.qdrant_collection_name,
                    vectors_config=VectorParams(
                        size=settings.qdrant_vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info("✓ Collection created")
            else:
                logger.info(f"✓ Collection already exists: {settings.qdrant_collection_name}")

            # Initialize LangChain vector store wrapper
            self.vector_store = QdrantVectorStore(
                client=self.client,
                collection_name=settings.qdrant_collection_name,
                embedding=self.embeddings
            )

            self.initialized = True
            logger.info("✓ Vector store service initialized")

        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise

    async def add_documents(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        document_id: int
    ) -> int:
        """
        Add documents to vector store

        Args:
            texts: List of text chunks
            metadatas: List of metadata dicts for each chunk
            document_id: Moodle document ID

        Returns:
            Number of chunks added
        """
        if not self.initialized:
            await self.initialize()

        try:
            # Add document_id to all metadatas
            for meta in metadatas:
                meta['document_id'] = document_id

            # Generate embeddings and add to Qdrant
            embeddings_list = await self.embeddings.aembed_documents(texts)

            points = []
            for i, (text, embedding, metadata) in enumerate(zip(texts, embeddings_list, metadatas)):
                point_id = str(uuid.uuid4())
                points.append(
                    PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload={
                            'text': text,
                            'metadata': metadata,
                            'document_id': document_id
                        }
                    )
                )

            self.client.upsert(
                collection_name=settings.qdrant_collection_name,
                points=points
            )

            logger.info(f"✓ Added {len(points)} chunks for document {document_id}")
            return len(points)

        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise

    async def search(
        self,
        query: str,
        top_k: int = None,
        score_threshold: float = None,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents

        Args:
            query: Search query
            top_k: Number of results to return
            score_threshold: Minimum similarity score
            filter_dict: Optional filters

        Returns:
            List of search results with text and metadata
        """
        if not self.initialized:
            await self.initialize()

        top_k = top_k or settings.rag_top_k
        score_threshold = score_threshold or settings.rag_score_threshold

        try:
            # Generate query embedding
            query_embedding = await self.embeddings.aembed_query(query)

            # Search in Qdrant
            search_results = self.client.search(
                collection_name=settings.qdrant_collection_name,
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=score_threshold,
                query_filter=self._build_filter(filter_dict) if filter_dict else None
            )

            results = []
            for result in search_results:
                results.append({
                    'text': result.payload.get('text', ''),
                    'metadata': result.payload.get('metadata', {}),
                    'score': result.score
                })

            logger.info(f"✓ Found {len(results)} results for query: {query[:50]}...")
            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    async def delete_document(self, document_id: int) -> bool:
        """
        Delete all chunks for a document

        Args:
            document_id: Moodle document ID

        Returns:
            Success status
        """
        if not self.initialized:
            await self.initialize()

        try:
            self.client.delete(
                collection_name=settings.qdrant_collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="document_id",
                            match=MatchValue(value=document_id)
                        )
                    ]
                )
            )

            logger.info(f"✓ Deleted all chunks for document {document_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False

    def _build_filter(self, filter_dict: Dict) -> Filter:
        """Build Qdrant filter from dict"""
        conditions = []
        for key, value in filter_dict.items():
            conditions.append(
                FieldCondition(
                    key=key,
                    match=MatchValue(value=value)
                )
            )
        return Filter(must=conditions)

    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        if not self.initialized:
            await self.initialize()

        try:
            info = self.client.get_collection(settings.qdrant_collection_name)
            return {
                'vectors_count': info.vectors_count,
                'points_count': info.points_count,
                'status': info.status
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}
