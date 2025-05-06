import pytest
from eventual.core import Hypergraph, Concept, Event
from eventual.streams.sensory_event_stream import SensoryEventStream
from eventual.streams.instance_stream import InstanceStream
from eventual.streams.delta_stream import DeltaStream

def test_compute_deltas():
    hypergraph = Hypergraph()
    sensory_stream = SensoryEventStream(hypergraph)
    instance_stream = InstanceStream(sensory_stream)
    delta_stream = DeltaStream(hypergraph, instance_stream, threshold=0.1)

    # Add a concept to the hypergraph
    concept = Concept(concept_id="light_1", name="light", initial_state=1.0)
    hypergraph.add_concept(concept)

    # Simulate an instance stream
    instance_stream.sensory_event_stream.events = [
        Event(event_id="event_1", timestamp="2023-10-01", concept=concept, delta=0.0)
    ]

    # Compute deltas
    events = delta_stream.compute_deltas()
    assert len(events) == 0  # No significant change yet

    # Update the concept state and compute deltas again
    concept.update_state(0.8)
    events = delta_stream.compute_deltas()
    assert len(events) == 1  # Significant change detected