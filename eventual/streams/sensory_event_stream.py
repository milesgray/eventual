
from datetime import datetime
from typing import Callable, Any
from dataclasses import dataclass
from eventual.core import Concept, Event, Hypergraph

@dataclass
class SensorConfig:
    """
    Configuration for a sensor, including its type and data processing function.

    Attributes:
        sensor_id (str): Unique identifier for the sensor.
        sensor_type (str): Type of sensor (e.g., "text", "light").
        processor (Callable): Function to process raw data into concept states.
    """
    sensor_id: str
    sensor_type: str
    processor: Callable[[Any], dict[str, float]]

class SensoryEventStream:
    """
    A class for ingesting raw sensory data and converting it into a stream of events.

    The SensoryEventStream processes raw data from various sensor feeds (e.g., text, light, sound)
    and transforms it into events by detecting changes in the state of concepts. These events are
    then added to a hypergraph for further processing.

    Attributes:
        hypergraph (Hypergraph): The hypergraph where concepts and events are stored.
        sensors (dict[str, SensorConfig]): A dictionary of sensor configurations.
        temporal_boundary (TemporalBoundary): The temporal boundary detector for creating events.
    """

    def __init__(self, hypergraph: Hypergraph, default_threshold: float = 0.1):
        """
        Initialize the SensoryEventStream with a hypergraph.

        Args:
            hypergraph (Hypergraph): The hypergraph to store concepts and events.
            default_threshold (float): Default threshold for detecting significant changes.
        """
        self.hypergraph = hypergraph
        self.sensors: dict[str, SensorConfig] = {}
        self.temporal_boundary = TemporalBoundary(threshold=default_threshold)

    def add_sensor(self, sensor_id: str, sensor_type: str, processor: Callable[[Any], dict[str, float]]):
        """
        Add a sensor to the sensory event stream.

        Args:
            sensor_id (str): A unique identifier for the sensor.
            sensor_type (str): The type of sensor (e.g., "text", "light").
            processor (Callable): Function to process raw data into concept states.
        """
        self.sensors[sensor_id] = SensorConfig(sensor_id, sensor_type, processor)

    def ingest(self, sensor_id: str, data: Any) -> list[Event]:
        """
        Ingest raw data from a sensor and process it into events.

        Args:
            sensor_id (str): The ID of the sensor providing the data.
            data (Any): The raw data from the sensor.

        Returns:
            list[Event]: A list of events generated from the data.

        Raises:
            ValueError: If the sensor ID is not found.
        """
        if sensor_id not in self.sensors:
            raise ValueError(f"Sensor with ID {sensor_id} not found.")

        sensor_config = self.sensors[sensor_id]
        processed_data = sensor_config.processor(data)
        events = []

        for concept_name, value in processed_data.items():
            concept_id = f"concept_{concept_name}"
            if concept_id not in self.hypergraph.concepts:
                # Create a new concept if it doesn't exist
                concept = Concept(concept_id, concept_name, initial_state=value)
                self.hypergraph.add_concept(concept)
            else:
                # Update the existing concept's state
                concept = self.hypergraph.concepts[concept_id]
                event = self.temporal_boundary.detect_event(concept, value)
                if event:
                    events.append(event)
                    concept.update_state(value)

        # Add events to the hypergraph
        for event in events:
            self.hypergraph.add_event(event)

        return events

class TemporalBoundary:
    """
    Detects significant changes in concept states to create events.

    Attributes:
        threshold (float): The minimum change required to trigger an event.
    """

    def __init__(self, threshold: float = 0.1):
        """
        Initialize the TemporalBoundary with a threshold.

        Args:
            threshold (float): The minimum change required to trigger an event.
        """
        self.threshold = threshold

    def detect_event(self, concept: Concept, new_state: float) -> Event | None:
        """
        Detect if a change in concept state is significant enough to create an event.

        Args:
            concept (Concept): The concept whose state has changed.
            new_state (float): The new state of the concept.

        Returns:
            Union[Event, None]: An event if the change is significant, otherwise None.
        """
        delta = abs(concept.state - new_state)
        if delta >= self.threshold:
            return Event(
                event_id=f"event_{len(self.hypergraph.events)}",
                timestamp=datetime.now(),
                concept=concept,
                delta=delta
            )
        return None