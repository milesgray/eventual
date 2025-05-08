import pytest
from datetime import datetime
from eventual.core.hypergraph import Hypergraph
from eventual.core.concept import Concept
from eventual.core.event import Event
from eventual.adapters.situational_awareness_adapter import SituationalAwarenessAdapter

# Fixture for a Hypergraph with some concepts and events
@pytest.fixture
def populated_hypergraph():
    hypergraph = Hypergraph()
    concept1 = Concept(concept_id="concept_1", name="apple", initial_state=1.0)
    concept2 = Concept(concept_id="concept_2", name="banana", initial_state=1.0)
    concept3 = Concept(concept_id="concept_3", name="orange", initial_state=1.0)
    hypergraph.add_concept(concept1)
    hypergraph.add_concept(concept2)
    hypergraph.add_concept(concept3)

    event1 = Event(event_id="event_1", timestamp=datetime.now(), concepts={concept1, concept2}, delta=0.1, metadata={"source": "test"})
    event2 = Event(event_id="event_2", timestamp=datetime.now(), concepts={concept2, concept3}, delta=0.2, metadata={"source": "test"})
    hypergraph.add_event(event1)
    hypergraph.add_event(event2)

    return hypergraph

def test_adapter_initialization(populated_hypergraph):
    adapter = SituationalAwarenessAdapter(hypergraph=populated_hypergraph)
    assert adapter._hypergraph is populated_hypergraph

def test_adapter_initialization_with_invalid_hypergraph():
    with pytest.raises(TypeError):
        SituationalAwarenessAdapter(hypergraph="not a hypergraph")

def test_generate_context_with_relevant_knowledge(populated_hypergraph):
    adapter = SituationalAwarenessAdapter(hypergraph=populated_hypergraph)
    query = "tell me about apples"
    context = adapter.generate_context(query)

    # Check that the context string is not empty
    assert context != ""

    # Check for the presence of key substrings and structure
    assert "Concepts related to the query: apple." in context
    assert "Relevant Events:" in context
    # Check for parts of the event description
    assert "Event event_1: Concepts [apple, banana], Delta 0.10" in context or "Event event_1: Concepts [banana, apple], Delta 0.10" in context # Account for potential concept order variation
    assert "Metadata {'source': 'test'}" in context

    # Check that irrelevant concepts are not explicitly mentioned as related to the query (though they might appear in event descriptions)
    assert "orange" not in context.split("Relevant Events:")[0] # Check only the part before event descriptions

def test_generate_context_no_relevant_knowledge(populated_hypergraph):
    adapter = SituationalAwarenessAdapter(hypergraph=populated_hypergraph)
    query = "tell me about grapes"
    context = adapter.generate_context(query)

    # Check that the context string is empty when no relevant knowledge is found
    assert context == ""

def test_generate_context_multiple_relevant_concepts_and_events(populated_hypergraph):
    adapter = SituationalAwarenessAdapter(hypergraph=populated_hypergraph)
    query = "what about bananas and oranges?"
    context = adapter.generate_context(query)

    assert context != ""
    assert "Concepts related to the query: banana, orange." in context or "Concepts related to the query: orange, banana." in context # Account for potential concept order variation
    assert "Relevant Events:" in context

    # Check for presence of both relevant event descriptions
    event1_present = ("Event event_1: Concepts [apple, banana], Delta 0.10" in context or "Event event_1: Concepts [banana, apple], Delta 0.10" in context) and ("Metadata {'source': 'test'}" in context)
    event2_present = ("Event event_2: Concepts [banana, orange], Delta 0.20" in context or "Event event_2: Concepts [orange, banana], Delta 0.20" in context) and ("Metadata {'source': 'test'}" in context)

    assert event1_present
    assert event2_present

# Add more tests for different query types or context generation strategies later
