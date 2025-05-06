from datetime import datetime
from typing import dict, Any, Optional
from uuid import uuid4

class Event:
    """
    Represents a discrete event in the event-based hypergraph.

    An event is created when a significant change in the state of a concept is detected.
    Events are the building blocks of the hypergraph and are used to model memory in an
    LLM-based agent. Each event has a unique identifier, a timestamp, a concept that
    changed, and a delta representing the magnitude of the change.

    Attributes:
        event_id (str): A unique identifier for the event.
        timestamp (datetime): The time at which the event occurred.
        concept_id (str): The ID of the concept that changed.
        delta (float): The magnitude of the change in the concept's state.
        metadata (dict[str, Any]): Additional metadata associated with the event.
    """

    def __init__(
        self,
        concept_id: str,
        delta: float,
        timestamp: Optional[datetime] = None,
        metadata: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize an Event.

        Args:
            concept_id (str): The ID of the concept that changed.
            delta (float): The magnitude of the change in the concept's state.
            timestamp (Optional[datetime]): The time at which the event occurred.
                Defaults to the current time if not provided.
            metadata (Optional[dict[str, Any]]): Additional metadata associated with the event.
                Defaults to an empty dictionary if not provided.
        """
        self.event_id = str(uuid4())  # Generate a unique ID for the event
        self.timestamp = timestamp if timestamp is not None else datetime.now()
        self.concept_id = concept_id
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
            "concept_id": self.concept_id,
            "delta": self.delta,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Event":
        """
        Create an Event from a dictionary representation.

        Args:
            data (dict[str, Any]): A dictionary containing the event's attributes.

        Returns:
            Event: An Event object.
        """
        return cls(
            concept_id=data["concept_id"],
            delta=data["delta"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data["metadata"],
        )

    def __repr__(self) -> str:
        """
        Return a string representation of the event.

        Returns:
            str: A string representation of the event.
        """
        return (
            f"Event(event_id={self.event_id}, timestamp={self.timestamp}, "
            f"concept_id={self.concept_id}, delta={self.delta}, metadata={self.metadata})"
        )

    def __eq__(self, other: Any) -> bool:
        """
        Check if two events are equal.

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
        Return a hash value for the event.

        Returns:
            int: A hash value based on the event's ID.
        """
        return hash(self.event_id)