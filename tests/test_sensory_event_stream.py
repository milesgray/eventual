import pytest
from eventual.core import Hypergraph, TemporalBoundaryConfig, Concept, Event
from eventual.streams.sensory_event_stream import SensoryEventStream

def test_add_sensor():
    temporal_boundary_config = TemporalBoundaryConfig(threshold=0.1)
    stream = SensoryEventStream(temporal_boundary_config=temporal_boundary_config)
    stream.add_sensor("sensor_1", "text", lambda x: {"light": 1.0})
    assert "sensor_1" in stream.sensors

def test_ingest_text_data():
    hypergraph = Hypergraph()
    temporal_boundary_config = TemporalBoundaryConfig(threshold=0.1)
    stream = SensoryEventStream(temporal_boundary_config=temporal_boundary_config)
    stream.add_sensor("sensor_1", "text", lambda x: {"light": 1.0})
    events = stream.ingest("sensor_1", "The light is too bright.")
    assert len(events) == 1
    assert events[0]["concept_id"] == "concept_light"

def test_ingest_numerical_data():
    hypergraph = Hypergraph()
    temporal_boundary_config = TemporalBoundaryConfig(threshold=0.1)
    stream = SensoryEventStream(temporal_boundary_config=temporal_boundary_config)
    stream.add_sensor("sensor_2", "light", lambda x: {"light": x / 100.0})
    events = stream.ingest("sensor_2", 75.0)
    assert len(events) == 1
    assert events[0]["concept_id"] == "concept_light"

def test_ingest_invalid_sensor():
    temporal_boundary_config = TemporalBoundaryConfig(threshold=0.1)
    stream = SensoryEventStream(temporal_boundary_config=temporal_boundary_config)
    with pytest.raises(ValueError):
        stream.ingest("invalid_sensor", "Some data")