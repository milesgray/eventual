"""
## TemporalBoundary

The `TemporalBoundary` class is the core engine of the Eventual framework. It detects significant changes in concept states and generates events when a change exceeds a configurable threshold. The threshold can be adjusted dynamically based on historical data, ensuring that the system adapts to the variability of incoming data.

### Configuration

The behavior of the `TemporalBoundary` can be customized using the `TemporalBoundaryConfig` class:

```python
config = TemporalBoundaryConfig(
    threshold=0.1,  # Minimum change to trigger an event
    decay_factor=0.9,  # Rate at which historical changes decay
    dynamic_threshold=True,  # Whether to adjust the threshold dynamically
)
```
"""
from datetime import datetime
from typing import Optional
from dataclasses import dataclass
from eventual.core import Concept, Event

@dataclass
class TemporalBoundaryConfig:
    """
    Configuration for the TemporalBoundary detector.

    Attributes:
        threshold (float): The minimum change in a concept's state to trigger an event.
        decay_factor (float): The rate at which the significance of past changes decays over time.
        dynamic_threshold (bool): Whether to adjust the threshold dynamically based on historical data.
    """
    threshold: float = 0.1
    decay_factor: float = 0.9
    dynamic_threshold: bool = True

class TemporalBoundary:
    """
    Detects significant changes in concept states and creates events.

    The TemporalBoundary class is the core engine of the Eventual framework. It monitors changes
    in the state of concepts and generates events when a significant change is detected. The
    significance of a change is determined by a configurable threshold, which can be adjusted
    dynamically based on historical data.

    Attributes:
        config (TemporalBoundaryConfig): The configuration for the detector.
        history (dict[str, list[float]]): A history of state changes for each concept.
    """

    def __init__(self, config: Optional[TemporalBoundaryConfig] = None):
        """
        Initialize the TemporalBoundary detector.

        Args:
            config (Optional[TemporalBoundaryConfig]): The configuration for the detector.
                If not provided, default values will be used.
        """
        self.config = config if config else TemporalBoundaryConfig()
        self.history: dict[str, list[float]] = {}

    def _calculate_dynamic_threshold(self, concept_id: str, delta: float) -> float:
        """
        Calculate a dynamic threshold for a concept based on its historical changes.

        Args:
            concept_id (str): The ID of the concept.
            delta (float): The current change in the concept's state.

        Returns:
            float: The dynamic threshold for the concept.
        """
        if concept_id not in self.history:
            self.history[concept_id] = []
        self.history[concept_id].append(delta)

        # Apply exponential decay to historical deltas
        weighted_deltas = [
            delta * (self.config.decay_factor ** i)
            for i, delta in enumerate(reversed(self.history[concept_id]))
        ]
        avg_delta = sum(weighted_deltas) / len(weighted_deltas) if weighted_deltas else 0.0

        # Adjust the threshold based on the average delta
        return self.config.threshold * (1 + avg_delta)

    def detect_event(self, concept: Concept, new_state: float) -> Optional[Event]:
        """
        Detect a significant change in a concept's state and create an event if necessary.

        Args:
            concept (Concept): The concept whose state has changed.
            new_state (float): The new state of the concept.

        Returns:
            Optional[Event]: An event representing the change, or None if no significant change occurred.
        """
        delta = abs(concept.state - new_state)

        # Calculate the threshold (dynamic or static)
        threshold = (
            self._calculate_dynamic_threshold(concept.concept_id, delta)
            if self.config.dynamic_threshold
            else self.config.threshold
        )

        if delta >= threshold:
            # Create an event
            event = Event(
                event_id=f"event_{len(self.history.get(concept.concept_id, []))}",
                timestamp=datetime.now(),
                concepts={concept},
                delta=delta,
            )
            return event
        return None