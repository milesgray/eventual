import unittest
from datetime import datetime, timedelta
from eventual.core import Hypergraph, Concept, Event

class TestHypergraph(unittest.TestCase):
    def test_add_concept(self):
        hypergraph = Hypergraph()
        concept = Concept(concept_id="light_1", name="light", initial_state=1.0)
        hypergraph.add_concept(concept)
        self.assertIn("light_1", hypergraph.concepts)
        # Verify name lookup also works after adding
        retrieved_concept = hypergraph.get_concept_by_name("light")
        self.assertIsNotNone(retrieved_concept)
        self.assertEqual(retrieved_concept.concept_id, "light_1")

    def test_get_concept_by_id_found(self):
        hypergraph = Hypergraph()
        concept = Concept(concept_id="concept_123", name="test concept", initial_state=5.0)
        hypergraph.add_concept(concept)
        retrieved_concept = hypergraph.get_concept(concept.concept_id)
        self.assertIsNotNone(retrieved_concept)
        self.assertEqual(retrieved_concept.concept_id, concept.concept_id)
        self.assertEqual(retrieved_concept.name, concept.name)

    def test_get_concept_by_id_not_found(self):
        hypergraph = Hypergraph()
        retrieved_concept = hypergraph.get_concept("non_existent_id")
        self.assertIsNone(retrieved_concept)

    def test_get_concept_by_name_found_exact_match(self):
        hypergraph = Hypergraph()
        concept = Concept(concept_id="concept_abc", name="Exact Match", initial_state=2.0)
        hypergraph.add_concept(concept)
        retrieved_concept = hypergraph.get_concept_by_name("Exact Match")
        self.assertIsNotNone(retrieved_concept)
        self.assertEqual(retrieved_concept.concept_id, concept.concept_id)

    def test_get_concept_by_name_found_case_insensitive(self):
        hypergraph = Hypergraph()
        concept = Concept(concept_id="concept_def", name="CaseSensitive", initial_state=3.0)
        hypergraph.add_concept(concept)
        retrieved_concept = hypergraph.get_concept_by_name("casesensitive") # Test lower case
        self.assertIsNotNone(retrieved_concept)
        self.assertEqual(retrieved_concept.concept_id, concept.concept_id)
        retrieved_concept = hypergraph.get_concept_by_name("CASESENSITIVE") # Test upper case
        self.assertIsNotNone(retrieved_concept)
        self.assertEqual(retrieved_concept.concept_id, concept.concept_id)

    def test_get_concept_by_name_found_lemmatized(self):
        hypergraph = Hypergraph()
        # Add concept with base lemma name
        concept_run = Concept(concept_id="concept_run_1", name="run", initial_state=1.0)
        hypergraph.add_concept(concept_run)

        # Search using different forms of the word
        retrieved_concept_running = hypergraph.get_concept_by_name("running")
        self.assertIsNotNone(retrieved_concept_running)
        self.assertEqual(retrieved_concept_running.concept_id, concept_run.concept_id)

        retrieved_concept_ran = hypergraph.get_concept_by_name("ran")
        self.assertIsNotNone(retrieved_concept_ran)
        self.assertEqual(retrieved_concept_ran.concept_id, concept_run.concept_id)

    def test_get_concept_by_name_not_found(self):
        hypergraph = Hypergraph()
        concept = Concept(concept_id="concept_ghi", name="Another Concept", initial_state=4.0)
        hypergraph.add_concept(concept)
        retrieved_concept = hypergraph.get_concept_by_name("non_existent_name")
        self.assertIsNone(retrieved_concept)
        retrieved_concept = hypergraph.get_concept_by_name("running") # Test a lemmatized form that doesn't exist
        self.assertIsNone(retrieved_concept)

    def test_add_concept_if_not_exists_new_concept(self):
        hypergraph = Hypergraph()
        concept = Concept(concept_id="new_concept_1", name="new idea", initial_state=1.0)
        returned_concept = hypergraph.add_concept_if_not_exists(concept)
        self.assertEqual(len(hypergraph.concepts), 1)
        self.assertIn("new_concept_1", hypergraph.concepts)
        self.assertEqual(returned_concept.concept_id, "new_concept_1")
        # Verify the returned concept is the instance stored in the hypergraph
        self.assertIs(returned_concept, hypergraph.get_concept("new_concept_1"))

    def test_add_concept_if_not_exists_existing_id(self):
        hypergraph = Hypergraph()
        existing_concept = Concept(concept_id="existing_id_1", name="original name", initial_state=1.0)
        hypergraph.add_concept(existing_concept)

        # Attempt to add a concept with the same ID but different name/state
        new_concept_with_same_id = Concept(concept_id="existing_id_1", name="different name", initial_state=2.0)
        returned_concept = hypergraph.add_concept_if_not_exists(new_concept_with_same_id)

        self.assertEqual(len(hypergraph.concepts), 1) # Should not add a new concept
        self.assertIs(returned_concept, existing_concept) # Should return the original concept instance
        self.assertEqual(returned_concept.name, "original name") # Ensure original data is kept
        self.assertEqual(returned_concept.state, 1.0)

    def test_add_concept_if_not_exists_existing_name(self):
        hypergraph = Hypergraph()
        existing_concept = Concept(concept_id="original_id_1", name="Existing Name", initial_state=1.0)
        hypergraph.add_concept(existing_concept)

        # Attempt to add a concept with a different ID but the same name (lemmatized, case-insensitive)
        new_concept_with_same_name = Concept(concept_id="different_id_1", name="existing name", initial_state=2.0)
        returned_concept = hypergraph.add_concept_if_not_exists(new_concept_with_same_name)

        self.assertEqual(len(hypergraph.concepts), 1) # Should not add a new concept
        self.assertIs(returned_concept, existing_concept) # Should return the original concept instance
        self.assertEqual(returned_concept.concept_id, "original_id_1") # Ensure original data is kept
        self.assertEqual(returned_concept.name, "Existing Name")
        self.assertEqual(returned_concept.state, 1.0)

    def test_add_concept_if_not_exists_existing_id_and_name(self):
        hypergraph = Hypergraph()
        existing_concept = Concept(concept_id="existing_id_2", name="Existing Concept", initial_state=1.0)
        hypergraph.add_concept(existing_concept)

        # Attempt to add a concept with the same ID and name
        same_concept = Concept(concept_id="existing_id_2", name="Existing Concept", initial_state=1.0)
        returned_concept = hypergraph.add_concept_if_not_exists(same_concept)

        self.assertEqual(len(hypergraph.concepts), 1) # Should not add a new concept
        self.assertIs(returned_concept, existing_concept) # Should return the original concept instance


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
        # Verify the event is linked back to the concept instance in the hypergraph
        retrieved_concept = hypergraph.get_concept("light_1")
        self.assertIsNotNone(retrieved_concept)
        self.assertIn(event, retrieved_concept.events)

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
        self.assertNotIn(light_concept, related_concepts) # Ensure the original concept is not included

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