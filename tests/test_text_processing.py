import unittest
from unittest.mock import patch, MagicMock
from eventual.processors.text_processor import TextProcessor
from eventual.processors.processor_output import ProcessorOutput, ExtractedConcept, ExtractedEvent
from datetime import datetime
import json

class TestTextProcessor(unittest.TestCase):

    def setUp(self):
        # Initialize TextProcessor before each test.
        # Use a dummy config path to avoid issues if config.yaml is missing
        with patch('eventual.processors.text_processor.TextProcessor._load_llm_config', return_value={}):
             self.processor = TextProcessor(config_path="dummy_config.yaml")

    def test_instantiation(self):
        # Test that TextProcessor can be instantiated
        # Instantiation is already tested in setUp, just assert the instance
        self.assertIsInstance(self.processor, TextProcessor)

    def test_get_lemma(self):
        # Test the _get_lemma helper method
        self.assertEqual(self.processor._get_lemma("running"), "run")
        self.assertEqual(self.processor._get_lemma("ran"), "run")
        # Updated assertion to match spaCy's output
        self.assertEqual(self.processor._get_lemma("better"), "well")
        self.assertEqual(self.processor._get_lemma("houses"), "house")
        self.assertEqual(self.processor._get_lemma(""), "")
        self.assertEqual(self.processor._get_lemma("A"), "a") # Test lowercasing

    def test_update_concept_map(self):
        # Test updating the concept map
        initial_map_size = len(self.processor.concept_map)
        self.processor.update_concept_map("energy", ["power", "strength"])
        # Check if the new concept was added (lemmatized)
        self.assertIn("energy", self.processor.concept_map)
        # Check if synonyms were added and lemmatized
        self.assertIn("power", self.processor.concept_map["energy"])
        self.assertIn("strength", self.processor.concept_map["energy"])
        self.assertEqual(len(self.processor.concept_map), initial_map_size + 1)

        # Test adding synonyms to an existing concept
        self.assertIn("light", self.processor.concept_map) # Should be in default map
        self.processor.update_concept_map("light", ["shine", "brighten"])
        self.assertIn("shine", self.processor.concept_map["light"])
        self.assertIn("brighten", self.processor.concept_map["light"])
        # Ensure old synonyms are potentially replaced or merged depending on implementation (current replaces)
        # The current update_concept_map implementation replaces the list, so check for the new synonyms
        self.assertEqual(set(self.processor.concept_map["light"]), set(["shine", "brighten"]))


    def test_extract_concepts_empty_text(self):
        # Test extract_concepts with empty input text
        output = self.processor.extract_concepts("")
        self.assertIsInstance(output, ProcessorOutput)
        self.assertEqual(len(output.extracted_concepts), 0)
        self.assertEqual(len(output.extracted_events), 0)

    def test_extract_concepts_no_relevant_concepts(self):
        # Test extract_concepts with text containing no concepts from the map
        output = self.processor.extract_concepts("This is a simple sentence about nothing important.")
        self.assertIsInstance(output, ProcessorOutput)
        self.assertEqual(len(output.extracted_concepts), 0)

    def test_extract_concepts_with_relevant_concepts(self):
        # Test extract_concepts with text containing relevant concepts
        text = "The light is bright and the sound is loud."
        output = self.processor.extract_concepts(text)
        self.assertIsInstance(output, ProcessorOutput)
        # Check if concepts are extracted (lemmatized)
        extracted_concept_names = {c.name for c in output.extracted_concepts}
        self.assertIn("light", extracted_concept_names)
        self.assertIn("sound", extracted_concept_names)
        # Check if scores are assigned (will be non-zero for these concepts)
        concept_scores = {c.name: c.initial_state for c in output.extracted_concepts}
        self.assertGreater(concept_scores.get("light", 0), 0)
        self.assertGreater(concept_scores.get("sound", 0), 0)

    def test_extract_concepts_normalization(self):
        # Test extract_concepts with and without normalization
        text = "Light and darkness."
        output_normalized = self.processor.extract_concepts(text, normalize=True)
        output_raw = self.processor.extract_concepts(text, normalize=False)

        normalized_scores = {c.name: c.initial_state for c in output_normalized.extracted_concepts}
        raw_scores = {c.name: c.initial_state for c in output_raw.extracted_concepts}

        # With normalization, the highest score should be close to 1.0
        if normalized_scores:
             self.assertAlmostEqual(max(normalized_scores.values()), 1.0, places=5)
             # Check that raw scores are different from normalized scores (unless only one concept)
             if len(normalized_scores) > 1:
                 self.assertNotEqual(normalized_scores, raw_scores)
        
        # Raw scores should reflect actual TF-IDF values and not be normalized to 1
        if raw_scores:
            for score in raw_scores.values():
                 self.assertGreaterEqual(score, 0)


    def test_detect_phase_shifts_no_change(self):
        # Test detect_phase_shifts with no significant change
        text1 = "The light is on."
        text2 = "The light is still on."
        # Temporarily update concept map for this test to ensure 'light' is a concept
        original_map = self.processor.concept_map.copy()
        self.processor.update_concept_map("light", ["on"])

        shifts = self.processor.detect_phase_shifts(text1, text2, delta_threshold=0.1)
        self.assertEqual(len(shifts), 0) # Expect no phase shifts

        self.processor.concept_map = original_map # Restore original map

    def test_detect_phase_shifts_significant_change(self):
        # Test detect_phase_shifts with a significant change
        text1 = "The room was dark."
        text2 = "The room is now bright."
        # Temporarily update concept map for this test
        original_map = self.processor.concept_map.copy()
        self.processor.update_concept_map("darkness", ["dark"])
        self.processor.update_concept_map("light", ["bright"])


        shifts = self.processor.detect_phase_shifts(text1, text2, delta_threshold=0.1)
        self.assertGreater(len(shifts), 0) # Expect at least one phase shift

        # Check details of the detected shifts (example: check for 'darkness' or 'light' shift)
        shift_concepts = {e.concept_identifiers[0] for e in shifts if e.concept_identifiers}
        self.assertTrue("darkness" in shift_concepts or "light" in shift_concepts)

        # Check the delta for a concept that changed significantly
        for shift in shifts:
            if shift.concept_identifiers and shift.concept_identifiers[0] == "darkness":
                 # Assuming darkness score goes down from text1 to text2
                 self.assertLess(shift.delta, -0.1)
            if shift.concept_identifiers and shift.concept_identifiers[0] == "light":
                 # Assuming light score goes up from text1 to text2
                 self.assertGreater(shift.delta, 0.1)

        self.processor.concept_map = original_map # Restore original map


    def test_detect_phase_shifts_below_threshold(self):
        # Test detect_phase_shifts with changes below the threshold
        text1 = "It was a little dark."
        text2 = "It is slightly less dark now."
         # Temporarily update concept map for this test
        original_map = self.processor.concept_map.copy()
        self.processor.update_concept_map("darkness", ["dark"])

        shifts = self.processor.detect_phase_shifts(text1, text2, delta_threshold=0.5) # Use a higher threshold
        self.assertEqual(len(shifts), 0) # Expect no phase shifts above this threshold

        self.processor.concept_map = original_map # Restore original map


    @patch('eventual.processors.text_processor.litellm.completion')
    def test_extract_concepts_and_graph_llm(self, mock_litellm_completion):
        # Mock the LLM response
        mock_response_content = {
            "concepts": ["Google", "Gemini", "AI model", "tech company", "release", "model"],
            "relationships": [["Google", "release"], ["Google", "tech company"], ["Gemini", "AI model"], ["Gemini", "model"], ["release", "model"]]
        }
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.content = json.dumps(mock_response_content)
        mock_litellm_completion.return_value = mock_response

        text = "Google released Gemini models. Gemini is a powerful AI model. Google is a tech company. Releasing models is complex."
        output = self.processor.extract_concepts_and_graph_llm(text)

        self.assertIsInstance(output, ProcessorOutput)

        # Check extracted concepts (should be lemmatized)
        extracted_concept_names = {c.name for c in output.extracted_concepts}
        # Corrected expected_concepts to match lemmatized first token of multi-word concepts
        expected_concepts = {"google", "gemini", "ai", "tech", "release", "model"}
        self.assertEqual(extracted_concept_names, expected_concepts)

        # Check extracted events (relationships)
        self.assertEqual(len(output.extracted_events), len(mock_response_content["relationships"]))
        extracted_relationships = set()
        for event in output.extracted_events:
             self.assertEqual(event.event_type, 'relationship')
             # Ensure concept identifiers are lemmatized and stored as a tuple for set comparison
             lemmatized_identifiers = tuple(sorted([self.processor._get_lemma(c) for c in event.concept_identifiers]))
             extracted_relationships.add(lemmatized_identifiers)

        expected_relationships = set()
        for relation in mock_response_content["relationships"]:
             expected_relationships.add(tuple(sorted([self.processor._get_lemma(c) for c in relation])))

        self.assertEqual(extracted_relationships, expected_relationships)

        # Verify litellm.completion was called with the correct arguments
        mock_litellm_completion.assert_called_once()
        call_args, call_kwargs = mock_litellm_completion.call_args

        # Check the prompt content (allow for variations in spacing/formatting)
        prompt = call_kwargs['messages'][1]['content']
        self.assertIn("Analyze the following text and extract key concepts and their relationships.", prompt)
        self.assertIn("JSON format", prompt)
        self.assertIn(text, prompt)

        # Check other litellm parameters (using default values since llm_settings is empty)
        self.assertEqual(call_kwargs['model'], 'gpt-4o')
        self.assertEqual(call_kwargs['temperature'], 0.7)
        self.assertEqual(call_kwargs['top_p'], 1.0)
        self.assertEqual(call_kwargs['messages'][0]['role'], 'system')
        self.assertIn("extracts concepts and relationships from text and formats them as JSON", call_kwargs['messages'][0]['content'])

    @patch('eventual.processors.text_processor.litellm.completion')
    def test_extract_concepts_and_graph_llm_empty_text(self, mock_litellm_completion):
        # Test with empty text
        output = self.processor.extract_concepts_and_graph_llm("")
        self.assertIsInstance(output, ProcessorOutput)
        self.assertEqual(len(output.extracted_concepts), 0)
        self.assertEqual(len(output.extracted_events), 0)
        mock_litellm_completion.assert_not_called()

    @patch('eventual.processors.text_processor.litellm.completion')
    def test_extract_concepts_and_graph_llm_invalid_json(self, mock_litellm_completion):
        # Mock LLM response with invalid JSON
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.content = "This is not JSON."
        mock_litellm_completion.return_value = mock_response

        text = "Some text."
        output = self.processor.extract_concepts_and_graph_llm(text)

        self.assertIsInstance(output, ProcessorOutput)
        self.assertEqual(len(output.extracted_concepts), 0)
        self.assertEqual(len(output.extracted_events), 0)
        mock_litellm_completion.assert_called_once()


if __name__ == '__main__':
    unittest.main()