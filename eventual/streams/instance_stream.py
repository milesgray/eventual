"""
## InstanceStream

The `InstanceStream` class is responsible for breaking down sensory event streams into granular instances. These instances represent the smallest meaningful units of data and are used to compute delta streams.

This version assumes that the input stream (SensoryEventStream or similar) already provides the necessary
concept information, so it no longer directly accesses the Hypergraph.

### Usage

```python
from eventual.streams import SensoryEventStream, InstanceStream
from datetime import datetime

# Assuming SensoryEventStream is defined and provides necessary concept information in its events
# and a mock SensoryEventStream output for demonstration:
class MockSensoryEventStream:
    def process(self):
        # Simulate events with concept IDs and values
        return [
            {"event_id": "event_1", "timestamp": datetime.now(), "concept_id": "light_1", "delta": 0.5},
            {"event_id": "event_2", "timestamp": datetime.now(), "concept_id": "sound_2", "delta": 0.8}
        ]

sensory_event_stream = MockSensoryEventStream()

# Process the sensory event stream into instances
instance_stream = InstanceStream()
instances = instance_stream.process(sensory_event_stream.process())

print(instances)
```
"""
from typing import Optional
from datetime import datetime
# Removed import of Hypergraph, Concept, and Event
# from eventual.core import Concept, Event, Hypergraph # No longer needs Hypergraph

# Kept import of SensoryEventStream as that is the input stream
# Update if SensoryEventStream also stops using Hypergraph directly
from eventual.streams.sensory_event_stream import SensoryEventStream

# Removed dependency on utils.numerical_properties - if it's needed it should be passed or instantiated within the class.
# from eventual.utils.numerical_properties import normalize_value

class Instance:
    """
    Represents a granular instance of data, which is the smallest meaningful unit in a sensory event stream.

    Attributes:
        instance_id (str): A unique identifier for the instance.
        timestamp (datetime): The time at which the instance was created.
        concept_id (str): The ID of the concept associated with this instance.
        value (float): The numerical value of the instance.
        metadata (dict[str, any]): Additional metadata about the instance (e.g., source event ID).
    """

    def __init__(self, instance_id: str, timestamp: datetime, concept_id: str, value: float, metadata: Optional[dict[str, any]] = None):
        self.instance_id = instance_id
        self.timestamp = timestamp
        self.concept_id = concept_id
        self.value = value
        self.metadata = metadata or {}

    def __repr__(self):
        return f"Instance(instance_id={self.instance_id}, timestamp={self.timestamp}, concept_id={self.concept_id}, value={self.value})"

class InstanceStream:
    """
    A class for breaking down sensory event streams into granular instance streams.

    The InstanceStream processes events from an input stream (e.g., SensoryEventStream) and decomposes them into
    individual instances, which represent the smallest meaningful units of data. These instances
    are then used to compute delta streams, which capture changes in concept states over time.

    This version is decoupled from the Hypergraph and relies on the input stream providing 
    the necessary concept information.
    """

    # Removed hypergraph dependency
    def __init__(self):
        """
        Initialize the InstanceStream. No longer requires a hypergraph.
        """
        self.instances: list[Instance] = []

    # Updated to take the event data directly, not the SensoryEventStream object
    def process_event(self, event_data: dict[str, any]) -> list[Instance]:
        """
        Process a single event and decompose it into granular instances.

        Args:
            event_data (dict[str, any]): A dictionary containing event information.  This is ASSUMED to have
                                          'concept_id', 'timestamp', and 'delta' keys (or similar names).

        Returns:
            list[Instance]: A list of instances generated from the event.
        """
        instances: list[Instance] = []

        # Now expects the necessary information to be *in* the event_data
        concept_id = event_data.get("concept_id")
        timestamp = event_data.get("timestamp")
        delta = event_data.get("delta")

        if concept_id is None or timestamp is None or delta is None:
            print(f"Warning: Skipping event due to missing required keys (concept_id, timestamp, or delta): {event_data}")
            return instances # Return empty list

        # Create an instance for the event
        instance_id = f"instance_{len(self.instances)}"
        instance = Instance(
            instance_id=instance_id,
            timestamp=timestamp,
            concept_id=concept_id,
            value=delta,
            metadata={
                "event_id": event_data.get("event_id"),  # Presume event_id is also part of event_data
                # Removed: concept_name - InstanceStream no longer needs it
                # "concept_name": concept.name,
                "source": "event",
            },
        )
        instances.append(instance)

        # Add the instance to the stream
        self.instances.append(instance)

        return instances

    # Updated to take a LIST of event data (dictionaries), not a SensoryEventStream object
    def process(self, event_data_list: list[dict[str, any]]) -> list[Instance]:
        """
        Process all events from a list of event data (dictionaries) and decompose them into instances.

        Args:
            event_data_list (list[dict[str, any]]): A list of dictionaries, where each dictionary represents an event.

        Returns:
            list[Instance]: A list of instances generated from the events.
        """
        instances: list[Instance] = []
        for event_data in event_data_list:
            instances.extend(self.process_event(event_data))
        return instances

    def get_instances_by_concept(self, concept_id: str) -> list[Instance]:
        """
        Retrieve all instances associated with a specific concept.

        Args:
            concept_id (str): The ID of the concept.

        Returns:
            list[Instance]: A list of instances associated with the concept.
        """
        return [instance for instance in self.instances if instance.concept_id == concept_id]

    def __repr__(self):
        return f"InstanceStream(instances={len(self.instances)})"
