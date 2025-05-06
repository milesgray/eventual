from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass
class ExtractedConcept:
    """
    Represents a concept extracted by a processor.
    """
    name: str
    # Optional ID, could be generated later during integration
    concept_id: Optional[str] = field(default=None)
    # any initial properties or state extracted by the processor
    properties: dict[str, any] = field(default_factory=dict)
    initial_state: float = 0.0 # Assuming a default initial state

@dataclass
class ExtractedEvent:
    """
    Represents an event or relationship extracted by a processor.
    Refers to concepts by their names or IDs.
    """
    # Concepts involved in the event. Can use names (strings) initially,
    # which will be resolved to Concept objects during integration.
    concept_identifiers: list[str] # list of concept names or IDs
    timestamp: datetime = field(default_factory=datetime.now)
    # Event-specific data, e.g., state changes, relationship types
    delta: float = 0.0 # Example: change in state for associated concepts
    event_type: Optional[str] = field(default=None) # e.g., 'relationship', 'state_change'
    properties: dict[str, any] = field(default_factory=dict)
    event_id: Optional[str] = field(default=None) # Optional ID, could be generated later

@dataclass
class ProcessorOutput:
    """
    A container for the output of a processor.
    """
    extracted_concepts: list[ExtractedConcept] = field(default_factory=list)
    extracted_events: list[ExtractedEvent] = field(default_factory=list)
