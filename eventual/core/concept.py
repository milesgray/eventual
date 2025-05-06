"""
## Concept Module

The `Concept` class represents a concept with numerical properties that can change over time. It is a core component of the Eventual framework, used to track state changes and generate events.

### Usage

```python
from eventual.core import Concept

# Create a new concept
light_concept = Concept(name="light", initial_state=1.0)

# Update the state
light_concept.update_state(0.5, reason="Light dimmed")

# Add metadata
light_concept.add_metadata("source", "sensor_1")

# Retrieve history
for entry in light_concept.get_history():
    print(entry)
```

"""
from typing import Any, Optional, Set
from datetime import datetime
from uuid import uuid4

# Forward declaration for type hinting if Event is in a separate file and imported
# This avoids circular import issues if Concept and Event reference each other.
# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from .event import Event # Assuming Event is in event.py in the same directory

class Concept:
    """
    A class representing a concept with numerical properties that can change over time.

    A concept is a fundamental unit in the Eventual framework, representing an abstract or concrete
    entity (e.g., "light", "darkness", "temperature") that can be sensed and tracked. Each concept
    has a state, which is a numerical value representing its current condition. Changes in the state
    of a concept are used to generate events.

    Attributes:
        concept_id (str): A unique identifier for the concept.
        name (str): The name of the concept (e.g., "light", "darkness").
        state (float): The current state of the concept (numerical value).
        history (List[dict[str, Any]]): A history of state changes, including timestamps and deltas.
        metadata (dict[str, Any]): Additional metadata about the concept (e.g., source, context).
        events (Set[Event]): A set of events this concept is part of.
    """

    def __init__(self, concept_id: Optional[str] = None, name: str = "", initial_state: float = 0.0, metadata: Optional[dict[str, Any]] = None):
        """
        Initialize a Concept instance.

        Args:
            concept_id (Optional[str]): A unique identifier for the concept. If not provided, a UUID will be generated.
            name (str): The name of the concept (e.g., "light", "darkness").
            initial_state (float): The initial state of the concept (default: 0.0).
            metadata (Optional[dict[str, Any]]): Additional metadata about the concept (e.g., source, context).
        """
        self.concept_id = concept_id if concept_id else f"concept_{uuid4().hex}"
        self.name = name
        self.state = initial_state
        self.history = []  # Tracks state changes over time
        self.metadata = metadata if metadata else {}
        self.events: Set[Any] = set() # Set of Event objects this concept is part of; Use Any to break circular dependency for now, or forward reference

        # Record the initial state in history
        self._record_state_change(initial_state, "Initial state")

    def update_state(self, new_state: float, reason: Optional[str] = None):
        """
        Update the state of the concept and record the change in history.

        Args:
            new_state (float): The new state of the concept.
            reason (Optional[str]): A description of why the state changed (e.g., "sensor input").
        """
        if new_state != self.state:
            delta = new_state - self.state
            self.state = new_state
            self._record_state_change(new_state, reason, delta)

    def _record_state_change(self, new_state: float, reason: Optional[str] = None, delta: Optional[float] = None):
        """
        Record a state change in the concept's history.

        Args:
            new_state (float): The new state of the concept.
            reason (Optional[str]): A description of why the state changed.
            delta (Optional[float]): The change in state (new_state - previous_state).
        """
        self.history.append({
            "timestamp": datetime.now(),
            "state": new_state,
            "delta": delta,
            "reason": reason
        })

    def get_history(self) -> list[dict[str, Any]]:
        """
        Get the history of state changes for the concept.

        Returns:
            List[dict[str, Any]]: A list of state change records, each containing:
                - timestamp: The time of the state change.
                - state: The new state.
                - delta: The change in state.
                - reason: The reason for the state change.
        """
        return self.history

    def add_metadata(self, key: str, value: Any):
        """
        Add or update metadata for the concept.

        Args:
            key (str): The metadata key.
            value (Any): The metadata value.
        """
        self.metadata[key] = value

    def get_metadata(self, key: str) -> Optional[Any]:
        """
        Retrieve metadata for the concept.

        Args:
            key (str): The metadata key.

        Returns:
            Optional[Any]: The metadata value, or None if the key does not exist.
        """
        return self.metadata.get(key)

    def __repr__(self):
        """
        Return a string representation of the Concept instance.

        Returns:
            str: A string representation of the concept.
        """
        return f"Concept(concept_id={self.concept_id}, name={self.name}, state={self.state}, history_length={len(self.history)}, events_count={len(self.events)})"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Concept):
            return False
        return self.concept_id == other.concept_id

    def __hash__(self) -> int:
        return hash(self.concept_id)
