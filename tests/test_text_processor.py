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

# Helper to find a concept in the hypergraph by its lemma (name)
def find_concept_by_lemma(hypergraph: Hypergraph, lemma: str) -> Optional[Concept]:
    for concept in hypergraph.concepts.values():
        if concept.name.lower() == lemma.lower(): # Concept names are stored as lemmas
            return concept
    return None

# Helper to check if an event exists between a set of concepts based on their lemmas
def event_exists_between_lemmas(hg: Hypergraph, concept_lemmas: set[str]) -> bool:
    for event in hg.events.values():
        event_concept_lemmas = {c.name.lower() for c in event.concepts}
        if event_concept_lemmas == {cl.lower() for cl in concept_lemmas}: # Compare lowercase lemmas
            return True
    return False

# Helper to check if a phase shift event exists for a specific concept lemma
def phase_shift_event_exists_for_lemma(hg: Hypergraph, concept_lemma: str) -> bool:
     for event in hg.events.values():
          # Check if it's a phase shift event involving one concept with the matching lemma
          if len(event.concepts) == 1 and list(event.concepts)[0].name.lower() == concept_lemma.lower() and event.metadata.get("source") == "TFIDF_phase_shift_detection" and event.delta != 0.0:
               return True
     return False

def test_extract_concepts(text_processor):
    processor = TextProcessor()
    # Use text with different forms of words in the concept map
    text = "The lights were too bright, and the sounds are overwhelming."
    concepts = processor.extract_concepts(text)
    # Check for concepts by their lemmas
    assert "light" in concepts
    assert "sound" in concepts
    # Check if scores are within the normalized range [0, 1]
    assert 0 <= concepts["light"] <= 1
    assert 0 <= concepts["sound"] <= 1

def test_extract_concepts_adds_to_hypergraph(text_processor):
    """Test that extract_concepts adds detected concepts (lemmas) to the hypergraph."""
    hypergraph = Hypergraph()
    # Use text with different forms of words in the concept map
    text = "The lights were bright. The sounds are loud."
    
    # Use extract_concepts and pass the hypergraph
    concepts_scores = text_processor.extract_concepts(text, hypergraph=hypergraph)

    # Check if concepts (lemmas) from the default map are added
    assert find_concept_by_lemma(hypergraph, "light") is not None
    assert find_concept_by_lemma(hypergraph, "sound") is not None

    # Check if concepts have a non-zero initial state (from TF-IDF score) if text is not empty
    light_concept = find_concept_by_lemma(hypergraph, "light")
    sound_concept = find_concept_by_lemma(hypergraph, "sound")
    
    assert light_concept is not None
    assert sound_concept is not None
    # Scores will be normalized if normalize=True (default)
    assert 0 <= light_concept.state <= 1
    assert 0 <= sound_concept.state <= 1

    # Check that the returned dictionary is still correct (using lemmas)
    assert "light" in concepts_scores
    assert "sound" in concepts_scores

def test_extract_concepts_and_graph_llm_populates_hypergraph(text_processor, mock_litellm_completion):
    """Test that extract_concepts_and_graph_llm adds concepts (lemmas) and events to the provided hypergraph."""
    hypergraph = Hypergraph()
    text = "Google released Gemini models. Gemini is a powerful AI model. Google is a tech company. Releasing models is complex."

    # Call the LLM-based method
    text_processor.extract_concepts_and_graph_llm(text, hypergraph)

    # Check if concepts (lemmas) from the mocked LLM response were added
    # "AI model" becomes "ai", "release models" becomes "release"
    expected_lemmas = {"concept a", "concept b", "concept c", "google", "gemini", "ai", "tech company", "release"}
    for lemma in expected_lemmas:
        assert find_concept_by_lemma(hypergraph, lemma) is not None, f"Lemma '{lemma}' not found in hypergraph concepts: {[c.name for c in hypergraph.concepts.values()]}"

    # Check if events (relationships) from the mocked LLM response were added based on lemmas
    concept_a = find_concept_by_lemma(hypergraph, "concept a")
    concept_b = find_concept_by_lemma(hypergraph, "concept b")
    concept_c = find_concept_by_lemma(hypergraph, "concept c")
    google_concept = find_concept_by_lemma(hypergraph, "google")
    gemini_concept = find_concept_by_lemma(hypergraph, "gemini")
    ai_model_concept = find_concept_by_lemma(hypergraph, "ai") # Expecting "ai" as lemma for "AI model"
    tech_company_concept = find_concept_by_lemma(hypergraph, "tech company") # Assuming "tech company" lemmatizes to itself or we handle it
    release_concept = find_concept_by_lemma(hypergraph, "release") # Expecting "release" for "release models"

    assert event_exists_between_lemmas(hypergraph, {"concept a", "concept b"})
    assert event_exists_between_lemmas(hypergraph, {"concept b", "concept c"})
    assert event_exists_between_lemmas(hypergraph, {"google", "gemini"})
    assert event_exists_between_lemmas(hypergraph, {"gemini", "ai"})
    assert event_exists_between_lemmas(hypergraph, {"google", "tech company"})
    assert event_exists_between_lemmas(hypergraph, {"google", "release"})

    # Check event metadata and delta for LLM events
    for event in hypergraph.events.values():
         if event.metadata.get("source") == "LLM_concept_extraction":
              assert event.delta == 0.0 # LLM relationship events have delta 0
              assert "relationship" in event.metadata

def test_detect_phase_shifts(text_processor):
    text1 = "The room was dark and quiet."
    text2 = "The room is now light and noisy."
    phase_shifts = text_processor.detect_phase_shifts(text1, text2)
    
    shifted_concepts_lemmas = {ps[0].lower() for ps in phase_shifts}
    assert "light" in shifted_concepts_lemmas
    assert "darkness" in shifted_concepts_lemmas
    assert "sound" in shifted_concepts_lemmas
    assert "silence" in shifted_concepts_lemmas
    assert all(ps[1] >= 0 for ps in phase_shifts)

def test_detect_phase_shifts_adds_events_to_hypergraph(text_processor):
    hypergraph = Hypergraph()
    text1 = "The room was dark and quiet."
    text2 = "The room is now light and noisy."
    delta_threshold = 0.1

    phase_shifts_data = text_processor.detect_phase_shifts(text1, text2, hypergraph=hypergraph, delta_threshold=delta_threshold)

    shifted_concepts_data = {ps[0].lower(): ps[1] for ps in phase_shifts_data}
    assert "light" in shifted_concepts_data
    assert "darkness" in shifted_concepts_data
    assert "sound" in shifted_concepts_data
    assert "silence" in shifted_concepts_data

    assert shifted_concepts_data.get("light", 0) > 0
    assert shifted_concepts_data.get("sound", 0) > 0
    assert shifted_concepts_data.get("darkness", 0) < 0
    assert shifted_concepts_data.get("silence", 0) < 0

    light_concept = find_concept_by_lemma(hypergraph, "light")
    sound_concept = find_concept_by_lemma(hypergraph, "sound")
    darkness_concept = find_concept_by_lemma(hypergraph, "darkness")
    silence_concept = find_concept_by_lemma(hypergraph, "silence")

    assert light_concept is not None
    assert sound_concept is not None
    assert darkness_concept is not None
    assert silence_concept is not None

    assert phase_shift_event_exists_for_lemma(hypergraph, "light")
    assert phase_shift_event_exists_for_lemma(hypergraph, "sound")
    assert phase_shift_event_exists_for_lemma(hypergraph, "darkness")
    assert phase_shift_event_exists_for_lemma(hypergraph, "silence")

    for event in hypergraph.events.values():
         if event.metadata.get("source") == "TFIDF_phase_shift_detection":
              assert event.delta != 0.0
              assert "concept_lemma" in event.metadata
              assert "delta_magnitude" in event.metadata
              assert "text1_score" in event.metadata
              assert "text2_score" in event.metadata
              assert len(event.concepts) == 1
              assert event.metadata.get("concept_lemma").lower() == list(event.concepts)[0].name.lower()

def test_update_concept_map(text_processor):
    processor = TextProcessor()
    processor.update_concept_map("temperatures", ["heated", "chilling"])
    assert "temperature" in processor.concept_map
    assert "heat" in processor.concept_map["temperature"]
    assert "chill" in processor.concept_map["temperature"]
    assert "temperatures" not in processor.concept_map
    assert "heated" not in processor.concept_map["temperature"]
    assert "chilling" not in processor.concept_map["temperature"]
