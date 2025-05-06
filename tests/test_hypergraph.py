import pytest
from datetime import datetime
from eventual.core import Hypergraph, Concept, Event

def test_add_concept():
    hypergraph = Hypergraph()
    concept = Concept(concept_id="light_1", name="light", initial_state=1.0)
    hypergraph.add_concept(concept)
    assert "light_1" in hypergraph.concepts

def test_add_event():
    hypergraph = Hypergraph()
    concept = Concept(concept_id="light_1", name="light", initial_state=1.0)
    hypergraph.add_concept(concept)
    event = Event(
        event_id="event_1",
        timestamp=datetime.now(),
        concepts={concept},
        delta=0.5
    )
    hypergraph.add_event(event)
    assert len(hypergraph.events) == 1

def test_find_related_concepts():
    hypergraph = Hypergraph()
    light_concept = Concept(concept_id="light_1", name="light", initial_state=1.0)
    darkness_concept = Concept(concept_id="darkness_1", name="darkness", initial_state=0.0)
    hypergraph.add_concept(light_concept)
    hypergraph.add_concept(darkness_concept)
    event = Event(
        event_id="event_1",
        timestamp=datetime.now(),
        concepts={light_concept, darkness_concept},
        delta=0.5
    )
    hypergraph.add_event(event)
    related_concepts = hypergraph.find_related_concepts("light_1")
    assert darkness_concept in related_concepts