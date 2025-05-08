"""
# Hypergraph Module

The `hypergraph` module is the core of the `Eventual` framework. It provides classes for managing concepts, events, and their relationships in a hypergraph structure.

## Classes

### `Concept`
Represents a concept in the hypergraph. A concept is a node with a unique identifier, a name, and a numerical state.

### `Event`
Represents an event in the hypergraph. An event is a hyperedge that connects one or more concepts and captures a change in their states.

### `Hypergraph`
Manages all concepts and events in the hypergraph. It supports adding concepts, creating events, and querying relationships between concepts and concepts.

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
import json
from typing import Optional, List, Set, Tuple, Dict, Any
from eventual.core.event import Event
from eventual.core.concept import Concept
from datetime import datetime, timedelta
import spacy # Import spacy for query processing

class Hypergraph:
    """
    Represents a hypergraph that stores concepts and events. The hypergraph is the core data structure
    for modeling memory in an LLM-based agent. It supports adding concepts, creating events, and querying
    relationships between concepts and concepts.

    Attributes:
        concepts (dict[str, Concept]): A dictionary of concepts, keyed by concept ID.
        events (dict[str, Event]): A dictionary of events, keyed by event ID.
        _concept_names (dict[str, str]): Internal dictionary mapping concept names to concept IDs for efficient lookup.
        _nlp (spacy.Language): spaCy language model for query processing.
    """

    def __init__(self):
        """
        Initialize an empty Hypergraph.
        """
        self.concepts: dict[str, Concept] = {}
        self.events: dict[str, Event] = {}
        self._concept_names: dict[str, str] = {}
        try:
            self._nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Downloading spaCy model 'en_core_web_sm'...")
            from spacy.cli import download
            download("en_core_web_sm")
            self._nlp = spacy.load("en_core_web_sm")


    def _get_lemma(self, text: str) -> str:
        """
        Gets the root form (lemma) of a single word or short phrase using spaCy.

        Args:
            text: The input text.

        Returns:
            The lemma of the text.
        """
        if not text:
            return ""
        doc = self._nlp(text)
        if doc and doc[0]:
            return doc[0].lemma_.lower()
        return text.lower() # Fallback to lower case if lemmatization fails

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

    def search_concepts_by_name(self, keyword: str) -> List[Concept]:
        """
        Search for concepts whose name (lemma) contains the given keyword (case-insensitive).

        Args:
            keyword (str): The keyword to search for within concept names.

        Returns:
            List[Concept]: A list of concepts whose names contain the keyword.
        """
        keyword_lower = keyword.lower()
        matching_concepts = []
        for concept in self.concepts.values():
            if keyword_lower in concept.name.lower():
                matching_concepts.append(concept)
        return matching_concepts

    def get_recent_events(self, time_window: timedelta) -> List[Event]:
        """
        Retrieve events that occurred within the specified time window before the current time.

        Args:
            time_window (timedelta): The time window (e.g., timedelta(hours=1), timedelta(days=7)).

        Returns:
            List[Event]: A list of events within the time window, ordered by timestamp (most recent first).
        """
        now = datetime.now()
        recent_events = []
        for event in self.events.values():
            if now - event.timestamp <= time_window:
                recent_events.append(event)
        # Sort by timestamp in descending order (most recent first)
        recent_events.sort(key=lambda event: event.timestamp, reverse=True)
        return recent_events

    def retrieve_knowledge(self, query: str) -> Tuple[List[Concept], List[Event]]:
        """
        Retrieve relevant concepts and events based on a query string.

        Args:
            query (str): The query string.

        Returns:
            Tuple[List[Concept], List[Event]]: A tuple containing a list of relevant concepts
                                              and a list of relevant events.
        """
        # 1. Tokenize and lemmatize the query string.
        doc = self._nlp(query)
        query_lemmas = {token.lemma_.lower() for token in doc if not token.is_stop and token.is_alpha}

        # 2. Find concepts in the hypergraph whose names (lemmas) match the lemmatized terms from the query.
        relevant_concepts: Set[Concept] = set()
        for concept in self.concepts.values():
            if concept.name.lower() in query_lemmas:
                relevant_concepts.add(concept)

        # 3. Collect all events that involve these matched concepts.
        relevant_events: Set[Event] = set()
        for concept in relevant_concepts:
            # Access events directly from the concept object in the hypergraph
            stored_concept = self.get_concept(concept.concept_id)
            if stored_concept:
                relevant_events.update(stored_concept.events)

        # 4. Return the set of relevant concepts and events.
        return list(relevant_concepts), list(relevant_events)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Hypergraph object to a dictionary for serialization.
        """
        return {
            "concepts": {concept_id: concept.to_dict() for concept_id, concept in self.concepts.items()},
            "events": {event_id: event.to_dict() for event_id, event in self.events.items()},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Hypergraph":
        """
        Create a Hypergraph object from a dictionary.
        """
        hypergraph = cls()

        # Load concepts first
        concepts_data = data.get("concepts", {})
        for concept_id, concept_data in concepts_data.items():
            concept = Concept.from_dict(concept_data)
            hypergraph.concepts[concept_id] = concept
            hypergraph._concept_names[concept.name] = concept_id

        # Load events and link them to concepts
        events_data = data.get("events", {})
        for event_id, event_data in events_data.items():
            # Retrieve concept objects from the hypergraph based on event_data's concept_ids
            event_concepts: Set[Concept] = set()
            for concept_id in event_data.get("concept_ids", []):
                concept = hypergraph.get_concept(concept_id)
                if concept:
                    event_concepts.add(concept)
                else:
                    # This indicates an issue with the saved data - a concept ID in an event
                    # doesn't correspond to a concept in the saved concepts list.
                    print(f"Warning: Concept ID {concept_id} for event {event_id} not found during loading. Event may be incomplete.")

            # Only create the event if its concepts can be retrieved (at least partially)
            if event_concepts or not event_data.get("concept_ids"):
                 event = Event.from_dict(event_data, concepts=event_concepts) # Pass the set of concepts
                 hypergraph.events[event_id] = event
                 # Link the event back to the concepts
                 for concept in event_concepts:
                      concept.events.add(event)
            else:
                print(f"Warning: Skipping event {event_id} during loading due to no concepts found.")

        return hypergraph


    def __repr__(self):
        return f"Hypergraph(concepts={len(self.concepts)}, events={len(self.events)})"
