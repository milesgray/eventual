import pytest
from eventual.utils.text_processor import TextProcessor

def test_extract_concepts():
    processor = TextProcessor()
    text = "The light is too bright, and the sound is overwhelming."
    concepts = processor.extract_concepts(text)
    assert "light" in concepts
    assert "sound" in concepts
    assert 0 <= concepts["light"] <= 1
    assert 0 <= concepts["sound"] <= 1

def test_detect_phase_shifts():
    processor = TextProcessor()
    text1 = "The room is dark and quiet."
    text2 = "The room is now bright and noisy."
    phase_shifts = processor.detect_phase_shifts(text1, text2)
    assert ("light", pytest.approx(0.8, 0.1)) in phase_shifts
    assert ("sound", pytest.approx(0.7, 0.1)) in phase_shifts

def test_update_concept_map():
    processor = TextProcessor()
    processor.update_concept_map("temperature", ["heat", "cold"])
    assert "temperature" in processor.concept_map
    assert "heat" in processor.concept_map["temperature"]