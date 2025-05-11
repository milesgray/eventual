import unittest
from datetime import datetime, timedelta
from eventual.core import Hypergraph, Concept, Event
import logging # Import logging

# Configure logging for the test to capture warnings
logging.basicConfig(level=logging.INFO)

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

    def test_add_event_single_concept(self):
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
        self.assertIn(retrieved_concept, hypergraph.events["event_1"].concepts) # Verify concept in event is the stored instance
        self.assertEqual(len(hypergraph.events["event_1"].concepts), 1)

    def test_add_event_links_correct_concept_instance(self):
        hypergraph = Hypergraph()
        # Add the original concept instance
        original_concept = Concept(concept_id="concept_to_link", name="linked concept", initial_state=1.0)
        hypergraph.add_concept(original_concept)

        # Create a *new* concept instance with the same ID
        new_concept_instance = Concept(concept_id="concept_to_link", name="different instance", initial_state=99.0)

        # Create an event using the new concept instance
        event = Event(
            event_id="event_link_test",
            timestamp=datetime.now(),
            concepts={new_concept_instance},
            delta=1.0
        )

        hypergraph.add_event(event)

        # Retrieve the event from the hypergraph
        retrieved_event = hypergraph.get_event("event_link_test")
        self.assertIsNotNone(retrieved_event)

        # Verify the concept in the retrieved event's concepts set is the *original* instance from the hypergraph
        self.assertEqual(len(retrieved_event.concepts), 1)
        linked_concept_in_event = list(retrieved_event.concepts)[0]
        self.assertIs(linked_concept_in_event, original_concept) # Assert that it's the exact same object in memory
        self.assertEqual(linked_concept_in_event.name, "linked concept") # Verify it has the original name
        self.assertEqual(linked_concept_in_event.state, 1.0) # Verify it has the original state

        # Verify the event is linked back to the original concept instance
        retrieved_concept = hypergraph.get_concept("concept_to_link")
        self.assertIsNotNone(retrieved_concept)
        self.assertIn(retrieved_event, retrieved_concept.events)

    def test_add_event_with_multiple_concepts(self):
        hypergraph = Hypergraph()
        # Use concept names with distinct lemmas
        concept1 = Concept(concept_id="concept_multi_1", name="apple", initial_state=1.0)
        concept2 = Concept(concept_id="concept_multi_2", name="banana", initial_state=2.0)
        concept3 = Concept(concept_id="concept_multi_3", name="orange", initial_state=3.0)
        hypergraph.add_concept(concept1)
        hypergraph.add_concept(concept2)
        hypergraph.add_concept(concept3)

        event = Event(
            event_id="event_multi",
            timestamp=datetime.now(),
            concepts={concept1, concept2, concept3},
            delta=0.1
        )

        hypergraph.add_event(event)

        self.assertEqual(len(hypergraph.events), 1)
        retrieved_event = hypergraph.get_event("event_multi")
        self.assertIsNotNone(retrieved_event)

        # Verify all original concept instances are in the event's concepts set within the hypergraph
        self.assertEqual(len(retrieved_event.concepts), 3)
        self.assertIn(concept1, retrieved_event.concepts)
        self.assertIn(concept2, retrieved_event.concepts)
        self.assertIn(concept3, retrieved_event.concepts)

        # Verify the event is linked back to each original concept instance
        self.assertIn(retrieved_event, hypergraph.get_concept("concept_multi_1").events)
        self.assertIn(retrieved_event, hypergraph.get_concept("concept_multi_2").events)
        self.assertIn(retrieved_event, hypergraph.get_concept("concept_multi_3").events)

    def test_add_event_with_non_existent_concept(self):
        hypergraph = Hypergraph()
        concept1 = Concept(concept_id="exists_1", name="exists", initial_state=1.0)
        non_existent_concept = Concept(concept_id="non_existent_1", name="does not exist", initial_state=2.0)
        hypergraph.add_concept(concept1)

        # Create an event with one existing and one non-existent concept
        event = Event(
            event_id="event_with_missing",
            timestamp=datetime.now(),
            concepts={concept1, non_existent_concept},
            delta=0.2
        )

        # Adding this event should log a warning and only link to the existing concept
        # Use the logger for the module eventual.core.hypergraph
        module_logger = logging.getLogger('eventual.core.hypergraph')
        with self.assertLogs(module_logger, level='WARNING') as log_context:
             hypergraph.add_event(event)

        self.assertEqual(len(hypergraph.events), 1)
        retrieved_event = hypergraph.get_event("event_with_missing")
        self.assertIsNotNone(retrieved_event)

        # Verify the event's concepts set only contains the existing concept instance
        self.assertEqual(len(retrieved_event.concepts), 1)
        self.assertIn(concept1, retrieved_event.concepts)
        self.assertNotIn(non_existent_concept, retrieved_event.concepts)

        # Verify the event is linked back *only* to the existing concept instance
        self.assertIn(retrieved_event, hypergraph.get_concept("exists_1").events)
        # Assert that the non-existent concept was not added to the hypergraph
        self.assertIsNone(hypergraph.get_concept("non_existent_1"))

        # Check for the warning message in the captured logs
        self.assertTrue(any(f"Adding event event_with_missing with concept non_existent_1 not found in hypergraph." in record.getMessage() for record in log_context.records))


    def test_add_event_raises_error_for_duplicate_id(self):
        hypergraph = Hypergraph()
        concept = Concept(concept_id="concept_for_duplicate", name="for duplicate event", initial_state=1.0)
        hypergraph.add_concept(concept)

        event1 = Event(event_id="duplicate_event_id", timestamp=datetime.now(), concepts={concept}, delta=0.1)
        hypergraph.add_event(event1)

        # Attempt to add another event with the same ID
        event2 = Event(event_id="duplicate_event_id", timestamp=datetime.now(), concepts={concept}, delta=0.2)

        with self.assertRaises(ValueError) as context:
            hypergraph.add_event(event2)

        self.assertIn("Event with ID duplicate_event_id already exists.", str(context.exception))
        self.assertEqual(len(hypergraph.events), 1) # Ensure no new event was added


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