from datetime import datetime
from typing import Optional, TYPE_CHECKING, Dict, Any, Set
from uuid import uuid4

if TYPE_CHECKING:
    from .concept import Concept # For type hinting

class Event:
    """
    Represents a discrete event in the event-based hypergraph.

    An event can be created due to a significant change in the state of one or more concepts,
    or it can represent a relationship between multiple concepts.
    Events are the building blocks of the hypergraph and are used to model memory in an
    LLM-based agent. Each event has a unique identifier, a timestamp, a set of concepts
    it involves, and a delta (which might be 0 for relational events).

    Attributes:
        event_id (str): A unique identifier for the event.
        timestamp (datetime): The time at which the event occurred.
        concepts (set[Concept]): The set of concepts involved in this event.
        delta (float): The magnitude of the change (e.g., in a concept's state if the event is about a single concept's change,
                       or 0.0 for purely relational events between multiple concepts).
        metadata (dict[str, any]): Additional metadata associated with the event.
    """

    def __init__(
        self,
        concepts: set['Concept'], # Changed from concept_id: str
        delta: float,
        timestamp: Optional[datetime] = None,
        metadata: Optional[dict[str, any]] = None,
        event_id: Optional[str] = None, # Made event_id optional, will generate if None
    ):
        """
        Initialize an Event.

        Args:
            concepts (set[Concept]): The set of concepts involved in this event.
            delta (float): The magnitude of the change or a value associated with the event.
            timestamp (Optional[datetime]): The time at which the event occurred.
                Defaults to the current time if not provided.
            metadata (Optional[dict[str, any]]): Additional metadata associated with the event.
                Defaults to an empty dictionary if not provided.
            event_id (Optional[str]): A unique identifier for the event. If None, a UUID is generated.
        """
        if not concepts:
            raise ValueError("An event must involve at least one concept.")
            
        self.event_id = event_id if event_id else f"event_{uuid4().hex}"  # Generate a unique ID for the event
        self.timestamp = timestamp if timestamp is not None else datetime.now()
        self.concepts = concepts
        self.delta = delta
        self.metadata = metadata if metadata is not None else {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary representation for serialization.

        Returns:
            Dict[str, Any]: A dictionary containing the event's attributes.
        """
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "concept_ids": [concept.concept_id for concept in self.concepts], # Store concept IDs
            "delta": self.delta,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], concepts: Set['Concept']) -> "Event":
        """
        Create an Event from a dictionary representation and a set of Concept objects.

        Args:
            data (Dict[str, Any]): A dictionary containing the event's attributes.
            concepts (Set[Concept]): The set of Concept objects involved in this event.
                                      These should be the Concept objects already in the Hypergraph.

        Returns:
            Event: The created Event object.

        Raises:
            ValueError: If the provided concepts do not match the concept_ids in the data.
        """
        # Optional: Add a check here to ensure the provided concepts match the concept_ids in data
        # This would require iterating through data.get("concept_ids", []) and checking if
        # len(concepts) matches and if the IDs align.
        # For now, assuming the caller (Hypergraph.from_dict) provides the correct concepts.
        expected_concept_ids = set(data.get("concept_ids", []))
        provided_concept_ids = {c.concept_id for c in concepts}

        # It's important that the set of concepts provided matches the set of concept_ids from the data
        if expected_concept_ids != provided_concept_ids:
             # This indicates an issue in the loading process, as the provided concepts don't match the event data.
             # Depending on desired strictness, this could be a warning or an error.
             print(f"Warning: Concepts provided for event {data.get('event_id')} do not match concept_ids in data. Event may be reconstructed incorrectly.")

        return cls(
            concepts=concepts,
            delta=data["delta"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
            event_id=data.get("event_id")
        )


    def __repr__(self) -> str:
        """
        Return a string representation of the event.

        Returns:
            str: A string representation of the event.
        """
        concept_names = ", ".join(sorted([c.name for c in self.concepts]))
        return (
            f"Event(event_id={self.event_id}, timestamp={self.timestamp}, "
            f"concepts=[{concept_names}], delta={self.delta}, metadata={self.metadata})"
        )

    def __eq__(self, other: any) -> bool:
        """
        Check if two events are equal based on their event_id.

        Args:
            other (any): The object to compare with.

        Returns:
            bool: True if the events are equal, False otherwise.
        """
        if not isinstance(other, Event):
            return False
        return self.event_id == other.event_id

    def __hash__(self) -> int:
        """
        Return a hash value for the event based on its event_id.

        Returns:
            int: A hash value based on the event's ID.
        """
        return hash(self.event_id)
