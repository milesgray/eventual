import pytest
from eventual.ingestors.chat_ingestor import ChatIngestor
from eventual.processors.text_processor import TextProcessor
from eventual.processors.processor_output import ProcessorOutput, ExtractedConcept, ExtractedEvent

# Fixture for a ChatIngestor instance
@pytest.fixture
def chat_ingestor():
    # ChatIngestor can be initialized without a TextProcessor, it will create a default one
    return ChatIngestor()

def test_chat_ingestor_initialization():
    # Test default initialization
    ingestor = ChatIngestor()
    assert isinstance(ingestor._text_processor, TextProcessor)

    # Test initialization with a provided TextProcessor
    custom_processor = TextProcessor(language_model="en_core_web_sm") # Example custom init
    ingestor_with_custom = ChatIngestor(text_processor=custom_processor)
    assert ingestor_with_custom._text_processor is custom_processor

def test_chat_ingestor_ingest_basic(chat_ingestor):
    message = "This is a test message about light and sound."
    processor_output = chat_ingestor.ingest(message)

    assert isinstance(processor_output, ProcessorOutput)
    # Check for expected concepts (lemmatized)
    extracted_concept_names = {c.name for c in processor_output.extracted_concepts}
    assert "light" in extracted_concept_names
    assert "sound" in extracted_concept_names

    # Check that no events are extracted by default TF-IDF
    assert len(processor_output.extracted_events) == 0

# You might add more tests here later for LLM-based ingestion, 
# different message types, edge cases, etc.
