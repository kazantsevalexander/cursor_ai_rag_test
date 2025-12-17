"""
Integration test for FAISS vector store.
Tests the complete RAG pipeline.
"""

import asyncio
from pathlib import Path
from rag.index import get_vector_index
from rag.query import query_knowledge_base


async def test_rag_pipeline():
    """Test the complete RAG pipeline."""
    print("=" * 60)
    print("Testing FAISS Vector Store Integration")
    print("=" * 60)
    
    # 1. Get vector index
    print("\n1. Initializing vector index...")
    index = get_vector_index()
    print(f"   ✓ Index initialized with {index.collection.count()} documents")
    
    # 2. Check if documents are indexed
    count = index.collection.count()
    if count == 0:
        print("\n2. No documents found, indexing...")
        from config import DOCUMENTS_DIR
        count = index.index_documents_directory(DOCUMENTS_DIR, force_reindex=True)
        print(f"   ✓ Indexed {count} documents")
    else:
        print(f"\n2. Documents already indexed: {count}")
    
    # 3. Test similarity search
    print("\n3. Testing similarity search...")
    test_queries = [
        "Что такое Python?",
        "Как управлять проектом?",
        "Расскажи о научных исследованиях"
    ]
    
    for query in test_queries:
        print(f"\n   Query: '{query}'")
        docs = index.similarity_search(query, k=2)
        
        if docs:
            print(f"   ✓ Found {len(docs)} relevant documents:")
            for i, doc in enumerate(docs, 1):
                source = doc.metadata.get('source', 'Unknown')
                preview = doc.page_content[:100].replace('\n', ' ')
                print(f"      {i}. [{source}] {preview}...")
        else:
            print("   ✗ No documents found")
    
    # 4. Test RAG query
    print("\n4. Testing RAG query with context...")
    test_query = "Что такое Python и для чего он используется?"
    print(f"   Query: '{test_query}'")
    
    try:
        response = await query_knowledge_base(test_query)
        print(f"   ✓ Response generated:")
        print(f"      {response[:200]}...")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # 5. Get statistics
    print("\n5. Vector store statistics:")
    stats = index.get_stats()
    print(f"   Total documents: {stats['total_documents']}")
    print(f"   Storage path: {stats['persist_directory']}")
    
    # Check file sizes
    persist_dir = Path(stats['persist_directory'])
    if persist_dir.exists():
        index_file = persist_dir / "index.faiss"
        metadata_file = persist_dir / "metadata.pkl"
        
        if index_file.exists():
            size_mb = index_file.stat().st_size / 1024 / 1024
            print(f"   Index size: {size_mb:.2f} MB")
        
        if metadata_file.exists():
            size_mb = metadata_file.stat().st_size / 1024 / 1024
            print(f"   Metadata size: {size_mb:.2f} MB")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_rag_pipeline())
