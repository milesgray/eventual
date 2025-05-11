import pytest
from typing import Optional
from unittest.mock import MagicMock
from eventual.utils.text_processor import TextProcessor
from eventual.core.hypergraph import Hypergraph
from eventual.core.concept import Concept
from eventual.core.event import Event
import json
import os

# Mock the litellm.completion call for testing LLM functionality
@pytest.fixture
def mock_litellm_completion(mocker):
    """Fixture to mock litellm.completion."""
    mock_response = MagicMock()
    # Configure the mock response to return a predictable structure
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    # Default content for LLM response - LLM might return phrases, our code lemmatizes them.
    mock_response.choices[0].message.content = json.dumps({
        "concepts": ["concept a", "concept b", "concept c", "google", "gemini", "AI model", "tech company", "release models"], # "AI model" becomes "ai", "release models" becomes "release"
        "relationships": [
            ["concept a", "concept b"],
            ["concept b", "concept c"],
            ["google", "gemini"],
            ["gemini", "AI model"],
            ["google", "tech company"],
            ["google", "release models"]
        ]
    })
    return mocker.patch("eventual.utils.text_processor.litellm.completion", return_value=mock_response)

# Fixture for a TextProcessor instance with default settings
@pytest.fixture
def text_processor():
    """Fixture for a TextProcessor instance."""
    # Create a dummy config file for testing loading
    dummy_config_path = "test_config.yaml"
    with open(dummy_config_path, "w") as f:
        f.write("""llm_settings:
  model: "mock-model"
  temperature: 0.5
""")
    processor = TextProcessor(config_path=dummy_config_path)
    yield processor
    # Clean up the dummy config file
    os.remove(dummy_config_path)

# Helper to find a concept by its name (lemma) in a list of ExtractedConcept objects
def find_extracted_concept_by_name(concepts: list, name: str) -> Optional: # Use Optional to handle not found
    for concept in concepts:
        # Assuming name attribute in ExtractedConcept stores the lemma
        if concept.name.lower() == name.lower():
            return concept
    return None

# Helper to check if an extracted event exists between a set of concept identifiers
def extracted_event_exists_between_identifiers(events: list, identifiers: set[str]) -> bool:
    for event in events:
        # Ensure concept_identifiers is treated as a set for comparison
        event_identifiers = set(ci.lower() for ci in event.concept_identifiers) # Ensure comparison is case-insensitive
        if event_identifiers == {i.lower() for i in identifiers}: # Ensure comparison is case-insensitive
            return True
    return False


def test_extract_concepts(text_processor):
    # Use text with different forms of words in the concept map
    text = "The lights were too bright, and the sounds are overwhelming."
    processor_output = text_processor.extract_concepts(text)
    concepts = {c.name: c.initial_state for c in processor_output.extracted_concepts}
    # Check for concepts by their lemmas
    assert "light" in concepts
    assert "sound" in concepts
    # Check if scores are within the normalized range [0, 1]
    assert 0 <= concepts["light"] <= 1
    assert 0 <= concepts["sound"] <= 1

def test_extract_concepts_adds_to_hypergraph(text_processor):
    """Test that extract_concepts returns ExtractedConcept objects with correct data."""
    # Use text with different forms of words in the concept map
    text = "The lights were bright. The sounds are loud."
    
    # Use extract_concepts - it now returns ProcessorOutput, not modifies hypergraph
    processor_output = text_processor.extract_concepts(text)
    extracted_concepts = processor_output.extracted_concepts

    # Check if ExtractedConcept objects for expected lemmas are present
    light_concept_data = find_extracted_concept_by_name(extracted_concepts, "light")
    sound_concept_data = find_extracted_concept_by_name(extracted_concepts, "sound")
    
    assert light_concept_data is not None
    assert sound_concept_data is not None

    # Check if concepts have a non-zero initial state (from TF-IDF score) if text is not empty
    # Scores will be normalized if normalize=True (default)
    assert 0 <= light_concept_data.initial_state <= 1
    assert 0 <= sound_concept_data.initial_state <= 1


def test_extract_concepts_and_graph_llm_populates_hypergraph(text_processor, mock_litellm_completion):
    """Test that extract_concepts_and_graph_llm returns ProcessorOutput with concepts and events."""
    text = "Google released Gemini models. Gemini is a powerful AI model. Google is a tech company. Releasing models is complex."

    # Call the LLM-based method - it now returns ProcessorOutput
    processor_output = text_processor.extract_concepts_and_graph_llm(text)
    extracted_concepts = processor_output.extracted_concepts
    extracted_events = processor_output.extracted_events

    # Check if concepts (lemmas) from the mocked LLM response were extracted
    # The _get_lemma method lemmatizes multi-word phrases to the lemma of the first word.
    expected_lemmas = {"concept", "google", "gemini", "ai", "tech", "release"}
    extracted_lemmas = {c.name.lower() for c in extracted_concepts}
    for lemma in expected_lemmas:
        assert lemma in extracted_lemmas, f"Expected lemma '{lemma}' not found in extracted concepts: {extracted_lemmas}"

    # Check if events (relationships) from the mocked LLM response were extracted
    # We check if events involving the correct concept identifiers (lemmatized) exist

    # ("concept a", "concept b") -> ("concept", "concept") -> {"concept"}
    assert extracted_event_exists_between_identifiers(extracted_events, {"concept"}), "Relationship between 'concept a' and 'concept b' (lemmatized to 'concept') not found or incorrect."
    # ("concept b", "concept c") -> ("concept", "concept") -> {"concept"}
    # This test is redundant if the above passes and there's only one such relationship type.
    # If specific pairs matter beyond just {"concept"}, then the mock or logic needs adjustment.

    assert extracted_event_exists_between_identifiers(extracted_events, {"google", "gemini"})
    assert extracted_event_exists_between_identifiers(extracted_events, {"gemini", "ai"}) # "AI model" -> "ai"
    assert extracted_event_exists_between_identifiers(extracted_events, {"google", "tech"}) # "tech company" -> "tech"
    assert extracted_event_exists_between_identifiers(extracted_events, {"google", "release"}) # "release models" -> "release"

    # Check event metadata and delta for LLM events
    for event in extracted_events:
        assert event.event_type == 'relationship'
        assert event.delta == 0.0 # LLM relationship events have delta 0
        assert "source" in event.properties
        assert event.properties.get("source") == "LLM_concept_extraction"
        assert "relationship_type" in event.properties # Could be more specific if LLM provides it


def test_detect_phase_shifts(text_processor):
    text1 = "The room was dark and quiet."
    text2 = "The room is now light and noisy."
    phase_shift_events = text_processor.detect_phase_shifts(text1, text2)
    
    # Check if ExtractedEvent objects for expected concept lemmas are present in the list
    # Safely access the first element and handle potential None or empty list
    shifted_concept_identifiers = {e.concept_identifiers[0].lower() for e in phase_shift_events if e.concept_identifiers and len(e.concept_identifiers) > 0}

    assert "light" in shifted_concept_identifiers
    assert "darkness" in shifted_concept_identifiers
    assert "sound" in shifted_concept_identifiers
    assert "silence" in shifted_concept_identifiers

    # Check that the delta values are present and have the correct sign (simplified check)
    # This assumes one event per concept in phase_shift_events
    deltas = {e.concept_identifiers[0].lower(): e.delta for e in phase_shift_events if e.concept_identifiers and len(e.concept_identifiers) > 0}
    assert deltas.get("light", 0) > 0
    assert deltas.get("sound", 0) > 0
    assert deltas.get("darkness", 0) < 0
    assert deltas.get("silence", 0) < 0

def test_detect_phase_shifts_adds_events_to_hypergraph(text_processor):
    """Test that detect_phase_shifts returns ExtractedEvent objects with correct data."""
    text1 = "The room was dark and quiet."
    text2 = "The room is now light and noisy."
    delta_threshold = 0.1

    # Call detect_phase_shifts - it now returns a list of ExtractedEvent objects
    phase_shift_events = text_processor.detect_phase_shifts(text1, text2, delta_threshold=delta_threshold)

    # Check if ExtractedEvent objects for expected concept lemmas are present
    # Safely access the first element and handle potential None or empty list
    shifted_concept_identifiers = {e.concept_identifiers[0].lower() for e in phase_shift_events if e.concept_identifiers and len(e.concept_identifiers) > 0}

    assert "light" in shifted_concept_identifiers
    assert "darkness" in shifted_concept_identifiers
    assert "sound" in shifted_concept_identifiers
    assert "silence" in shifted_concept_identifiers

    # Check properties and delta for the extracted phase shift events
    for event in phase_shift_events:
        assert event.event_type == 'phase_shift'
        assert event.delta != 0.0
        assert "source" in event.properties
        assert event.properties.get("source") == "TFIDF_phase_shift_detection"
        assert "delta_magnitude" in event.properties
        assert "text1_score" in event.properties
        assert "text2_score" in event.properties
        assert len(event.concept_identifiers) == 1
        # Safely access concept_lemma property and compare
        concept_lemma_from_properties = event.properties.get("concept_lemma")
        assert concept_lemma_from_properties is not None, "concept_lemma property missing in phase shift event."
        assert concept_lemma_from_properties.lower() == event.concept_identifiers[0].lower()

def test_update_concept_map(text_processor):
    processor = TextProcessor()
    processor.update_concept_map("temperatures", ["heated", "chilling"])
    assert "temperature" in processor.concept_map
    assert "heat" in processor.concept_map["temperature"]
    assert "chill" in processor.concept_map["temperature"]
    assert "temperatures" not in processor.concept_map # Ensure the original key is not there if it was different from lemma
    # Check that lemmatized synonyms are in the map, not the originals
    assert "heated" not in processor.concept_map["temperature"] # Original synonym should not be key
    assert "chilling" not in processor.concept_map["temperature"] # Original synonym should not be key

