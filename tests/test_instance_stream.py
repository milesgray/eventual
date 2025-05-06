import unittest
from datetime import datetime
from eventual.core import Hypergraph, Concept, Event, TemporalBoundaryConfig
from eventual.streams.sensory_event_stream import SensoryEventStream
from eventual.streams.instance_stream import InstanceStream, Instance

class TestInstanceStream(unittest.TestCase):
    def test_process_event(self):
        temporal_boundary_config = TemporalBoundaryConfig(threshold=0.1)
        sensory_event_stream = SensoryEventStream(temporal_boundary_config=temporal_boundary_config)
        instance_stream = InstanceStream()

        hypergraph = Hypergraph()
        concept = Concept(concept_id="light_1", name="light", initial_state=1.0)
        hypergraph.add_concept(concept)

        event_data = {
            "event_id": "event_1",
            "timestamp": datetime.now(),
            "concept_id": "light_1",
            "delta": 0.5,
        }

        instances = instance_stream.process_event(event_data)

        self.assertEqual(len(instances), 1)
        self.assertEqual(instances[0].concept_id, "light_1")
        self.assertEqual(instances[0].value, 0.5)

    def test_process_sensory_event_stream(self):
        temporal_boundary_config = TemporalBoundaryConfig(threshold=0.1)
        sensory_event_stream = SensoryEventStream(temporal_boundary_config=temporal_boundary_config)
        instance_stream = InstanceStream()
        sensory_event_stream.add_sensor("sensor_1", "text", lambda x: {"light": x})
        sensory_output = sensory_event_stream.ingest("sensor_1", 0.5)
        instances = instance_stream.process(sensory_output)
        self.assertEqual(len(instances), 1)
        if instances:
            self.assertEqual(instances[0].concept_id, "concept_light")

    def test_get_instances_by_concept(self):
        temporal_boundary_config = TemporalBoundaryConfig(threshold=0.1)
        sensory_event_stream = SensoryEventStream(temporal_boundary_config=temporal_boundary_config)
        instance_stream = InstanceStream()
        sensory_event_stream.add_sensor("sensor_1", "text", lambda x: {"light": x})
        sensory_output = sensory_event_stream.ingest("sensor_1", 0.5)
        instances = instance_stream.process(sensory_output)

        instances = instance_stream.get_instances_by_concept("concept_light")
        self.assertEqual(len(instances), 1)
        if instances:
            self.assertEqual(instances[0].concept_id, "concept_light")

if __name__ == '__main__':
    unittest.main()