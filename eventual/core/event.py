from datetime import datetime
from typing import Any, Optional, Set, TYPE_CHECKING
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
        concepts (Set[Concept]): The set of concepts involved in this event.
        delta (float): The magnitude of the change (e.g., in a concept's state if the event is about a single concept's change,
                       or 0.0 for purely relational events between multiple concepts).
        metadata (dict[str, Any]): Additional metadata associated with the event.
    """

    def __init__(
        self,
        concepts: Set['Concept'], # Changed from concept_id: str
        delta: float,
        timestamp: Optional[datetime] = None,
        metadata: Optional[dict[str, Any]] = None,
        event_id: Optional[str] = None, # Made event_id optional, will generate if None
    ):
        """
        Initialize an Event.

        Args:
            concepts (Set[Concept]): The set of concepts involved in this event.
            delta (float): The magnitude of the change or a value associated with the event.
            timestamp (Optional[datetime]): The time at which the event occurred.
                Defaults to the current time if not provided.
            metadata (Optional[dict[str, Any]]): Additional metadata associated with the event.
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

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the event to a dictionary representation.

        Returns:
            dict[str, Any]: A dictionary containing the event's attributes.
        """
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "concept_ids": [concept.concept_id for concept in self.concepts], # Store concept IDs
            "delta": self.delta,
            "metadata": self.metadata,
        }

    # from_dict would become more complex as it would need access to the Hypergraph
    # or a way to retrieve Concept objects from IDs to reconstruct the concepts set.
    # For now, I will comment it out as it's not directly used by the current TextProcessor flow
    # and would require more context on how it should behave (e.g., if it needs a Hypergraph instance).
    # @classmethod
    # def from_dict(cls, data: dict[str, Any], hypergraph: Optional['Hypergraph'] = None) -> "Event":
    #     """
    #     Create an Event from a dictionary representation.
    #     Requires a hypergraph instance to retrieve concepts by their IDs.
    #     """
    #     retrieved_concepts = set()
    #     if hypergraph and "concept_ids" in data:
    #         for concept_id in data["concept_ids"]:
    #             concept = hypergraph.get_concept(concept_id)
    #             if concept:
    #                 retrieved_concepts.add(concept)
    #         if len(retrieved_concepts) != len(data["concept_ids"]):
    #             # Handle missing concepts appropriately, e.g., raise error or log warning
    #             pass 
    #     if not retrieved_concepts and "concept_ids" in data and data["concept_ids"]:
    #           raise ValueError("Could not reconstruct concepts for Event from_dict without a valid hypergraph or if concepts are missing.")

    #     return cls(
    #         concepts=retrieved_concepts,
    #         delta=data["delta"],
    #         timestamp=datetime.fromisoformat(data["timestamp"]),
    #         metadata=data["metadata"],
    #         event_id=data.get("event_id") # event_id was missing in previous version here
    #     )

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

    def __eq__(self, other: Any) -> bool:
        """
        Check if two events are equal based on their event_id.

        Args:
            other (Any): The object to compare with.

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
