# mcp_modules/ageni-qdrant/client.py
import os
import openai
import requests
from typing import List, Dict, Any, Optional, Tuple
from .config import Config

class OpenRouterClient:
    """Client for OpenRouter API to handle embeddings and text generation."""
    
    def __init__(self, config: Config):
        self.config = config
        self.api_key = config.get("openrouter.api_key")
        self.model = config.get("openrouter.model", "openai/gpt-4o")
        self.embedding_model = config.get("memory.embedding_model", "openai/text-embedding-ada-002")
        self.base_url = "https://openrouter.ai/api/v1"
        
        # Set up OpenAI client
        openai.api_key = self.api_key
        openai.base_url = f"{self.base_url}/"
        openai.api_type = "openai"
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a text using OpenRouter API."""
        try:
            response = openai.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {e}")
            return []
    
    def generate_text(self, prompt: str, max_tokens: int = 100) -> str:
        """Generate text using OpenRouter API."""
        try:
            response = openai.completions.create(
                model=self.model,
                prompt=prompt,
                max_tokens=max_tokens
            )
            return response.choices[0].text
        except Exception as e:
            print(f"Error generating text: {e}")
            return ""

class QdrantClient:
    """Client for Qdrant vector database operations."""
    
    def __init__(self, config: Config):
        self.config = config
        self.host = config.get("qdrant.host", "localhost")
        self.port = config.get("qdrant.port", 6333)
        self.api_key = config.get("qdrant.api_key")
        self.base_url = f"http://{self.host}:{self.port}"
        
        # Set up session with API key if provided
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"api-key": self.api_key})
    
    def _collection_name(self, context: str) -> str:
        """Generate collection name based on context."""
        # Convert context to a valid collection name
        collection_type = self.config.get("memory.collection_type", "character")
        if collection_type == "character":
            return f"character_{context.lower().replace(' ', '_').replace('.', '_')}"
        else:  # chat
            return f"chat_{context.lower().replace(' ', '_').replace('.', '_')}"
    
    def create_collection(self, collection_name: str) -> bool:
        """Create a new collection in Qdrant."""
        try:
            url = f"{self.base_url}/collections/{collection_name}"
            payload = {
                "vectors": {
                    "size": self.config.get("memory.vector_size", 1536),
                    "distance": "Cosine"
                },
                "optimizers_config": {
                    "default_segment_number": 4,
                    "reordering_enabled": True
                }
            }
            
            response = self.session.put(url, json=payload)
            return response.status_code in [200, 201]
        except Exception as e:
            print(f"Error creating collection: {e}")
            return False
    
    def upsert_vectors(self, collection_name: str, vectors: List[Dict]) -> bool:
        """Upsert vectors to a collection."""
        try:
            url = f"{self.base_url}/collections/{collection_name}/points"
            payload = {"points": vectors}
            
            response = self.session.put(url, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"Error upserting vectors: {e}")
            return False
    
    def search_vectors(self, collection_name: str, vector: List[float], limit: int = 10) -> List[Dict]:
        """Search for similar vectors in a collection."""
        try:
            url = f"{self.base_url}/collections/{collection_name}/points/search"
            payload = {
                "vector": vector,
                "limit": limit,
                "with_payload": True
            }
            
            response = self.session.post(url, json=payload)
            if response.status_code == 200:
                return response.json()["result"]
            return []
        except Exception as e:
            print(f"Error searching vectors: {e}")
            return []
    
    def list_collections(self) -> List[str]:
        """List all collections in Qdrant."""
        try:
            url = f"{self.base_url}/collections"
            response = self.session.get(url)
            if response.status_code == 200:
                return [col["name"] for col in response.json()["result"]["collections"]]
            return []
        except Exception as e:
            print(f"Error listing collections: {e}")
            return []