"""
# Hypergraph Module

The `hypergraph` module is the core of the `Eventual` framework. It provides classes for managing concepts, events, and their relationships in a hypergraph structure.

## Classes

### `Concept`
Represents a concept in the hypergraph. A concept is a node with a unique identifier, a name, and a numerical state.

### `Event`
Represents an event in the hypergraph. An event is a hyperedge that connects one or more concepts and captures a change in their states.

### `Hypergraph`
Manages all concepts and events in the hypergraph. It supports adding concepts, creating events, and querying relationships between concepts and events.

## Example Usage

```python
from eventual.core import Hypergraph, Concept, Event
from datetime import datetime

# Initialize a hypergraph
hypergraph = Hypergraph()

# Create and add concepts
light_concept = Concept(concept_id="light_1", name="light", initial_state=1.0)
hypergraph.add_concept(light_concept)

# Create and add an event
event = Event(
    event_id="event_1",
    timestamp=datetime.now(),
    concepts={light_concept},
    delta=0.5
)
hypergraph.add_event(event)
```
"""
from typing import Optional
from eventual.core.event import Event
from eventual.core.concept import Concept

class Hypergraph:
    """
    Represents a hypergraph that stores concepts and events. The hypergraph is the core data structure
    for modeling memory in an LLM-based agent. It supports adding concepts, creating events, and querying
    relationships between concepts and events.

    Attributes:
        concepts (dict[str, Concept]): A dictionary of concepts, keyed by concept ID.
        events (dict[str, Event]): A dictionary of events, keyed by event ID.
    """

    def __init__(self):
        """
        Initialize an empty Hypergraph.
        """
        self.concepts: dict[str, Concept] = {}
        self.events: dict[str, Event] = {}

    def add_concept(self, concept: Concept):
        """
        Add a concept to the hypergraph.

        Args:
            concept (Concept): The concept to add.
        """
        if concept.concept_id in self.concepts:
            raise ValueError(f"Concept with ID {concept.concept_id} already exists.")
        self.concepts[concept.concept_id] = concept

    def get_concept(self, concept_id: str) -> Optional[Concept]:
        """
        Retrieve a concept by its ID.

        Args:
            concept_id (str): The ID of the concept to retrieve.

        Returns:
            Optional[Concept]: The concept, or None if not found.
        """
        return self.concepts.get(concept_id)

    def add_event(self, event: Event):
        """
        Add an event to the hypergraph.

        Args:
            event (Event): The event to add.
        """
        if event.event_id in self.events:
            raise ValueError(f"Event with ID {event.event_id} already exists.")
        self.events[event.event_id] = event
        for concept in event.concepts:
            concept.events.add(event)

    def get_event(self, event_id: str) -> Optional[Event]:
        """
        Retrieve an event by its ID.

        Args:
            event_id (str): The ID of the event to retrieve.

        Returns:
            Optional[Event]: The event, or None if not found.
        """
        return self.events.get(event_id)

    def get_events_by_concept(self, concept_id: str) -> list[Event]:
        """
        Retrieve all events associated with a concept.

        Args:
            concept_id (str): The ID of the concept.

        Returns:
            list[Event]: A list of events involving the concept.
        """
        concept = self.get_concept(concept_id)
        if not concept:
            return []
        return list(concept.events)

    def find_related_concepts(self, concept_id: str) -> set[Concept]:
        """
        Find all concepts related to a given concept through shared events.

        Args:
            concept_id (str): The ID of the concept.

        Returns:
            set[Concept]: A set of related concepts.
        """
        concept = self.get_concept(concept_id)
        if not concept:
            return set()

        related_concepts = set()
        for event in concept.events:
            related_concepts.update(event.concepts)
        related_concepts.discard(concept)  # Remove the original concept
        return related_concepts

    def get_events_by_concept_set(self, concept_ids: set[str]) -> list[Event]:
        """
        Retrieve all events that involve exactly the specified set of concepts.

        Args:
            concept_ids (set[str]): The set of concept IDs.

        Returns:
            list[Event]: A list of events involving exactly the specified concepts.
        """
        matching_events = []
        for event in self.events.values():
            event_concept_ids = {concept.concept_id for concept in event.concepts}
            if event_concept_ids == concept_ids:
                matching_events.append(event)
        return matching_events

    def __repr__(self):
        return f"Hypergraph(concepts={len(self.concepts)}, events={len(self.events)})"