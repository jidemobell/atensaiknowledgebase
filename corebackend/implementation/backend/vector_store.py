"""
Vector Store for IBM AIOps Knowledge System
Handles semantic search using Qdrant vector database
"""

from typing import List, Dict, Any, Optional
import uuid
import json
from datetime import datetime

# Try to import qdrant
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue, MatchAny
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

class VectorStore:
    def __init__(self, host: str = "localhost", port: int = 6333):
        """Initialize vector store with Qdrant client"""
        if not QDRANT_AVAILABLE:
            print("Warning: Qdrant not available. Vector search will be disabled.")
            self.client = None
            return
            
        try:
            self.client = QdrantClient(host=host, port=port)
            self.collection_name = "asm_knowledge"
            self._ensure_collection()
        except Exception as e:
            print(f"Warning: Could not connect to Qdrant: {e}")
            self.client = None
    
    def _ensure_collection(self):
        """Create collection if it doesn't exist"""
        if not self.client:
            return
            
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                # Create collection with 384-dimensional vectors (sentence-transformers default)
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
                print(f"Created Qdrant collection: {self.collection_name}")
            else:
                print(f"Using existing Qdrant collection: {self.collection_name}")
                
        except Exception as e:
            print(f"Error creating collection: {e}")
            self.client = None
    
    def add_documents(self, processed_docs: List[Dict[str, Any]]) -> bool:
        """Add processed documents to vector store"""
        if not self.client:
            print("Vector store not available - documents will not be indexed")
            return False
        
        points = []
        
        try:
            for doc in processed_docs:
                for chunk in doc['chunks']:
                    # Skip chunks without embeddings
                    if not chunk.get('embedding'):
                        continue
                    
                    point = PointStruct(
                        id=str(uuid.uuid4()),
                        vector=chunk['embedding'],
                        payload={
                            'text': chunk['text'],
                            'chunk_id': chunk['chunk_id'],
                            'chunk_type': chunk['chunk_type'],
                            'position': chunk['position'],
                            'token_count': chunk['token_count'],
                            'case_id': doc.get('case_id', doc.get('doc_id', 'unknown')),
                            'services': doc['services'],
                            'source_type': chunk['source_type'],
                            'confidence': doc['metadata'].get('confidence', 0.5),
                            'version': doc['metadata'].get('version'),
                            'environment': doc['metadata'].get('environment'),
                            'priority': doc['metadata'].get('priority'),
                            'processed_at': doc.get('processed_at', datetime.now().isoformat())
                        }
                    )
                    points.append(point)
            
            if points:
                # Batch insert
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
                print(f"Added {len(points)} chunks to vector store")
                return True
            else:
                print("No valid chunks to add (missing embeddings)")
                return False
                
        except Exception as e:
            print(f"Error adding documents to vector store: {e}")
            return False
    
    def semantic_search(self, 
                       query_embedding: List[float], 
                       services: List[str] = None, 
                       chunk_types: List[str] = None,
                       limit: int = 5) -> List[Dict[str, Any]]:
        """Semantic search with service and type filtering"""
        
        if not self.client or not query_embedding:
            return []
        
        try:
            # Build filters
            must_conditions = []
            
            if services:
                must_conditions.append(
                    FieldCondition(
                        key="services",
                        match=MatchAny(any=services)
                    )
                )
            
            if chunk_types:
                must_conditions.append(
                    FieldCondition(
                        key="chunk_type",
                        match=MatchAny(any=chunk_types)
                    )
                )
            
            # Create filter if we have conditions
            search_filter = Filter(must=must_conditions) if must_conditions else None
            
            # Search
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=search_filter,
                limit=limit,
                with_payload=True
            )
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'text': result.payload['text'],
                    'score': float(result.score),
                    'chunk_id': result.payload['chunk_id'],
                    'chunk_type': result.payload['chunk_type'],
                    'case_id': result.payload['case_id'],
                    'services': result.payload['services'],
                    'source_type': result.payload['source_type'],
                    'confidence': result.payload.get('confidence', 0.5),
                    'version': result.payload.get('version'),
                    'environment': result.payload.get('environment'),
                    'priority': result.payload.get('priority')
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error during semantic search: {e}")
            return []
    
    def search_by_case_id(self, case_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a specific case"""
        if not self.client:
            return []
        
        try:
            # Search with case_id filter
            results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="case_id",
                            match=MatchValue(value=case_id)
                        )
                    ]
                ),
                with_payload=True,
                limit=100  # Reasonable limit for one case
            )
            
            formatted_results = []
            for result in results[0]:  # results is (points, next_page_offset)
                formatted_results.append({
                    'text': result.payload['text'],
                    'chunk_id': result.payload['chunk_id'],
                    'chunk_type': result.payload['chunk_type'],
                    'position': result.payload['position'],
                    'services': result.payload['services'],
                    'source_type': result.payload['source_type']
                })
            
            # Sort by position for proper ordering
            return sorted(formatted_results, key=lambda x: x['position'])
            
        except Exception as e:
            print(f"Error searching by case ID: {e}")
            return []
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection"""
        if not self.client:
            return {"status": "unavailable", "reason": "Qdrant not connected"}
        
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "status": "connected",
                "collection_name": self.collection_name,
                "points_count": info.points_count,
                "vector_size": info.config.params.vectors.size,
                "distance": info.config.params.vectors.distance.name
            }
        except Exception as e:
            return {"status": "error", "reason": str(e)}
    
    def delete_case_documents(self, case_id: str) -> bool:
        """Delete all documents for a specific case"""
        if not self.client:
            return False
        
        try:
            # Delete points with specific case_id
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="case_id",
                            match=MatchValue(value=case_id)
                        )
                    ]
                )
            )
            print(f"Deleted documents for case: {case_id}")
            return True
            
        except Exception as e:
            print(f"Error deleting case documents: {e}")
            return False

class MockVectorStore:
    """Mock vector store for when Qdrant is not available"""
    
    def __init__(self, *args, **kwargs):
        self.documents = []
        print("Using mock vector store (Qdrant not available)")
    
    def add_documents(self, processed_docs: List[Dict[str, Any]]) -> bool:
        """Store documents in memory"""
        for doc in processed_docs:
            self.documents.append(doc)
        return True
    
    def semantic_search(self, query_embedding=None, services=None, chunk_types=None, limit=5) -> List[Dict[str, Any]]:
        """Mock semantic search - returns empty list"""
        # Use parameters to avoid lint warnings
        _ = query_embedding, services, chunk_types, limit
        return []
    
    def search_by_case_id(self, case_id: str) -> List[Dict[str, Any]]:
        """Mock case search"""
        # Use parameter to avoid lint warning
        _ = case_id
        return []
    
    def get_collection_info(self) -> Dict[str, Any]:
        return {
            "status": "mock", 
            "reason": "Using in-memory mock store",
            "documents_count": len(self.documents)
        }
    
    def delete_case_documents(self, case_id: str) -> bool:
        _ = case_id  # Use parameter to avoid lint warning
        return True

# Factory function to create appropriate vector store
def create_vector_store(host: str = "localhost", port: int = 6333):
    """Create vector store, falling back to mock if Qdrant unavailable"""
    if QDRANT_AVAILABLE:
        return VectorStore(host, port)
    else:
        return MockVectorStore(host, port)
