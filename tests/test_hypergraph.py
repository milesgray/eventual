import unittest
from datetime import datetime, timedelta
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

    def test_retrieve_knowledge_matching_concepts(self):
        hypergraph = Hypergraph()
        concept1 = Concept(concept_id="concept_1", name="apple", initial_state=1.0)
        concept2 = Concept(concept_id="concept_2", name="banana", initial_state=1.0)
        concept3 = Concept(concept_id="concept_3", name="orange", initial_state=1.0)
        hypergraph.add_concept(concept1)
        hypergraph.add_concept(concept2)
        hypergraph.add_concept(concept3)

        # Add events involving these concepts
        event1 = Event(event_id="event_1", timestamp=datetime.now(), concepts={concept1, concept2}, delta=0.1)
        event2 = Event(event_id="event_2", timestamp=datetime.now(), concepts={concept2, concept3}, delta=0.2)
        hypergraph.add_event(event1)
        hypergraph.add_event(event2)

        # Query for concepts and events related to "apple"
        query = "tell me about apples"
        relevant_concepts, relevant_events = hypergraph.retrieve_knowledge(query)

        # Check that the relevant concept (apple) is returned
        self.assertEqual(len(relevant_concepts), 1)
        self.assertIn(concept1, relevant_concepts)

        # Check that events involving apple are returned (event1)
        self.assertEqual(len(relevant_events), 1)
        self.assertIn(event1, relevant_events)

    def test_retrieve_knowledge_no_match(self):
        hypergraph = Hypergraph()
        concept1 = Concept(concept_id="concept_1", name="apple", initial_state=1.0)
        hypergraph.add_concept(concept1)

        # Query for something not in the hypergraph
        query = "tell me about grapes"
        relevant_concepts, relevant_events = hypergraph.retrieve_knowledge(query)

        # Check that no concepts or events are returned
        self.assertEqual(len(relevant_concepts), 0)
        self.assertEqual(len(relevant_events), 0)

    def test_retrieve_knowledge_multiple_matches_and_events(self):
        hypergraph = Hypergraph()
        concept1 = Concept(concept_id="concept_1", name="apple", initial_state=1.0)
        concept2 = Concept(concept_id="concept_2", name="banana", initial_state=1.0)
        concept3 = Concept(concept_id="concept_3", name="orange", initial_state=1.0)
        hypergraph.add_concept(concept1)
        hypergraph.add_concept(concept2)
        hypergraph.add_concept(concept3)

        # Add events involving these concepts
        event1 = Event(event_id="event_1", timestamp=datetime.now() - timedelta(days=1), concepts={concept1, concept2}, delta=0.1)
        event2 = Event(event_id="event_2", timestamp=datetime.now(), concepts={concept2, concept3}, delta=0.2)
        event3 = Event(event_id="event_3", timestamp=datetime.now(), concepts={concept1, concept3}, delta=0.3)
        hypergraph.add_event(event1)
        hypergraph.add_event(event2)
        hypergraph.add_event(event3)

        # Query for concepts and events related to "banana"
        query = "what do you know about bananas?"
        relevant_concepts, relevant_events = hypergraph.retrieve_knowledge(query)

        # Check that the relevant concept (banana) is returned
        self.assertEqual(len(relevant_concepts), 1)
        self.assertIn(concept2, relevant_concepts)

        # Check that events involving banana are returned (event1 and event2)
        self.assertEqual(len(relevant_events), 2)
        self.assertIn(event1, relevant_events)
        self.assertIn(event2, relevant_events)

    def test_retrieve_knowledge_query_with_different_forms(self):
        hypergraph = Hypergraph()
        concept1 = Concept(concept_id="concept_1", name="run", initial_state=1.0) # Lemma is "run"
        hypergraph.add_concept(concept1)

        # Add an event involving the concept
        event1 = Event(event_id="event_1", timestamp=datetime.now(), concepts={concept1}, delta=0.1)
        hypergraph.add_event(event1)

        # Query using a different form of the word
        query = "running faster"
        relevant_concepts, relevant_events = hypergraph.retrieve_knowledge(query)

        # Check that the concept with the matching lemma is returned
        self.assertEqual(len(relevant_concepts), 1)
        self.assertIn(concept1, relevant_concepts)

        # Check that events involving the concept are returned
        self.assertEqual(len(relevant_events), 1)
        self.assertIn(event1, relevant_events)

if __name__ == '__main__':
    unittest.main()