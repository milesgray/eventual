import pytest
from eventual.core import Concept, TemporalBoundary, TemporalBoundaryConfig, Event

def test_static_threshold():
    config = TemporalBoundaryConfig(threshold=0.1, dynamic_threshold=False)
    detector = TemporalBoundary(config)
    concept = Concept(concept_id="light_1", name="light", initial_state=1.0)

    # No event for small change
    event = detector.detect_event(concept, 0.95)
    assert event is None

    # Event for significant change
    event = detector.detect_event(concept, 0.8)
    assert event is not None
    assert event.delta == 0.19999999999999996

def test_dynamic_threshold():
    config = TemporalBoundaryConfig(threshold=0.1, dynamic_threshold=True)
    detector = TemporalBoundary(config)
    concept = Concept(concept_id="light_1", name="light", initial_state=1.0)

    # First significant change
    event = detector.detect_event(concept, 0.8)
    assert event is not None

    # Second change with adjusted threshold
    event = detector.detect_event(concept, 0.6)
    assert event is not None

def test_exponential_decay():
    config = TemporalBoundaryConfig(threshold=0.1, decay_factor=0.5, dynamic_threshold=True)
    detector = TemporalBoundary(config)
    concept = Concept(concept_id="light_1", name="light", initial_state=1.0)

    # Simulate a series of changes
    detector.detect_event(concept, 0.8)  # Delta = 0.2
    detector.detect_event(concept, 0.6)  # Delta = 0.2
    detector.detect_event(concept, 0.4)  # Delta = 0.2

    # Check that the threshold has increased
    event = detector.detect_event(concept, 0.3)
    assert event is not None