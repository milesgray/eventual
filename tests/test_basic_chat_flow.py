import pytest
import os
import shutil
from datetime import timedelta
from eventual.pipeline import EventualPipeline, Config
from eventual.core.hypergraph import Hypergraph
from eventual.persistence.hypergraph_persistence import HypergraphPersistence

# Define a temporary directory and file path for testing persistence
TEST_DIR = ".gemini/basic_chat_flow_tests"
TEST_HYPERGRAPH_PATH = os.path.join(TEST_DIR, "chat_hypergraph.json")

# Fixture to create and clean up the test directory and hypergraph file
@pytest.fixture(scope="module")
def setup_basic_chat_flow_tests():
    # Ensure the test directory exists
    os.makedirs(TEST_DIR, exist_ok=True)
    # Clean up any previous test hypergraph file
    if os.path.exists(TEST_HYPERGRAPH_PATH):
        os.remove(TEST_HYPERGRAPH_PATH)

    yield # Run the tests

    # Clean up the test directory after all tests in the module are done
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)

# Fixture for a basic pipeline config tailored for the chat flow
@pytest.fixture
def basic_chat_flow_config():
    # This mirrors the structure expected by _run_basic_chat_flow
    config = Config(
        languages=[Config.Language(code="en", name="English")],
        steps={13}, # Only run the basic chat flow step
        data_sources={},
        llm_settings={}, # Basic settings, not used in this test directly
        chat_settings={
            "example_messages": [
                "Hi, I'm interested in booking a flight.",
                "I want to go to Paris next month.",
                "My budget is around 700 dollars."
            ],
            "recent_memory_window_minutes": 10,
            "hypergraph_save_path": TEST_HYPERGRAPH_PATH
        }
    )
    return config

def test_basic_chat_flow_sequence(setup_basic_chat_flow_tests, basic_chat_flow_config):
    # Initial run - hypergraph should be created and populated by the first message
    pipeline = EventualPipeline(basic_chat_flow_config)
    pipeline.run() # This runs the _run_basic_chat_flow

    # Verify the hypergraph file was created and contains data
    assert os.path.exists(TEST_HYPERGRAPH_PATH)
    persistence_manager = HypergraphPersistence()
    loaded_hypergraph_after_first_run = persistence_manager.load_hypergraph(TEST_HYPERGRAPH_PATH)
    assert loaded_hypergraph_after_first_run is not None
    # Basic check: should have concepts and events from the first message
    assert len(loaded_hypergraph_after_first_run.concepts) > 0
    assert len(loaded_hypergraph_after_first_run.events) > 0

    # Modify messages for a second run to test persistence and cumulative effect
    basic_chat_flow_config.chat_settings["example_messages"] = [
        "Actually, I prefer flying to Rome instead.",
        "Is the budget still okay for Rome?"
    ]

    # Second run - hypergraph should be loaded and further updated
    pipeline_second_run = EventualPipeline(basic_chat_flow_config)
    pipeline_second_run.run() # This runs the _run_basic_chat_flow again, loading the previous state

    # Verify the hypergraph file was updated and contains data from both runs
    loaded_hypergraph_after_second_run = persistence_manager.load_hypergraph(TEST_HYPERGRAPH_PATH)
    assert loaded_hypergraph_after_second_run is not None
    # Should have more concepts/events than after the first run (assuming new concepts/events are extracted)
    assert len(loaded_hypergraph_after_second_run.concepts) >= len(loaded_hypergraph_after_first_run.concepts)
    assert len(loaded_hypergraph_after_second_run.events) >= len(loaded_hypergraph_after_first_run.events)

    # Further checks (will require manual verification due to environment limitation):
    # - Manually inspect the generated context strings in the console output for each message.
    #   Verify that the retrieved knowledge (concepts and events) in the context string is relevant to the message and the hypergraph's cumulative state.
    #   Verify that short-term memory (recent events) is included based on recent_memory_window_minutes.
    # - Manually inspect the final hypergraph state (by loading the JSON file) to ensure it reflects the concepts and events from all processed messages.

# Additional tests to consider (manual verification for now):
# - Test with empty messages list.
# - Test with different recent_memory_window_minutes values.
# - Test error handling scenarios (e.g., missing config settings).

