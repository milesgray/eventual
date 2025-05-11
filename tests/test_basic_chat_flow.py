import pytest
import os
import shutil
from datetime import timedelta
from unittest.mock import patch, MagicMock
import json

# Import Language directly from eventual.pipeline
from eventual.pipeline import EventualPipeline, Config, Language
from eventual.core.hypergraph import Hypergraph
from eventual.persistence.hypergraph_persistence import HypergraphPersistence
from eventual.processors.processor_output import ProcessorOutput, ExtractedConcept, ExtractedEvent

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
        # Use Language directly, not as a nested class of Config
        languages=[Language(code="en", name="English")],
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

@patch('eventual.processors.text_processor.litellm.completion')
def test_basic_chat_flow_sequence(mock_litellm_completion, setup_basic_chat_flow_tests, basic_chat_flow_config):
    # Mock LLM responses for each message
    mock_responses = [
        # Response for "Hi, I'm interested in booking a flight."
        {
            "concepts": ["booking", "flight"],
            "relationships": [["booking", "flight"]]
        },
        # Response for "I want to go to Paris next month."
        {
            "concepts": ["go", "Paris", "month"],
            "relationships": [["go", "Paris"]]
        },
        # Response for "My budget is around 700 dollars."
        {
            "concepts": ["budget", "700 dollars"],
            "relationships": [["budget", "700 dollars"]]
        },
        # Response for "Actually, I prefer flying to Rome instead."
        {
            "concepts": ["prefer", "flying", "Rome"],
            "relationships": [["prefer", "flying"], ["flying", "Rome"]]
        },
        # Response for "Is the budget still okay for Rome?"
        {
            "concepts": ["budget", "Rome", "okay"],
            "relationships": [["budget", "okay"], ["okay", "Rome"]]
        },
    ]

    # Configure the mock to return responses sequentially
    mock_litellm_completion.side_effect = [
        MagicMock(choices=[MagicMock(message=MagicMock(content=json.dumps(resp)))]
                  ) for resp in mock_responses
    ]

    # Initial run - hypergraph should be created and populated by the first message
    pipeline = EventualPipeline(basic_chat_flow_config)
    pipeline.run() # This runs the _run_basic_chat_flow

    # Verify the hypergraph file was created and contains data
    assert os.path.exists(TEST_HYPERGRAPH_PATH)
    persistence_manager = HypergraphPersistence()
    loaded_hypergraph_after_first_run = persistence_manager.load_hypergraph(TEST_HYPERGRAPH_PATH)
    assert loaded_hypergraph_after_first_run is not None

    # Define expected concepts and events after the first run (processing first 3 messages)
    expected_concepts_after_first_run = {"book", "flight", "go", "paris", "month", "budget", "700"} # Lemmatized concepts
    expected_events_after_first_run_relationships = {
        tuple(sorted(["booking", "flight"])),
        tuple(sorted(["go", "paris"])),
        tuple(sorted(["budget", "700 dollar"])),
    } # Lemmatized relationships

    # Check concepts after the first run
    extracted_concept_names_after_first_run = {c.name for c in loaded_hypergraph_after_first_run.concepts.values()}
    print(f"extracted_concept_names_after_first_run: {extracted_concept_names_after_first_run}")
    print(f"expected_concepts_after_first_run: {expected_concepts_after_first_run}")
    assert extracted_concept_names_after_first_run == expected_concepts_after_first_run

    # Check events after the first run (only checking relationship events for simplicity)
    extracted_relationships_after_first_run = set()
    for event in loaded_hypergraph_after_first_run.events.values():
        if event.event_type == 'relationship':
            # Ensure concept identifiers are lemmatized and stored as a tuple for set comparison
            lemmatized_identifiers = tuple(sorted([c.name for c in event.concepts]))
            extracted_relationships_after_first_run.add(lemmatized_identifiers)

    assert extracted_relationships_after_first_run == expected_events_after_first_run_relationships

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

    # Define expected concepts and events after the second run (cumulative)
    expected_concepts_after_second_run = expected_concepts_after_first_run.union({"prefer", "fly", "rome", "okay"}) # Lemmatized concepts
    expected_events_after_second_run_relationships = expected_events_after_first_run_relationships.union({
         tuple(sorted(["prefer", "fly"])),
         tuple(sorted(["fly", "rome"])),
         tuple(sorted(["budget", "okay"])), # budget should already exist from the first run
         tuple(sorted(["okay", "rome"])), # rome should be added in this run
    })


    # Check concepts after the second run
    extracted_concept_names_after_second_run = {c.name for c in loaded_hypergraph_after_second_run.concepts.values()}
    assert extracted_concept_names_after_second_run == expected_concepts_after_second_run

    # Check events after the second run
    extracted_relationships_after_second_run = set()
    for event in loaded_hypergraph_after_second_run.events.values():
        if event.event_type == 'relationship':
            # Ensure concept identifiers are lemmatized and stored as a tuple for set comparison
            lemmatized_identifiers = tuple(sorted([c.name for c in event.concepts]))
            extracted_relationships_after_second_run.add(lemmatized_identifiers)

    assert extracted_relationships_after_second_run == expected_events_after_second_run_relationships


    # Further checks (will require manual verification due to environment limitation):
    # - Manually inspect the generated context strings in the console output for each message.
    #   Verify that the retrieved knowledge (concepts and events) in the context string is relevant to the message and the hypergraph's cumulative state.
    #   Verify that short-term memory (recent events) is included based on recent_memory_window_minutes.
    # - Manually inspect the final hypergraph state (by loading the JSON file) to ensure it reflects the concepts and events from all processed messages.

# Additional tests to consider (manual verification for now):
# - Test with empty messages list.
# - Test with different recent_memory_window_minutes values.
# - Test error handling scenarios (e.g., missing config settings).

