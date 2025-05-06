import unittest
from eventual.processors.text_processor import TextProcessor
from eventual.processors.processor_output import ProcessorOutput, ExtractedConcept

class TestTextProcessing(unittest.TestCase):

    def test_extract_concepts(self):
        processor = TextProcessor()
        text = "The light is bright."
        output = processor.extract_concepts(text)
        self.assertIsInstance(output, ProcessorOutput)
        # Check that at least one ExtractedConcept is present, 
        # and that at least one of them has name 'light'
        self.assertTrue(len(output.extracted_concepts) > 0)
        self.assertTrue(any(c.name == "light" for c in output.extracted_concepts))

    def test_extract_concepts_empty_text(self):
        processor = TextProcessor()
        text = ""
        output = processor.extract_concepts(text)
        self.assertIsInstance(output, ProcessorOutput)
        self.assertEqual(len(output.extracted_concepts), 0)

    def test_extract_concepts_and_graph_llm(self):
        processor = TextProcessor()
        text = "Google released Gemini models. Gemini is a powerful AI model."
        try:
            output = processor.extract_concepts_and_graph_llm(text)
            self.assertIsInstance(output, ProcessorOutput)
            # Basic check - LLM test depends on external factors, so a full assert isn't reliable
            self.assertTrue(len(output.extracted_concepts) > 0 or len(output.extracted_events) > 0)
        except Exception as e:
            self.fail(f"LLM processing failed: {e}. Ensure LLM is configured correctly.")


if __name__ == '__main__':
    unittest.main()
