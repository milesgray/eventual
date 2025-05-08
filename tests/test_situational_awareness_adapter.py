import pytest
from datetime import datetime, timedelta
from eventual.core.hypergraph import Hypergraph
from eventual.core.concept import Concept
from eventual.core.event import Event
from eventual.adapters.situational_awareness_adapter import SituationalAwarenessAdapter

# Fixture for a Hypergraph with some concepts and events, including older ones
@pytest.fixture
def hypergraph_with_history():
    hypergraph = Hypergraph()
    concept1 = Concept(concept_id="concept_1", name="apple", initial_state=1.0)
    concept2 = Concept(concept_id="concept_2", name="banana", initial_state=1.0)
    concept3 = Concept(concept_id="concept_3", name="orange", initial_state=1.0)
    concept4 = Concept(concept_id="concept_4", name="grape", initial_state=1.0)
    hypergraph.add_concept(concept1)
    hypergraph.add_concept(concept2)
    hypergraph.add_concept(concept3)
    hypergraph.add_concept(concept4)

    # Older events (long-term memory)
    older_event_timestamp = datetime.now() - timedelta(days=7)
    event1_old = Event(event_id="event_1_old", timestamp=older_event_timestamp, concepts={concept1, concept2}, delta=0.1, metadata={"source": "test_old"})
    event2_old = Event(event_id="event_2_old", timestamp=older_event_timestamp, concepts={concept3, concept4}, delta=0.2, metadata={"source": "test_old"})
    hypergraph.add_event(event1_old)
    hypergraph.add_event(event2_old)

    # Recent events (short-term memory)
    recent_event_timestamp = datetime.now() - timedelta(minutes=5)
    event3_recent = Event(event_id="event_3_recent", timestamp=recent_event_timestamp, concepts={concept1, concept3}, delta=0.3, metadata={"source": "test_recent"})
    event4_recent = Event(event_id="event_4_recent", timestamp=recent_event_timestamp, concepts={concept2, concept4}, delta=0.4, metadata={"source": "test_recent"})
    hypergraph.add_event(event3_recent)
    hypergraph.add_event(event4_recent)

    return hypergraph

def test_adapter_initialization(hypergraph_with_history):
    adapter = SituationalAwarenessAdapter(hypergraph=hypergraph_with_history)
    assert adapter._hypergraph is hypergraph_with_history

def test_adapter_initialization_with_invalid_hypergraph():
    with pytest.raises(TypeError):
        SituationalAwarenessAdapter(hypergraph="not a hypergraph")

def test_generate_context_query_only(hypergraph_with_history):
    adapter = SituationalAwarenessAdapter(hypergraph=hypergraph_with_history)
    query = "tell me about apples"
    context = adapter.generate_context(query) # No recent_time_window

    assert context != ""
    # Check for expected concepts and events in the context string as substrings
    assert "Concepts related to the query:" in context # Updated assertion
    assert "apple" in context
    assert "Relevant Events:" in context

    # Check for parts of the expected event descriptions (flexible on order and full string match)
    assert "Event event_1_old:" in context and ("Concepts [apple, banana]" in context or "Concepts [banana, apple]" in context) and "Delta 0.10" in context
    assert "Event event_3_recent:" in context and ("Concepts [apple, orange]" in context or "Concepts [orange, apple]" in context) and "Delta 0.30" in context

    # Should not include event_2_old as it doesn't involve apple
    assert "event_2_old" not in context
    # event_4_recent doesn't directly involve apple
    # assert "event_4_recent" not in context

def test_generate_context_with_recent_time_window(hypergraph_with_history):
    adapter = SituationalAwarenessAdapter(hypergraph=hypergraph_with_history)
    query = "tell me about bananas" # Query for banana
    recent_time_window = timedelta(minutes=10) # Window includes recent events
    context = adapter.generate_context(query, recent_time_window=recent_time_window)

    assert context != ""
    assert "Concepts related to the query and recent activity:" in context
    assert "apple" in context
    assert "banana" in context
    assert "grape" in context
    assert "orange" in context

    assert "Relevant Events:" in context

    # Check for relevant event descriptions (flexible on concept order in event and overall order)
    assert "Event event_1_old:" in context and ("Concepts [apple, banana]" in context or "Concepts [banana, apple]" in context) and "Delta 0.10" in context
    assert "Event event_3_recent:" in context and ("Concepts [apple, orange]" in context or "Concepts [orange, apple]" in context) and "Delta 0.30" in context
    assert "Event event_4_recent:" in context and ("Concepts [banana, grape]" in context or "Concepts [grape, banana]" in context) and "Delta 0.40" in context

    # Should not include older events not involving banana and not recent
    assert "event_2_old" not in context

def test_generate_context_only_recent_time_window(hypergraph_with_history):
    adapter = SituationalAwarenessAdapter(hypergraph=hypergraph_with_history)
    query = "" # Empty query
    recent_time_window = timedelta(minutes=10) # Window includes recent events
    context = adapter.generate_context(query, recent_time_window=recent_time_window)

    assert context != ""
    # Check for the header indicating concepts related to recent activity
    assert "Concepts related to recent activity:" in context
    assert "apple" in context
    assert "banana" in context
    assert "grape" in context
    assert "orange" in context

    assert "Relevant Events:" in context
    # Should include only recent events (event_3_recent, event_4_recent)
    assert "Event event_3_recent:" in context and ("Concepts [apple, orange]" in context or "Concepts [orange, apple]" in context) and "Delta 0.30" in context
    assert "Event event_4_recent:" in context and ("Concepts [banana, grape]" in context or "Concepts [grape, banana]" in context) and "Delta 0.40" in context

    # Should not include older events
    assert "event_1_old" not in context
    assert "event_2_old" not in context

# Need to add tests for: 
# - Cases with no concepts or events in hypergraph
# - Edge cases with time windows (e.g., very small or large window)
# - Interaction with future summarization logic
