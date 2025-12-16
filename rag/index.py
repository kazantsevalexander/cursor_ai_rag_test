"""
Vector Index for RAG.
Creates and manages embeddings using ChromaDB.
"""

from typing import List, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from config import DATA_DIR, OPENAI_API_KEY, OPENAI_BASE_URL, DOCUMENTS_DIR, EMBEDDING_MODEL
from utils.logging import logger
from rag.loader import document_loader


class VectorIndex:
    """Manages vector embeddings and similarity search."""
    
    def __init__(self, persist_directory: Optional[Path] = None):
        """
        Initialize vector index.
        
        Args:
            persist_directory: Directory to persist embeddings
        """
        if persist_directory is None:
            persist_directory = DATA_DIR / "chroma_db"
        
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize embeddings (always use direct OpenAI API with latest model)
        self.embeddings = OpenAIEmbeddings(
            model=EMBEDDING_MODEL,
            openai_api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL
        )
        
        # Initialize or load vector store
        self.vectorstore = None
        self._load_or_create_vectorstore()
    
    def _load_or_create_vectorstore(self):
        """Load existing vectorstore or create new one."""
        try:
            # Try to load existing vectorstore
            self.vectorstore = Chroma(
                persist_directory=str(self.persist_directory),
                embedding_function=self.embeddings
            )
            logger.info("Loaded existing vector store")
        except Exception as e:
            logger.warning(f"Could not load existing vectorstore: {e}")
            # Create new vectorstore
            self.vectorstore = Chroma(
                persist_directory=str(self.persist_directory),
                embedding_function=self.embeddings
            )
            logger.info("Created new vector store")
    
    def add_documents(self, documents: List) -> None:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of document chunks
        """
        try:
            if not documents:
                logger.warning("No documents to add")
                return
            
            logger.info(f"Starting to add {len(documents)} documents to vector store...")
            logger.info("This may take a while as embeddings are being generated via OpenAI API...")
            
            self.vectorstore.add_documents(documents)
            
            logger.info(f"Successfully added {len(documents)} documents to vector store")
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}", exc_info=True)
            raise
    
    def similarity_search(
        self,
        query: str,
        k: int = 3
    ) -> List:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            k: Number of results to return
        
        Returns:
            List of relevant document chunks
        """
        try:
            results = self.vectorstore.similarity_search(query, k=k)
            logger.debug(f"Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            raise
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 3
    ) -> List[tuple]:
        """
        Search for similar documents with relevance scores.
        
        Args:
            query: Search query
            k: Number of results to return
        
        Returns:
            List of (document, score) tuples
        """
        try:
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            logger.debug(f"Found {len(results)} similar documents with scores")
            return results
            
        except Exception as e:
            logger.error(f"Error in similarity search with scores: {e}")
            raise
    
    def index_documents_directory(
        self,
        directory: Path = DOCUMENTS_DIR,
        force_reindex: bool = False
    ) -> int:
        """
        Index all documents from a directory.
        
        Args:
            directory: Directory containing documents
            force_reindex: If True, clear existing index first
        
        Returns:
            Number of documents indexed
        """
        try:
            logger.info(f"index_documents_directory called with force_reindex={force_reindex}")
            
            # Clear existing index if requested
            if force_reindex:
                logger.info("Clearing existing index")
                self.clear_index()
            
            # Check if index already has documents
            logger.info("Checking if vector store already has documents...")
            try:
                existing_count = self.vectorstore._collection.count()
                logger.info(f"Current document count in vector store: {existing_count}")
                if existing_count > 0 and not force_reindex:
                    logger.info(f"Vector store already contains {existing_count} documents. Skipping reindexing (use force_reindex=True to reindex).")
                    return existing_count
            except Exception as e:
                logger.warning(f"Could not check existing document count: {e}", exc_info=True)
                logger.info("Continuing with indexing despite count check failure...")
            
            # Load documents
            logger.info(f"Loading documents from {directory}...")
            documents = document_loader.load_directory(directory)
            logger.info(f"Document loader returned {len(documents) if documents else 0} documents")
            
            if not documents:
                logger.warning("No documents found to index")
                return 0
            
            # Add to vector store
            logger.info(f"Adding {len(documents)} document chunks to vector store...")
            self.add_documents(documents)
            
            logger.info(f"Successfully indexed {len(documents)} document chunks")
            return len(documents)
            
        except Exception as e:
            logger.error(f"Error indexing documents: {e}", exc_info=True)
            raise
    
    def clear_index(self):
        """Clear the entire vector store."""
        try:
            # Delete and recreate
            import shutil
            if self.persist_directory.exists():
                shutil.rmtree(self.persist_directory)
            
            self.persist_directory.mkdir(parents=True, exist_ok=True)
            self._load_or_create_vectorstore()
            
            logger.info("Vector store cleared")
            
        except Exception as e:
            logger.error(f"Error clearing index: {e}")
            raise
    
    def get_stats(self) -> dict:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with statistics
        """
        try:
            # ChromaDB collection stats
            collection = self.vectorstore._collection
            count = collection.count()
            
            return {
                "total_documents": count,
                "persist_directory": str(self.persist_directory)
            }
            
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}


# Global index instance
vector_index = VectorIndex()

