import pytest
from eventual.core import Hypergraph, Concept, Event, TemporalBoundaryConfig
from eventual.streams.sensory_event_stream import SensoryEventStream
from eventual.streams.instance_stream import InstanceStream
from eventual.streams.delta_stream import DeltaStream

def test_compute_deltas():
    temporal_boundary_config = TemporalBoundaryConfig(threshold=0.1)
    sensory_stream = SensoryEventStream(temporal_boundary_config=temporal_boundary_config)
    instance_stream = InstanceStream()
    delta_stream = DeltaStream(instance_stream, threshold=0.1)

    # Add a concept to the hypergraph
    hypergraph = Hypergraph()
    concept = Concept(concept_id="light_1", name="light", initial_state=1.0)
    hypergraph.add_concept(concept)

    # Simulate an instance stream
    initial_events = [{
        "event_id": "event_1",
        "timestamp": "2023-10-01",
        "concept_id": "light_1",
        "delta": 0.0
    }]

    # Compute deltas
    events = delta_stream.compute_deltas(initial_events)
    assert len(events) == 0  # No significant change yet

    # Update the concept state and compute deltas again
    concept.update_state(0.8)
    updated_events = [{
        "event_id": "event_1",
        "timestamp": "2023-10-01",
        "concept_id": "light_1",
        "delta": 0.2
    }]

    events = delta_stream.compute_deltas(updated_events)
    assert len(events) == 1  # Significant change detected