# tests/test_chat_scenario.py

import unittest
import os
import sys
from datetime import datetime, timedelta

# Add the parent directory to the sys.path to allow importing eventual
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from eventual.pipeline import EventualPipeline, load_config
from eventual.core.hypergraph import Hypergraph
from eventual.persistence.hypergraph_persistence import HypergraphPersistence

# Define a dummy config file path for testing
dummy_test_config_path = "dummy_test_config.yaml"

class TestChatScenario(unittest.TestCase):

    def setUp(self):
        """Set up a dummy config file and clean up any previous test artifacts."""
        self.cleanup_test_artifacts()
        self.create_dummy_config()
        self.hypergraph_save_path = "./test_chat_hypergraph.json"

    def tearDown(self):
        """Clean up test artifacts after each test."""
        self.cleanup_test_artifacts()

    def create_dummy_config(self):
        """Creates a dummy config file for testing purposes."""
        dummy_config_content = f"""
languages:
  - code: en
    name: English

steps: [13]

data_sources: {{}}

chat_settings:
  example_messages:
    - "Hello, how are you?"
    - "Tell me about the weather today."
    - "What is the capital of France?"
  recent_memory_window_minutes: 10
  hypergraph_save_path: "{self.hypergraph_save_path}"
"""
        try:
            with open(dummy_test_config_path, "w") as f:
                f.write(dummy_config_content)
        except Exception as e:
            self.fail(f"Error creating dummy test config file: {e}")

    def cleanup_test_artifacts(self):
        """Removes any files created during testing."""
        files_to_remove = [
            dummy_test_config_path,
            self.hypergraph_save_path if hasattr(self, 'hypergraph_save_path') else "./test_chat_hypergraph.json",
        ]
        for file_path in files_to_remove:
            if os.path.exists(file_path):
                os.remove(file_path)

    def test_basic_chat_sequence_processing(self):
        """Tests that the pipeline correctly processes a sequence of chat messages."""
        try:
            config = load_config(dummy_test_config_path)
            pipeline = EventualPipeline(config)
            pipeline.run() # This will execute step 13, the basic chat flow

            # Assertions to verify the outcome
            # 1. Check if the hypergraph file was created
            self.assertTrue(os.path.exists(self.hypergraph_save_path), "Hypergraph file was not created.")

            # 2. Load the hypergraph and check if it's not empty
            persistence_manager = HypergraphPersistence()
            loaded_hypergraph = persistence_manager.load_hypergraph(self.hypergraph_save_path)
            self.assertIsNotNone(loaded_hypergraph, "Could not load hypergraph from file.")
            # Basic check for some nodes/edges. The exact number will depend on TextProcessor's output.
            # We expect at least some concepts and events to be added from the dummy messages.
            self.assertGreater(len(loaded_hypergraph.get_nodes()), 0, "Hypergraph should contain nodes after processing.")
            self.assertGreater(len(loaded_hypergraph.get_edges()), 0, "Hypergraph should contain edges after processing.")

            # 3. (Optional but recommended) Add more specific assertions based on expected concepts/events
            # This requires knowing what TextProcessor is expected to extract from the dummy messages.
            # For example:
            # self.assertIn("weather", [node['label'] for node in loaded_hypergraph.get_nodes()], "Hypergraph should contain 'weather' concept.")
            # self.assertIn("capital of France", [node['label'] for node in loaded_hypergraph.get_nodes()], "Hypergraph should contain 'capital of France' concept.")

        except Exception as e:
            self.fail(f"An error occurred during the test: {e}")

if __name__ == '__main__':
    unittest.main()
