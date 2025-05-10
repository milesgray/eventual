import unittest
from eventual.core.hypergraph import Hypergraph
from eventual.ingestors.hypergraph_integrator import HypergraphIntegrator
from eventual.processors.processor_output import ProcessorOutput, ExtractedConcept, ExtractedEvent
from datetime import datetime

class TestHypergraphIntegration(unittest.TestCase):

    def test_integrate_concepts(self):
        hypergraph = Hypergraph()
        integrator = HypergraphIntegrator()

        # Create some ExtractedConcept objects
        concept1 = ExtractedConcept(name="light", initial_state=0.8)
        concept2 = ExtractedConcept(name="sound", initial_state=0.5)
        processor_output = ProcessorOutput(extracted_concepts=[concept1, concept2])

        integrator.integrate(processor_output, hypergraph)

        self.assertEqual(len(hypergraph.concepts), 2)
        self.assertTrue(hypergraph.get_concept_by_name("light") is not None)
        self.assertTrue(hypergraph.get_concept_by_name("sound") is not None)
        self.assertEqual(hypergraph.get_concept_by_name("light").state, 0.8)
        self.assertEqual(hypergraph.get_concept_by_name("sound").state, 0.5)

    def test_integrate_events(self):
        hypergraph = Hypergraph()
        integrator = HypergraphIntegrator()

        # First, add some concepts to the hypergraph
        concept1 = ExtractedConcept(name="light", initial_state=0.8)
        concept2 = ExtractedConcept(name="sound", initial_state=0.5)
        processor_output_concepts = ProcessorOutput(extracted_concepts=[concept1, concept2])
        integrator.integrate(processor_output_concepts, hypergraph)

        # Create some ExtractedEvent objects
        event1 = ExtractedEvent(concept_identifiers=["light", "sound"], timestamp=datetime.now(), delta=0.2)
        processor_output_events = ProcessorOutput(extracted_events=[event1])

        integrator.integrate(processor_output_events, hypergraph)

        self.assertEqual(len(hypergraph.events), 1)
        event = next(iter(hypergraph.events.values()))  # Get the first event
        self.assertEqual(len(event.concepts), 2)
        # self.assertTrue(any(c.name == "light" for c in event.concepts))
        # self.assertTrue(any(c.name == "sound" for c in event.concepts))

    def test_integrate_duplicate_concepts(self):
        hypergraph = Hypergraph()
        integrator = HypergraphIntegrator()

        # Create some ExtractedConcept objects, including a duplicate
        concept1 = ExtractedConcept(name="light", initial_state=0.8)
        concept2 = ExtractedConcept(name="light", initial_state=0.9)  # Duplicate name
        processor_output = ProcessorOutput(extracted_concepts=[concept1, concept2])

        integrator.integrate(processor_output, hypergraph)

        # Should only have one concept with the name "light"
        self.assertEqual(len(hypergraph.concepts), 1) # now enforces unique names so the second one is rejected

if __name__ == '__main__':
    unittest.main()
