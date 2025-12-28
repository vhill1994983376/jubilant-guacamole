# mcp_modules/ageni-qdrant/gui.py
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from .config import Config
from .memory_manager import MemoryManager

class MemoryGUI:
    """GUI for the AgeniQdrant memory management system."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AgeniQdrant Memory Manager")
        self.root.geometry("800x600")
        
        # Configuration
        self.config = Config()
        self.memory_manager = None
        
        # Create GUI components
        self.create_widgets()
        self.update_status()
        
    def create_widgets(self):
        """Create the main GUI widgets."""
        # Main notebook for different sections
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configuration tab
        self.config_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.config_frame, text="Configuration")
        self.create_config_widgets()
        
        # Memory Management tab
        self.memory_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.memory_frame, text="Memory Management")
        self.create_memory_widgets()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
    
    def create_config_widgets(self):
        """Create configuration widgets."""
        # OpenRouter API Key
        ttk.Label(self.config_frame, text="OpenRouter API Key:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.api_key_entry = ttk.Entry(self.config_frame, width=50, show="*")
        self.api_key_entry.grid(row=0, column=1, padx=5, pady=5)
        self.api_key_entry.insert(0, self.config.get("openrouter.api_key", ""))
        
        # Qdrant Host
        ttk.Label(self.config_frame, text="Qdrant Host:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.qdrant_host_entry = ttk.Entry(self.config_frame, width=30)
        self.qdrant_host_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.qdrant_host_entry.insert(0, self.config.get("qdrant.host", "localhost"))
        
        # Qdrant Port
        ttk.Label(self.config_frame, text="Qdrant Port:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.qdrant_port_entry = ttk.Entry(self.config_frame, width=10)
        self.qdrant_port_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.qdrant_port_entry.insert(0, str(self.config.get("qdrant.port", 6333)))
        
        # Qdrant API Key
        ttk.Label(self.config_frame, text="Qdrant API Key (optional):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.qdrant_api_key_entry = ttk.Entry(self.config_frame, width=50, show="*")
        self.qdrant_api_key_entry.grid(row=3, column=1, padx=5, pady=5)
        qdrant_api_key = self.config.get("qdrant.api_key")
        if qdrant_api_key:
            self.qdrant_api_key_entry.insert(0, qdrant_api_key)
        
        # Collection Type
        ttk.Label(self.config_frame, text="Collection Type:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.collection_type_var = tk.StringVar(value=self.config.get("memory.collection_type", "character"))
        ttk.Radiobutton(self.config_frame, text="Character (one per character card)", variable=self.collection_type_var, value="character").grid(row=4, column=1, sticky=tk.W, padx=5)
        ttk.Radiobutton(self.config_frame, text="Chat (one per character chat)", variable=self.collection_type_var, value="chat").grid(row=5, column=1, sticky=tk.W, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(self.config_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        self.save_button = ttk.Button(button_frame, text="Save Configuration", command=self.save_config)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        self.test_button = ttk.Button(button_frame, text="Test Connection", command=self.test_connection)
        self.test_button.pack(side=tk.LEFT, padx=5)
        
        self.status_frame = ttk.LabelFrame(self.config_frame, text="Status")
        self.status_frame.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)
        self.status_frame.columnconfigure(0, weight=1)
        
        self.config_status = ttk.Label(self.status_frame, text="Configuration incomplete")
        self.config_status.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    
    def create_memory_widgets(self):
        """Create memory management widgets."""
        # Context input
        ttk.Label(self.memory_frame, text="Context (Character Name or Chat Name):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.context_entry = ttk.Entry(self.memory_frame, width=50)
        self.context_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Message type
        ttk.Label(self.memory_frame, text="Message Type:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.message_type_var = tk.StringVar(value="user")
        ttk.Radiobutton(self.memory_frame, text="User", variable=self.message_type_var, value="user").grid(row=1, column=1, sticky=tk.W, padx=5)
        ttk.Radiobutton(self.memory_frame, text="Character", variable=self.message_type_var, value="character").grid(row=1, column=1, sticky=tk.E, padx=5)
        
        # Message input
        ttk.Label(self.memory_frame, text="Message:").grid(row=2, column=0, sticky=tk.NW, padx=5, pady=5)
        self.message_text = scrolledtext.ScrolledText(self.memory_frame, width=60, height=10)
        self.message_text.grid(row=2, column=1, padx=5, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(self.memory_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.add_memory_button = ttk.Button(button_frame, text="Add Memory", command=self.add_memory)
        self.add_memory_button.pack(side=tk.LEFT, padx=5)
        
        self.retrieve_button = ttk.Button(button_frame, text="Retrieve Memories", command=self.retrieve_memories)
        self.retrieve_button.pack(side=tk.LEFT, padx=5)
        
        self.summary_button = ttk.Button(button_frame, text="Get Context Summary", command=self.get_context_summary)
        self.summary_button.pack(side=tk.LEFT, padx=5)
        
        # Results area
        ttk.Label(self.memory_frame, text="Results:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.results_text = scrolledtext.ScrolledText(self.memory_frame, width=60, height=15)
        self.results_text.grid(row=5, column=0, columnspan=2, padx=5, pady=5)
    
    def update_status(self):
        """Update the status display."""
        if self.config.is_complete():
            self.config_status.config(text="Configuration complete", foreground="green")
            self.memory_manager = MemoryManager(self.config)
        else:
            self.config_status.config(text="Configuration incomplete", foreground="red")
            self.memory_manager = None
    
    def save_config(self):
        """Save configuration to file."""
        # Get values
        api_key = self.api_key_entry.get().strip()
        qdrant_host = self.qdrant_host_entry.get().strip()
        qdrant_port = self.qdrant_port_entry.get().strip()
        qdrant_api_key = self.qdrant_api_key_entry.get().strip()
        collection_type = self.collection_type_var.get()
        
        # Validate
        if not api_key:
            messagebox.showerror("Error", "Please enter an OpenRouter API key.")
            return
        
        if not qdrant_host:
            messagebox.showerror("Error", "Please enter a Qdrant host.")
            return
        
        try:
            port = int(qdrant_port)
            if not (1 <= port <= 65535):
                raise ValueError("Port must be between 1 and 65535")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid port: {e}")
            return
        
        # Save configuration
        self.config.set("openrouter.api_key", api_key)
        self.config.set("qdrant.host", qdrant_host)
        self.config.set("qdrant.port", port)
        self.config.set("qdrant.api_key", qdrant_api_key if qdrant_api_key else None)
        self.config.set("memory.collection_type", collection_type)
        
        # Update status
        self.update_status()
        messagebox.showinfo("Success", "Configuration saved successfully!")
    
    def test_connection(self):
        """Test connection to OpenRouter and Qdrant."""
        if not self.config.is_complete():
            messagebox.showerror("Error", "Please complete the configuration first.")
            return
        
        def test():
            try:
                # Test OpenRouter
                manager = MemoryManager(self.config)
                embedding = manager.openrouter_client.get_embedding("test")
                
                if not embedding:
                    self.status_var.set("Error: Failed to connect to OpenRouter")
                    return
                
                # Test Qdrant
                collections = manager.qdrant_client.list_collections()
                
                self.status_var.set(f"Success: Connected to OpenRouter and Qdrant. Found {len(collections)} collections.")
                
            except Exception as e:
                self.status_var.set(f"Error: {str(e)}")
        
        # Run in background thread
        thread = threading.Thread(target=test)
        thread.daemon = True
        thread.start()
        self.status_var.set("Testing connections...")
    
    def add_memory(self):
        """Add a memory to the system."""
        if not self.memory_manager:
            messagebox.showerror("Error", "Configuration not complete.")
            return
        
        context = self.context_entry.get().strip()
        message_type = self.message_type_var.get()
        message = self.message_text.get("1.0", tk.END).strip()
        
        if not context:
            messagebox.showerror("Error", "Please enter a context.")
            return
        
        if not message:
            messagebox.showerror("Error", "Please enter a message.")
            return
        
        def add():
            try:
                success = self.memory_manager.add_memory(message, context, message_type)
                if success:
                    self.status_var.set("Memory added successfully!")
                else:
                    self.status_var.set("Failed to add memory.")
            except Exception as e:
                self.status_var.set(f"Error adding memory: {str(e)}")
        
        # Run in background thread
        thread = threading.Thread(target=add)
        thread.daemon = True
        thread.start()
        self.status_var.set("Adding memory...")
    
    def retrieve_memories(self):
        """Retrieve memories for the given context."""
        if not self.memory_manager:
            messagebox.showerror("Error", "Configuration not complete.")
            return
        
        context = self.context_entry.get().strip()
        query = self.message_text.get("1.0", tk.END).strip()
        
        if not context:
            messagebox.showerror("Error", "Please enter a context.")
            return
        
        if not query:
            messagebox.showerror("Error", "Please enter a query.")
            return
        
        def retrieve():
            try:
                memories = self.memory_manager.retrieve_memories(query, context)
                self.results_text.delete("1.0", tk.END)
                
                if not memories:
                    self.results_text.insert(tk.END, "No memories found.")
                else:
                    for i, memory in enumerate(memories):
                        self.results_text.insert(tk.END, f"--- Memory {i+1} ---\n")
                        self.results_text.insert(tk.END, f"Text: {memory['text']}\n")
                        self.results_text.insert(tk.END, f"Type: {memory['type']}\n")
                        self.results_text.insert(tk.END, f"Timestamp: {memory['timestamp']}\n")
                        self.results_text.insert(tk.END, f"Keywords: {', '.join(memory['keywords'])}\n")
                        self.results_text.insert(tk.END, "\n")
                
                self.status_var.set(f"Retrieved {len(memories)} memories.")
            except Exception as e:
                self.status_var.set(f"Error retrieving memories: {str(e)}")
        
        # Run in background thread
        thread = threading.Thread(target=retrieve)
        thread.daemon = True
        thread.start()
        self.status_var.set("Retrieving memories...")
    
    def get_context_summary(self):
        """Get a summary of the context."""
        if not self.memory_manager:
            messagebox.showerror("Error", "Configuration not complete.")
            return
        
        context = self.context_entry.get().strip()
        
        if not context:
            messagebox.showerror("Error", "Please enter a context.")
            return
        
        def get_summary():
            try:
                summary = self.memory_manager.get_context_summary(context)
                self.results_text.delete("1.0", tk.END)
                self.results_text.insert(tk.END, summary)
                self.status_var.set("Context summary retrieved.")
            except Exception as e:
                self.status_var.set(f"Error getting context summary: {str(e)}")
        
        # Run in background thread
        thread = threading.Thread(target=get_summary)
        thread.daemon = True
        thread.start()
        self.status_var.set("Getting context summary...")

def main():
    """Main function to run the GUI."""
    root = tk.Tk()
    gui = MemoryGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()