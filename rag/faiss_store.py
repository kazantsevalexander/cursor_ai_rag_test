"""
FAISS Vector Store for RAG.
Stable, fast, and Windows-compatible vector database.
"""

import pickle
from pathlib import Path
from typing import List, Dict, Optional, Tuple

import faiss
import numpy as np
from langchain_core.documents import Document

from config import DATA_DIR
from utils.logging import logger


class FAISSVectorStore:
    """FAISS-based vector store with persistence."""
    
    def __init__(self, persist_directory: Optional[Path] = None, dimension: int = 1536):
        """
        Initialize FAISS vector store.
        
        Args:
            persist_directory: Directory to save/load the index
            dimension: Embedding dimension (1536 for text-embedding-3-small)
        """
        if persist_directory is None:
            persist_directory = DATA_DIR / "faiss_index"
        
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        self.dimension = dimension
        self.index_path = self.persist_directory / "index.faiss"
        self.metadata_path = self.persist_directory / "metadata.pkl"
        
        # Initialize or load index
        if self.index_path.exists() and self.metadata_path.exists():
            self._load()
        else:
            self._create_new_index()
    
    def _create_new_index(self):
        """Create a new FAISS index."""
        # Use IndexFlatL2 for exact search with L2 distance
        # For cosine similarity, we'll normalize vectors
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner Product (for normalized vectors = cosine)
        
        # Metadata storage
        self.documents: List[str] = []
        self.metadatas: List[Dict] = []
        self.ids: List[str] = []
        
        logger.info(f"Created new FAISS index with dimension {self.dimension}")
    
    def _load(self):
        """Load existing FAISS index and metadata."""
        try:
            # Load FAISS index
            self.index = faiss.read_index(str(self.index_path))
            
            # Load metadata
            with open(self.metadata_path, 'rb') as f:
                metadata = pickle.load(f)
                self.documents = metadata['documents']
                self.metadatas = metadata['metadatas']
                self.ids = metadata['ids']
            
            logger.info(f"Loaded FAISS index with {len(self.documents)} documents")
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}")
            logger.info("Creating new index instead")
            self._create_new_index()
    
    def _save(self):
        """Save FAISS index and metadata to disk."""
        try:
            # Save FAISS index
            faiss.write_index(self.index, str(self.index_path))
            
            # Save metadata
            metadata = {
                'documents': self.documents,
                'metadatas': self.metadatas,
                'ids': self.ids
            }
            
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(metadata, f)
            
            logger.debug(f"Saved FAISS index to {self.persist_directory}")
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
    
    def add(self, ids: List[str], documents: List[str], 
            embeddings: List[List[float]], metadatas: List[Dict]) -> None:
        """
        Add documents to the vector store.
        
        Args:
            ids: Document IDs
            documents: Document texts
            embeddings: Document embeddings
            metadatas: Document metadata
        """
        # Normalize embeddings for cosine similarity
        embeddings_array = np.array(embeddings, dtype=np.float32)
        
        # Normalize vectors (for cosine similarity with inner product)
        norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
        embeddings_array = embeddings_array / (norms + 1e-10)
        
        # Add to FAISS index
        self.index.add(embeddings_array)
        
        # Add metadata
        self.documents.extend(documents)
        self.metadatas.extend(metadatas)
        self.ids.extend(ids)
        
        # Auto-save
        self._save()
    
    def query(self, query_embeddings: List[List[float]], n_results: int = 3) -> Dict:
        """
        Query for similar documents.
        
        Args:
            query_embeddings: Query embedding vectors
            n_results: Number of results to return
        
        Returns:
            Dictionary with ids, documents, metadatas, and distances
        """
        if self.index.ntotal == 0:
            return {
                'ids': [[]],
                'documents': [[]],
                'metadatas': [[]],
                'distances': [[]]
            }
        
        # Normalize query embedding
        query_array = np.array(query_embeddings, dtype=np.float32)
        norms = np.linalg.norm(query_array, axis=1, keepdims=True)
        query_array = query_array / (norms + 1e-10)
        
        # Search
        n_results = min(n_results, self.index.ntotal)
        distances, indices = self.index.search(query_array, n_results)
        
        # Prepare results
        results = {
            'ids': [],
            'documents': [],
            'metadatas': [],
            'distances': []
        }
        
        for i in range(len(query_embeddings)):
            result_ids = []
            result_docs = []
            result_metas = []
            result_dists = []
            
            for j, idx in enumerate(indices[i]):
                if idx != -1 and idx < len(self.documents):
                    result_ids.append(self.ids[idx])
                    result_docs.append(self.documents[idx])
                    result_metas.append(self.metadatas[idx])
                    # Convert similarity to distance (1 - similarity)
                    result_dists.append(float(1 - distances[i][j]))
            
            results['ids'].append(result_ids)
            results['documents'].append(result_docs)
            results['metadatas'].append(result_metas)
            results['distances'].append(result_dists)
        
        return results
    
    def count(self) -> int:
        """Get number of documents in the store."""
        return self.index.ntotal
    
    def clear(self) -> None:
        """Clear all data from the store."""
        self._create_new_index()
        
        # Remove persisted files
        if self.index_path.exists():
            self.index_path.unlink()
        if self.metadata_path.exists():
            self.metadata_path.unlink()
        
        logger.info("FAISS index cleared")
    
    def delete_by_ids(self, ids: List[str]) -> None:
        """
        Delete documents by IDs.
        Note: FAISS doesn't support deletion, so we rebuild the index.
        """
        # Find indices to keep
        indices_to_keep = [i for i, doc_id in enumerate(self.ids) if doc_id not in ids]
        
        if len(indices_to_keep) == len(self.ids):
            logger.info("No documents to delete")
            return
        
        # Rebuild index with remaining documents
        logger.info(f"Rebuilding index after deleting {len(self.ids) - len(indices_to_keep)} documents")
        
        # Save remaining data
        remaining_docs = [self.documents[i] for i in indices_to_keep]
        remaining_metas = [self.metadatas[i] for i in indices_to_keep]
        remaining_ids = [self.ids[i] for i in indices_to_keep]
        
        # Get embeddings from index (if needed, we'd need to store them separately)
        # For now, we'll just clear and require re-adding
        self._create_new_index()
        
        self.documents = remaining_docs
        self.metadatas = remaining_metas
        self.ids = remaining_ids
        
        logger.warning("Note: Embeddings need to be regenerated after deletion")
        self._save()
