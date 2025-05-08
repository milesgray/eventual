"""
# Hypergraph Persistence

The `hypergraph_persistence` module provides functionality to save and load
the `Hypergraph` to and from a file.

This allows the hypergraph to persist across sessions.

## Usage

```python
from eventual.core.hypergraph import Hypergraph
from eventual.persistence.hypergraph_persistence import HypergraphPersistence

# Assuming you have a hypergraph instance
hypergraph = Hypergraph()
# ... populate hypergraph ...

# Initialize the persistence manager
persistence_manager = HypergraphPersistence()

# Define the file path
file_path = "hypergraph_data.json"

# Save the hypergraph
persistence_manager.save_hypergraph(hypergraph, file_path)
print(f"Hypergraph saved to {file_path}")

# Load the hypergraph
loaded_hypergraph = persistence_manager.load_hypergraph(file_path)
print(f"Hypergraph loaded from {file_path}")
print(f"Loaded Hypergraph state: {loaded_hypergraph}")
```
"""
import json
import os
from typing import Optional
from eventual.core.hypergraph import Hypergraph

class HypergraphPersistence:
    """
    Manages saving and loading of the Hypergraph to and from a file.
    """

    def __init__(self):
        """
        Initialize the HypergraphPersistence manager.
        """
        pass # No specific initialization needed for this basic version

    def save_hypergraph(self, hypergraph: Hypergraph, file_path: str):
        """
        Saves the Hypergraph object to a JSON file.

        Args:
            hypergraph (Hypergraph): The Hypergraph object to save.
            file_path (str): The path to the JSON file.
        """
        if not isinstance(hypergraph, Hypergraph):
            raise TypeError("hypergraph must be an instance of Hypergraph")

        hypergraph_dict = hypergraph.to_dict()

        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(hypergraph_dict, f, indent=4)
            print(f"Hypergraph successfully saved to {file_path}")
        except IOError as e:
            print(f"Error saving hypergraph to {file_path}: {e}")
            # Depending on desired behavior, you might re-raise the exception or handle it.
            raise

    def load_hypergraph(self, file_path: str) -> Optional[Hypergraph]:
        """
        Loads a Hypergraph object from a JSON file.

        Args:
            file_path (str): The path to the JSON file.

        Returns:
            Optional[Hypergraph]: The loaded Hypergraph object, or None if the file does not exist or loading fails.
        """
        if not os.path.exists(file_path):
            print(f"Warning: Hypergraph save file not found at {file_path}. Returning None.")
            return None

        try:
            with open(file_path, 'r') as f:
                hypergraph_dict = json.load(f)

            # Create a new Hypergraph instance from the loaded dictionary
            hypergraph = Hypergraph.from_dict(hypergraph_dict)
            print(f"Hypergraph successfully loaded from {file_path}")
            return hypergraph
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {file_path}: {e}")
            return None
        except Exception as e:
            print(f"Error loading hypergraph from {file_path}: {e}")
            return None

    def delete_hypergraph_file(self, file_path: str):
        """
        Deletes the Hypergraph save file.

        Args:
            file_path (str): The path to the JSON file.
        """
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Hypergraph save file deleted: {file_path}")
            except OSError as e:
                print(f"Error deleting hypergraph save file {file_path}: {e}")
                # Depending on desired behavior, you might re-raise the exception or handle it.
                raise
        else:
            print(f"Warning: Hypergraph save file not found for deletion: {file_path}")

