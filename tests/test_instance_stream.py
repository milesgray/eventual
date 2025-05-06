import pytest
from datetime import datetime
from eventual.core import Hypergraph, Concept, Event
from eventual.streams.sensory_event_stream import SensoryEventStream
from eventual.streams.instance_stream import InstanceStream, Instance

def test_process_event():
    hypergraph = Hypergraph()
    concept = Concept(concept_id="light_1", name="light", initial_state=1.0)
    hypergraph.add_concept(concept)

    event = Event(
        event_id="event_1",
        timestamp=datetime.now(),
        concept=concept,
        delta=0.5,
    )
    hypergraph.add_event(event)

    instance_stream = InstanceStream(hypergraph)
    instances = instance_stream.process_event(event)

    assert len(instances) == 1
    assert instances[0].concept_id == "light_1"
    assert instances[0].value == 0.5

def test_process_sensory_event_stream():
    hypergraph = Hypergraph()
    concept = Concept(concept_id="light_1", name="light", initial_state=1.0)
    hypergraph.add_concept(concept)

    event = Event(
        event_id="event_1",
        timestamp=datetime.now(),
        concept=concept,
        delta=0.5,
    )
    hypergraph.add_event(event)

    sensory_event_stream = SensoryEventStream(hypergraph)
    instance_stream = InstanceStream(hypergraph)
    instances = instance_stream.process_sensory_event_stream(sensory_event_stream)

    assert len(instances) == 1
    assert instances[0].concept_id == "light_1"

def test_get_instances_by_concept():
    hypergraph = Hypergraph()
    concept = Concept(concept_id="light_1", name="light", initial_state=1.0)
    hypergraph.add_concept(concept)

    event = Event(
        event_id="event_1",
        timestamp=datetime.now(),
        concept=concept,
        delta=0.5,
    )
    hypergraph.add_event(event)

    instance_stream = InstanceStream(hypergraph)
    instance_stream.process_event(event)

    instances = instance_stream.get_instances_by_concept("light_1")
    assert len(instances) == 1
    assert instances[0].concept_id == "light_1"