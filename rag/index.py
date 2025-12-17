"""
Vector Index for RAG.
Creates and manages embeddings using FAISS and OpenAI API.
FAISS provides fast, stable vector similarity search with persistence.
"""

from typing import List, Optional
from pathlib import Path
from openai import OpenAI

from config import DATA_DIR, OPENAI_API_KEY, DOCUMENTS_DIR
from utils.logging import logger
from rag.loader import document_loader
from rag.faiss_store import FAISSVectorStore


class OpenAIEmbeddingFunction:
    """Custom embedding function using OpenAI API directly."""
    
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self._client = OpenAI(api_key=api_key)
        self._model = model
    
    def __call__(self, input: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        if not input:
            return []
        
        logger.info(f"Generating embeddings for {len(input)} texts...")
        
        # Replace newlines with spaces
        texts = [text.replace("\n", " ") for text in input]
        
        try:
            response = self._client.embeddings.create(
                input=texts,
                model=self._model
            )
            
            # Extract embeddings in order
            embeddings = [item.embedding for item in response.data]
            logger.info(f"Successfully generated {len(embeddings)} embeddings")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise


class VectorIndex:
    """Manages vector embeddings and similarity search."""
    
    def __init__(self, persist_directory: Optional[Path] = None):
        """Initialize vector index."""
        if persist_directory is None:
            persist_directory = DATA_DIR / "faiss_index"
        else:
            persist_directory = Path(persist_directory)
        
        logger.info(f"Initializing FAISS vector store at {persist_directory}...")
        
        # Use FAISS vector store (stable and fast)
        try:
            self.collection = FAISSVectorStore(
                persist_directory=persist_directory,
                dimension=1536  # text-embedding-3-small dimension
            )
            logger.info("FAISS vector store initialized")
        except Exception as e:
            logger.error(f"Failed to create FAISS vector store: {e}")
            raise

        # Initialize embedding function
        self.embedding_fn = OpenAIEmbeddingFunction(
            api_key=OPENAI_API_KEY,
            model="text-embedding-3-small"
        )
        logger.info("Embedding function initialized")
        
        logger.info(f"Vector store ready. Documents: {self.collection.count()}")
    
    def add_documents(self, documents: List, batch_size: int = 5) -> None:
        """Add documents to the vector store in batches."""
        try:
            if not documents:
                logger.warning("No documents to add")
                return
            
            logger.info(f"Adding {len(documents)} documents to vector store in batches of {batch_size}...")
            
            base_count = self.collection.count()
            logger.info(f"Current document count in collection: {base_count}")
            
            # Process in batches
            total_added = 0
            for batch_start in range(0, len(documents), batch_size):
                batch_end = min(batch_start + batch_size, len(documents))
                batch_docs = documents[batch_start:batch_end]
                
                batch_num = batch_start//batch_size + 1
                total_batches = (len(documents)-1)//batch_size + 1
                logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch_docs)} documents)...")
                
                # Prepare batch data
                ids = []
                texts = []
                metadatas = []
                
                for i, doc in enumerate(batch_docs):
                    doc_id = f"doc_{base_count + total_added + i}"
                    ids.append(doc_id)
                    texts.append(doc.page_content)
                    # Ensure metadata values are strings
                    meta = {}
                    for k, v in doc.metadata.items():
                        meta[k] = str(v) if v is not None else ""
                    metadatas.append(meta)
                
                # Generate embeddings for batch
                logger.info(f"Generating embeddings for batch {batch_num}...")
                embeddings = self.embedding_fn(texts)
                logger.info(f"Embeddings generated for batch {batch_num}")
                
                # Add batch to collection
                logger.info(f"Adding batch {batch_num} to vector store...")
                
                try:
                    self.collection.add(
                        ids=ids,
                        documents=texts,
                        metadatas=metadatas,
                        embeddings=embeddings
                    )
                    logger.info(f"Batch {batch_num} added successfully")
                    
                except Exception as add_error:
                    logger.error(f"Error adding batch {batch_num}: {add_error}", exc_info=True)
                    raise
                
                total_added += len(batch_docs)
                logger.info(f"Progress: {total_added}/{len(documents)} documents added")
            
            final_count = self.collection.count()
            logger.info(f"Successfully added all {total_added} documents. Total in store: {final_count}")
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}", exc_info=True)
            raise

    
    def similarity_search(self, query: str, k: int = 3) -> List:
        """Search for similar documents."""
        try:
            # Generate query embedding
            query_embedding = self.embedding_fn([query])
            
            # Search
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=k
            )
            
            from langchain_core.documents import Document
            docs = []
            if results['documents'] and results['documents'][0]:
                for i, text in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    docs.append(Document(page_content=text, metadata=metadata))
            
            logger.debug(f"Found {len(docs)} similar documents")
            return docs
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            raise
    
    def similarity_search_with_score(self, query: str, k: int = 3) -> List[tuple]:
        """Search for similar documents with relevance scores."""
        try:
            # Generate query embedding
            query_embedding = self.embedding_fn([query])
            
            # Search
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=k
            )
            
            from langchain_core.documents import Document
            docs_with_scores = []
            
            if results['documents'] and results['documents'][0]:
                for i, text in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    distance = results['distances'][0][i] if results['distances'] else 0
                    doc = Document(page_content=text, metadata=metadata)
                    docs_with_scores.append((doc, distance))
            
            logger.debug(f"Found {len(docs_with_scores)} similar documents with scores")
            return docs_with_scores
            
        except Exception as e:
            logger.error(f"Error in similarity search with scores: {e}")
            raise
    
    def index_documents_directory(
        self,
        directory: Path = DOCUMENTS_DIR,
        force_reindex: bool = False
    ) -> int:
        """Index all documents from a directory."""
        try:
            current_count = self.collection.count()
            
            # Skip if already indexed and not forcing reindex
            if current_count > 0 and not force_reindex:
                logger.info(f"Index already contains {current_count} documents, skipping indexing")
                return current_count
            
            if force_reindex:
                logger.info("Clearing existing index for reindexing")
                self.clear_index()
            
            logger.info(f"Loading documents from {directory}...")
            documents = document_loader.load_directory(directory)
            
            if not documents:
                logger.warning("No documents found to index")
                return 0
            
            logger.info(f"Adding {len(documents)} document chunks to index...")
            self.add_documents(documents)
            
            final_count = self.collection.count()
            logger.info(f"Indexing complete. Total documents in index: {final_count}")
            return final_count
            
        except Exception as e:
            logger.error(f"Error indexing documents: {e}", exc_info=True)
            raise
    
    def clear_index(self):
        """Clear the entire vector store."""
        try:
            self.collection.clear()
            logger.info("Vector store cleared")
        except Exception as e:
            logger.error(f"Error clearing index: {e}")
            raise
    
    def get_stats(self) -> dict:
        """Get statistics about the vector store."""
        try:
            return {
                "total_documents": self.collection.count(),
                "persist_directory": str(self.collection.persist_directory)
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}


# Global index instance (lazy initialization)
_vector_index = None


def get_vector_index() -> VectorIndex:
    """Get or create the global vector index instance."""
    global _vector_index
    if _vector_index is None:
        logger.info("Initializing vector index...")
        _vector_index = VectorIndex()
    return _vector_index


# For backward compatibility
class _LazyVectorIndex:
    """Lazy proxy for VectorIndex."""
    
    def __getattr__(self, name):
        return getattr(get_vector_index(), name)


vector_index = _LazyVectorIndex()
