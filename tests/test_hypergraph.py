import unittest
from datetime import datetime
from eventual.core import Hypergraph, Concept, Event

class TestHypergraph(unittest.TestCase):
    def test_add_concept(self):
        hypergraph = Hypergraph()
        concept = Concept(concept_id="light_1", name="light", initial_state=1.0)
        hypergraph.add_concept(concept)
        self.assertIn("light_1", hypergraph.concepts)

    def test_add_event(self):
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
        self.assertEqual(len(hypergraph.events), 1)

    def test_find_related_concepts(self):
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
        self.assertIn(darkness_concept, related_concepts)

if __name__ == '__main__':
    unittest.main()