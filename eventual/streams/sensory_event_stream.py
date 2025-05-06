from datetime import datetime
from typing import Callable, Any, Dict, List
from dataclasses import dataclass
# Removed import for Hypergraph and Event as these are no longer managed directly
# from eventual.core import Concept, Event, Hypergraph
from eventual.core.temporal_boundary import TemporalBoundary # Keep TemporalBoundary

@dataclass
class SensorConfig:
    """
    Configuration for a sensor, including its type and data processing function.

    Attributes:
        sensor_id (str): Unique identifier for the sensor.
        sensor_type (str): Type of sensor (e.g., "text", "light").
        processor (Callable): Function to process raw data into concept states (returns dict[str, float] or similar).
    """
    sensor_id: str
    sensor_type: str
    processor: Callable[[Any], Dict[str, float]]

class SensoryEventStream:
    """
    A class for ingesting raw sensory data and converting it into a stream of event data (dictionaries).

    The SensoryEventStream processes raw data from various sensor feeds (e.g., text, light, sound)
    and transforms it into a list of dictionaries suitable for processing by an InstanceStream.
    It no longer directly interacts with a Hypergraph.
    """

    def __init__(self, default_threshold: float = 0.1):
        """
        Initialize the SensoryEventStream (no hypergraph needed).

        Args:
            default_threshold (float): Default threshold for detecting significant changes (used internally by TemporalBoundary).
        """
        # No hypergraph needed here anymore.
        # self.hypergraph = hypergraph
        self.sensors: Dict[str, SensorConfig] = {}
        self.temporal_boundary = TemporalBoundary(threshold=default_threshold)

    def add_sensor(self, sensor_id: str, sensor_type: str, processor: Callable[[Any], Dict[str, float]]):
        """
        Add a sensor to the sensory event stream.

        Args:
            sensor_id (str): A unique identifier for the sensor.
            sensor_type (str): The type of sensor (e.g., "text", "light").
            processor (Callable): Function to process raw data into concept states.  This should output
                                  a dictionary of concept names (strings) and values (floats).
        """
        self.sensors[sensor_id] = SensorConfig(sensor_id, sensor_type, processor)

    def ingest(self, sensor_id: str, data: Any) -> List[Dict[str, Any]]:
        """
        Ingest raw data from a sensor and process it into a list of event data (dictionaries).

        Args:
            sensor_id (str): The ID of the sensor providing the data.
            data (Any): The raw data from the sensor.

        Returns:
            List[Dict[str, Any]]: A list of event data dictionaries, each containing concept_id, timestamp, and delta.

        Raises:
            ValueError: If the sensor ID is not found.
        """
        if sensor_id not in self.sensors:
            raise ValueError(f"Sensor with ID {sensor_id} not found.")

        sensor_config = self.sensors[sensor_id]
        processed_data = sensor_config.processor(data)

        event_data_list: List[Dict[str, Any]] = []

        for concept_name, value in processed_data.items():
            # Generate a unique concept ID (the Integrator will handle actual ID assignment)
            concept_id = f"concept_{concept_name}"  # Consistent naming scheme
            # We can no longer directly check hypergraph.concepts - it's up to the next stages to handle
            # if concept_id not in self.hypergraph.concepts:  # Removed check
            #     # Create a new concept if it doesn't exist
            #     concept = Concept(concept_id, concept_name, initial_state=value)
            #     self.hypergraph.add_concept(concept)
            # else:
            #     # Update the existing concept's state
            #     concept = self.hypergraph.concepts[concept_id]
            #     event = self.temporal_boundary.detect_event(concept, value)
            #     if event:
            #         events.append(event)
            #         concept.update_state(value)
            event_data: Dict[str, Any] = {
                "concept_id": concept_id,
                "timestamp": datetime.now(),
                "delta": value,  # Use processed data value as delta
                "sensor_id": sensor_id # Add more metadata as needed
            }
            event_data_list.append(event_data)

        # Remove adding events to the hypergraph - it's up to the integrator now
        # for event in events:
        #     self.hypergraph.add_event(event)
        print(f"SensoryEventStream ingested data from sensor '{sensor_id}' and created {len(event_data_list)} event data entries.")

        return event_data_list

# No longer need TemporalBoundary as a class attribute; it will be called in process() if needed
# class TemporalBoundary:
#     """
#     Detects significant changes in concept states to create events.
#
#     Attributes:
#         threshold (float): The minimum change required to trigger an event.
#     """
#
#     def __init__(self, threshold: float = 0.1):
#         """
#         Initialize the TemporalBoundary with a threshold.
#
#         Args:
#             threshold (float): The minimum change required to trigger an event.
#         """
#         self.threshold = threshold
#
#     def detect_event(self, concept: Concept, new_state: float) -> Event | None:
#         """
#         Detect if a change in concept state is significant enough to create an event.
#
#         Args:
#             concept (Concept): The concept whose state has changed.
#             new_state (float): The new state of the concept.
#
#         Returns:
#             Union[Event, None]: An event if the change is significant, otherwise None.
#         """
#         delta = abs(concept.state - new_state)
#         if delta >= self.threshold:
#             return Event(
#                 event_id=f"event_{len(self.hypergraph.events)}",
#                 timestamp=datetime.now(),
#                 concept=concept,
#                 delta=delta
#             )
#         return None
