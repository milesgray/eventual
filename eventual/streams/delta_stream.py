"""
# DeltaStream

The `DeltaStream` module computes changes between instances of sensory data to create a delta stream. It detects significant changes in concept states and generates events, which are added to the hypergraph.

## Usage

```python
from eventual.core import Hypergraph
from eventual.streams import SensoryEventStream, InstanceStream, DeltaStream

# Initialize hypergraph and streams
hypergraph = Hypergraph()
sensory_stream = SensoryEventStream(hypergraph)
instance_stream = InstanceStream(sensory_stream)
delta_stream = DeltaStream(hypergraph, instance_stream, threshold=0.1)

# Add a concept to the hypergraph
concept = Concept(concept_id="light_1", name="light", initial_state=1.0)
hypergraph.add_concept(concept)

# Compute deltas
events = delta_stream.compute_deltas()
print(events)
```
"""
from datetime import datetime
from eventual.core import TemporalBoundary, Event, Hypergraph
from eventual.streams.instance_stream import InstanceStream
from eventual.utils.numerical_properties import compute_delta

class DeltaStream:
    """
    A class for computing changes between instances of sensory data to create a delta stream.

    The DeltaStream processes instances of sensory data, compares them to previous states,
    and generates deltas representing significant changes in concept states. These deltas
    are used to create events, which are added to the hypergraph.

    Attributes:
        hypergraph (Hypergraph): The hypergraph where concepts and events are stored.
        instance_stream (InstanceStream): The stream of instances to process.
        temporal_boundary (TemporalBoundary): The temporal boundary detector for creating events.
        previous_states (Dict[str, float]): A dictionary storing the previous state of each concept.
    """

    def __init__(self, hypergraph: Hypergraph, instance_stream: InstanceStream, threshold: float = 0.1):
        """
        Initialize the DeltaStream with a hypergraph, instance stream, and threshold.

        Args:
            hypergraph (Hypergraph): The hypergraph to store concepts and events.
            instance_stream (InstanceStream): The stream of instances to process.
            threshold (float): The threshold for detecting significant changes.
        """
        self.hypergraph = hypergraph
        self.instance_stream = instance_stream
        self.temporal_boundary = TemporalBoundary(threshold=threshold)
        self.previous_states = {}

    def compute_deltas(self) -> list[Event]:
        """
        Compute deltas between the current and previous states of concepts.

        Returns:
            list[Event]: A list of events generated from significant changes in concept states.
        """
        events = []
        instances = self.instance_stream.process()

        for instance in instances:
            concept_id = instance["concept_id"]
            current_state = instance["state"]

            # Get the previous state of the concept
            previous_state = self.previous_states.get(concept_id, None)

            if previous_state is not None:
                # Compute the delta between the current and previous states
                delta = compute_delta(previous_state, current_state)

                # Check if the delta exceeds the threshold
                if abs(delta) >= self.temporal_boundary.threshold:
                    concept = self.hypergraph.concepts.get(concept_id)
                    if concept:
                        # Create an event for the significant change
                        event = Event(
                            event_id=f"event_{len(self.hypergraph.events)}",
                            timestamp=datetime.now(),
                            concept=concept,
                            delta=delta
                        )
                        events.append(event)
                        self.hypergraph.add_event(event)

            # Update the previous state of the concept
            self.previous_states[concept_id] = current_state

        return events