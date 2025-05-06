"""
## InstanceStream

The `InstanceStream` class is responsible for breaking down sensory event streams into granular instances. These instances represent the smallest meaningful units of data and are used to compute delta streams.

### Usage

```python
from eventual.core import Hypergraph
from eventual.streams import SensoryEventStream, InstanceStream

# Initialize hypergraph and sensory event stream
hypergraph = Hypergraph()
sensory_event_stream = SensoryEventStream(hypergraph)

# Add a sensor and ingest data
sensory_event_stream.add_sensor("sensor_1", "text")
sensory_event_stream.ingest("sensor_1", "The light is too bright.")

# Process the sensory event stream into instances
instance_stream = InstanceStream(hypergraph)
instances = instance_stream.process_sensory_event_stream(sensory_event_stream)

print(instances)
```
"""
from typing import Any, Optional
from datetime import datetime
from eventual.core import Concept, Event, Hypergraph
from eventual.streams.sensory_event_stream import SensoryEventStream
from eventual.utils.numerical_properties import normalize_value

class Instance:
    """
    Represents a granular instance of data, which is the smallest meaningful unit in a sensory event stream.

    Attributes:
        instance_id (str): A unique identifier for the instance.
        timestamp (datetime): The time at which the instance was created.
        concept_id (str): The ID of the concept associated with this instance.
        value (float): The numerical value of the instance.
        metadata (dict[str, Any]): Additional metadata about the instance (e.g., source sensor, raw data).
    """

    def __init__(self, instance_id: str, timestamp: datetime, concept_id: str, value: float, metadata: Optional[dict[str, Any]] = None):
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

    The InstanceStream processes events from a SensoryEventStream and decomposes them into
    individual instances, which represent the smallest meaningful units of data. These instances
    are then used to compute delta streams, which capture changes in concept states over time.

    Attributes:
        hypergraph (Hypergraph): The hypergraph where concepts and events are stored.
        instances (list[Instance]): A list of instances generated from the sensory event stream.
    """

    def __init__(self, hypergraph: Hypergraph):
        """
        Initialize the InstanceStream with a hypergraph.

        Args:
            hypergraph (Hypergraph): The hypergraph to store concepts and events.
        """
        self.hypergraph = hypergraph
        self.instances = []

    def process_event(self, event: Event) -> list[Instance]:
        """
        Process an event and decompose it into granular instances.

        Args:
            event (Event): The event to process.

        Returns:
            list[Instance]: A list of instances generated from the event.
        """
        instances = []

        # Extract the concept associated with the event
        concept = self.hypergraph.concepts.get(event.concept.concept_id)
        if not concept:
            raise ValueError(f"Concept with ID {event.concept.concept_id} not found in hypergraph.")

        # Create an instance for the event
        instance_id = f"instance_{len(self.instances)}"
        instance = Instance(
            instance_id=instance_id,
            timestamp=event.timestamp,
            concept_id=concept.concept_id,
            value=event.delta,
            metadata={
                "event_id": event.event_id,
                "concept_name": concept.name,
                "source": "event",
            },
        )
        instances.append(instance)

        # Add the instance to the stream
        self.instances.append(instance)

        return instances

    def process_sensory_event_stream(self, sensory_event_stream: SensoryEventStream) -> list[Instance]:
        """
        Process all events from a sensory event stream and decompose them into instances.

        Args:
            sensory_event_stream (SensoryEventStream): The sensory event stream to process.

        Returns:
            list[Instance]: A list of instances generated from the sensory event stream.
        """
        instances = []
        for event in sensory_event_stream.hypergraph.events:
            instances.extend(self.process_event(event))
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