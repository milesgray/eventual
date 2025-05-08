import pytest
import os
import shutil
from datetime import datetime
from eventual.core.hypergraph import Hypergraph
from eventual.core.concept import Concept
from eventual.core.event import Event
from eventual.persistence.hypergraph_persistence import HypergraphPersistence

# Define a temporary directory and file path for testing
TEST_DIR = ".gemini/persistence_tests"
TEST_FILE_PATH = os.path.join(TEST_DIR, "test_hypergraph_data.json")

# Fixture to create and clean up the test file and directory
@pytest.fixture(scope="module")
def persistence_manager():
    manager = HypergraphPersistence()
    # Ensure the test directory exists
    os.makedirs(TEST_DIR, exist_ok=True)
    yield manager
    # Clean up the test directory after all tests in the module are done
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)

# Fixture for a simple hypergraph
@pytest.fixture
def simple_hypergraph():
    hypergraph = Hypergraph()
    concept1 = Concept(concept_id="c1", name="apple", initial_state=1.0)
    concept2 = Concept(concept_id="c2", name="banana", initial_state=0.5)
    hypergraph.add_concept(concept1)
    hypergraph.add_concept(concept2)
    event1 = Event(event_id="e1", timestamp=datetime.now(), concepts={concept1, concept2}, delta=0.2)
    hypergraph.add_event(event1)
    return hypergraph

def test_save_and_load_hypergraph(persistence_manager, simple_hypergraph):
    # Save the hypergraph
    persistence_manager.save_hypergraph(simple_hypergraph, TEST_FILE_PATH)

    # Check if the file was created
    assert os.path.exists(TEST_FILE_PATH)

    # Load the hypergraph
    loaded_hypergraph = persistence_manager.load_hypergraph(TEST_FILE_PATH)

    # Check that the loaded hypergraph is not None
    assert loaded_hypergraph is not None

    # Check if concepts were loaded correctly
    assert len(loaded_hypergraph.concepts) == len(simple_hypergraph.concepts)
    loaded_c1 = loaded_hypergraph.get_concept("c1")
    loaded_c2 = loaded_hypergraph.get_concept("c2")
    assert loaded_c1 is not None
    assert loaded_c2 is not None
    assert loaded_c1.name == "apple"
    assert loaded_c1.state == 1.0
    assert loaded_c2.name == "banana"
    assert loaded_c2.state == 0.5

    # Check if events were loaded correctly and linked to concepts
    assert len(loaded_hypergraph.events) == len(simple_hypergraph.events)
    loaded_e1 = loaded_hypergraph.get_event("e1")
    assert loaded_e1 is not None
    assert loaded_e1.delta == 0.2
    # Check that the concepts in the event are the instances from the loaded hypergraph
    assert len(loaded_e1.concepts) == 2
    assert loaded_c1 in loaded_e1.concepts
    assert loaded_c2 in loaded_e1.concepts

    # Check that events are linked back to concepts
    assert loaded_e1 in loaded_c1.events
    assert loaded_e1 in loaded_c2.events

def test_load_nonexistent_file(persistence_manager):
    # Try to load a file that doesn't exist
    nonexistent_file = os.path.join(TEST_DIR, "nonexistent_hypergraph.json")
    loaded_hypergraph = persistence_manager.load_hypergraph(nonexistent_file)

    # Check that None is returned
    assert loaded_hypergraph is None

def test_delete_hypergraph_file(persistence_manager, simple_hypergraph):
    # Save the hypergraph first
    persistence_manager.save_hypergraph(simple_hypergraph, TEST_FILE_PATH)
    assert os.path.exists(TEST_FILE_PATH)

    # Delete the file
    persistence_manager.delete_hypergraph_file(TEST_FILE_PATH)

    # Check that the file is deleted
    assert not os.path.exists(TEST_FILE_PATH)

    # Try deleting a nonexistent file (should not raise an error)
    persistence_manager.delete_hypergraph_file(os.path.join(TEST_DIR, "another_nonexistent_file.json"))

# Add tests for more complex hypergraphs, different data types in metadata, etc. if needed.
