# mcp_modules/ageni-qdrant/config.py
import os
import json
from typing import Dict, Any, Optional

class Config:
    """Configuration manager for the AgeniQdrant module."""
    
    def __init__(self, config_path: str = "mcp_modules/ageni-qdrant/config.json"):
        self.config_path = config_path
        self._config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default config."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
        
        # Default configuration
        return {
            "qdrant": {
                "host": "localhost",
                "port": 6333,
                "api_key": None
            },
            "openrouter": {
                "api_key": None,
                "model": "openai/gpt-4o"
            },
            "memory": {
                "collection_type": "character",  # "character" or "chat"
                "embedding_model": "openai/text-embedding-ada-002",
                "vector_size": 1536,
                "similarity_threshold": 0.75,
                "max_results": 10
            },
            "general": {
                "enabled": True,
                "debug": False
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self._save_config()
    
    def _save_config(self) -> None:
        """Save configuration to file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self._config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def is_complete(self) -> bool:
        """Check if all required configuration is set."""
        return (
            self.get("openrouter.api_key") is not None and
            self.get("qdrant.host") is not None and
            self.get("qdrant.port") is not None
        )