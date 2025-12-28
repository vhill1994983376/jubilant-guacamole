# AgeniQdrant MCP Module

A memory management system for Risu AI that uses an external Qdrant server for semantic storage and retrieval of agent memories.

## Features

- **External Qdrant Integration**: Connect to any Qdrant server for vector storage
- **OpenRouter API Integration**: Use OpenRouter for embeddings and text generation
- **Flexible Memory Organization**: Choose between character-based or chat-based memory collections
- **Keyword-based Memory Categorization**: Automatically categorize memories based on content
- **GUI Configuration**: Easy-to-use graphical interface for setup and management
- **Context-aware Memory Retrieval**: Retrieve relevant memories based on context and query

## Installation

1. Install the required dependencies:
   ```bash
   pip install qdrant-client openai requests