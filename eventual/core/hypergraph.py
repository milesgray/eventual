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
from typing import Optional, List, Set
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
        _concept_names (dict[str, str]): Internal dictionary mapping concept names to concept IDs for efficient lookup.
    """

    def __init__(self):
        """
        Initialize an empty Hypergraph.
        """
        self.concepts: dict[str, Concept] = {}
        self.events: dict[str, Event] = {}
        self._concept_names: dict[str, str] = {}

    def add_concept(self, concept: Concept):
        """
        Add a concept to the hypergraph.

        Args:
            concept (Concept): The concept to add.

        Raises:
            ValueError: If a concept with the same ID or name already exists.
        """
        if concept.concept_id in self.concepts:
            raise ValueError(f"Concept with ID {concept.concept_id} already exists.")
        # Assuming concept names should also be unique. If not, this check should be removed
        if concept.name in self._concept_names:
             raise ValueError(f"Concept with name '{concept.name}' already exists.")

        self.concepts[concept.concept_id] = concept
        self._concept_names[concept.name] = concept.concept_id

    def get_concept(self, concept_id: str) -> Optional[Concept]:
        """
        Retrieve a concept by its ID.

        Args:
            concept_id (str): The ID of the concept to retrieve.

        Returns:
            Optional[Concept]: The concept, or None if not found.
        """
        return self.concepts.get(concept_id)

    def get_concept_by_name(self, name: str) -> Optional[Concept]:
        """
        Retrieve a concept by its name.

        Args:
            name (str): The name of the concept to retrieve.

        Returns:
            Optional[Concept]: The concept, or None if not found.
        """
        concept_id = self._concept_names.get(name)
        if concept_id:
            return self.get_concept(concept_id)
        return None

    def add_concept_if_not_exists(self, concept: Concept) -> Concept:
        """
        Adds a concept if it doesn't exist (based on ID or name).
        Returns the existing concept if found, otherwise returns the newly added concept.

        Args:
            concept (Concept): The concept to add.

        Returns:
            Concept: The existing or newly added concept.
        """
        # Check by ID first (primary key)
        existing_concept_by_id = self.get_concept(concept.concept_id)
        if existing_concept_by_id:
            return existing_concept_by_id

        # Then check by name
        existing_concept_by_name = self.get_concept_by_name(concept.name)
        if existing_concept_by_name:
            # Assuming name uniqueness is enforced by add_concept
            # If we reach here, it means the ID was different but the name is the same.
            # Based on the current add_concept, this scenario implies a ValueError would have been raised if add_concept were called directly.
            # For add_concept_if_not_exists, we should probably return the existing one by name.
            return existing_concept_by_name

        # If neither exists, add the new concept
        self.add_concept(concept)
        return concept


    def add_event(self, event: Event):
        """
        Add an event to the hypergraph.

        Args:
            event (Event): The event to add.

        Raises:
            ValueError: If an event with the same ID already exists.
        """
        if event.event_id in self.events:
            raise ValueError(f"Event with ID {event.event_id} already exists.")
        self.events[event.event_id] = event
        for concept in event.concepts:
            # Ensure the concept is in the hypergraph before linking the event
            # Use get_concept to retrieve the instance stored in the hypergraph
            stored_concept = self.get_concept(concept.concept_id)
            if stored_concept:
                 stored_concept.events.add(event) # Link event to concept within the hypergraph's stored concepts
            else:
                 # This indicates an event is being added with a concept not present in the hypergraph.
                 # Depending on desired behavior, this might be an error or a warning.
                 # Current add_concept requires concepts to be added first.
                 print(f"Warning: Adding event {event.event_id} with concept {concept.concept_id} not found in hypergraph. Event not linked to this concept.")


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
        # Return a list from the set of events for consistency with type hint
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
        # Access events from the concept object retrieved from self.concepts
        # Ensure the concept object is retrieved from the hypergraph's internal store
        stored_concept = self.get_concept(concept_id)
        if stored_concept:
            for event in stored_concept.events:
                related_concepts.update(event.concepts)
            related_concepts.discard(stored_concept)  # Remove the original concept

        return related_concepts

    def get_events_by_concept_set(self, concept_ids: set[str]) -> list[Event]:
        """
        Retrieve all events that involve exactly the specified set of concepts.

        Args:
            concept_ids (set[str]): The set of concept IDs.

        Returns:
            list[Event]: A list of events involving exactly the specified concepts.
        """
        # Efficiently check if all concept_ids exist in the hypergraph
        if not all(cid in self.concepts for cid in concept_ids):
            # If any concept ID in the input set is not in the hypergraph, no event can match this set
            return []

        matching_events = []
        # Retrieve concept objects for the given IDs once from the hypergraph's store
        target_concepts = {self.concepts[cid] for cid in concept_ids}

        for event in self.events.values():
            # Compare the set of concept objects in the event to the target set
            if event.concepts == target_concepts:
                matching_events.append(event)
        return matching_events

    def __repr__(self):
        return f"Hypergraph(concepts={len(self.concepts)}, events={len(self.events)})"
