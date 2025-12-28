# mcp_modules/ageni-qdrant/memory_manager.py
import time
import uuid
from typing import List, Dict, Any, Optional, Tuple
from .client import OpenRouterClient, QdrantClient
from .config import Config

class MemoryManager:
    """Main memory management system for Risu AI."""
    
    def __init__(self, config: Config):
        self.config = config
        self.openrouter_client = OpenRouterClient(config)
        self.qdrant_client = QdrantClient(config)
        self.keywords = self._load_keywords()
        
    def _load_keywords(self) -> Dict[str, List[str]]:
        """Load keywords for memory categorization."""
        # Default keywords
        return {
            "user": ["user", "i", "me", "my", "mine"],
            "character": ["you", "your", "yours", "character"],
            "emotional": ["feel", "emotion", "sad", "happy", "angry", "excited"],
            "important": ["important", "crucial", "critical", "key", "essential"],
            "context": ["context", "background", "setting", "situation", "scenario"],
            "personal": ["name", "age", "location", "job", "hobby", "interest"]
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        text_lower = text.lower()
        found_keywords = []
        
        for category, words in self.keywords.items():
            for word in words:
                if word in text_lower:
                    found_keywords.append(f"{category}_{word}")
        
        return found_keywords
    
    def _create_memory_payload(self, text: str, context: str, message_type: str) -> Dict[str, Any]:
        """Create a memory payload from text."""
        timestamp = time.time()
        keywords = self._extract_keywords(text)
        
        payload = {
            "text": text,
            "context": context,
            "type": message_type,  # "user" or "character"
            "timestamp": timestamp,
            "keywords": keywords,
            "source": "risu_ai"
        }
        
        return payload
    
    def add_memory(self, text: str, context: str, message_type: str) -> bool:
        """Add a new memory to the system."""
        if not self.config.is_complete():
            print("Configuration not complete. Please set up your API keys.")
            return False
        
        # Get collection name
        collection_name = self.qdrant_client._collection_name(context)
        
        # Create collection if it doesn't exist
        if collection_name not in self.qdrant_client.list_collections():
            created = self.qdrant_client.create_collection(collection_name)
            if not created:
                print(f"Failed to create collection: {collection_name}")
                return False
        
        # Create memory payload
        payload = self._create_memory_payload(text, context, message_type)
        
        # Get embedding
        embedding = self.openrouter_client.get_embedding(text)
        if not embedding:
            print("Failed to get embedding for text")
            return False
        
        # Create vector point
        vector_point = {
            "id": str(uuid.uuid4()),
            "vector": embedding,
            "payload": payload
        }
        
        # Upsert to Qdrant
        success = self.qdrant_client.upsert_vectors(collection_name, [vector_point])
        if success:
            print(f"Successfully added memory to {collection_name}")
        else:
            print(f"Failed to add memory to {collection_name}")
        
        return success
    
    def retrieve_memories(self, query: str, context: str, limit: Optional[int] = None) -> List[Dict]:
        """Retrieve relevant memories for a query."""
        if not self.config.is_complete():
            print("Configuration not complete. Please set up your API keys.")
            return []
        
        if limit is None:
            limit = self.config.get("memory.max_results", 10)
        
        # Get collection name
        collection_name = self.qdrant_client._collection_name(context)
        
        # Get embedding for query
        embedding = self.openrouter_client.get_embedding(query)
        if not embedding:
            print("Failed to get embedding for query")
            return []
        
        # Search in Qdrant
        results = self.qdrant_client.search_vectors(collection_name, embedding, limit)
        
        # Filter results by similarity threshold
        threshold = self.config.get("memory.similarity_threshold", 0.75)
        filtered_results = []
        
        for result in results:
            if result.get("score", 0) >= threshold:
                filtered_results.append(result["payload"])
        
        return filtered_results
    
    def get_context_summary(self, context: str) -> str:
        """Get a summary of the context based on stored memories."""
        if not self.config.is_complete():
            return "Configuration not complete."
        
        # Get all memories for the context
        collection_name = self.qdrant_client._collection_name(context)
        all_collections = self.qdrant_client.list_collections()
        
        if collection_name not in all_collections:
            return "No memories found for this context."
        
        # Get embeddings for a generic query to retrieve memories
        embedding = self.openrouter_client.get_embedding("Get me all the important details about this context.")
        memories = self.qdrant_client.search_vectors(collection_name, embedding, 20)
        
        # Extract text from memories
        memory_texts = [mem["payload"]["text"] for mem in memories]
        
        # Generate summary
        prompt = f"Summarize the following memories:\n\n" + "\n".join(memory_texts[:10])
        summary = self.openrouter_client.generate_text(prompt, 200)
        
        return summary

def create_module_instance(config: Config) -> MemoryManager:
    """Create and return a MemoryManager instance."""
    return MemoryManager(config)