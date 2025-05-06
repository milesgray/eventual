"""
# DeltaStream

The `DeltaStream` module computes changes between instances of sensory data to create a delta stream. It detects significant changes in concept states and generates structured event data (`ExtractedEvent`), which can then be integrated into a hypergraph or other data store by a separate component (e.g., an Integrator).

## Usage

```python
from eventual.streams import InstanceStream, DeltaStream, SensoryEventStream
# Assuming Hypergraph and HypergraphIntegrator are available for integration step
# from eventual.core import Hypergraph
# from eventual.ingestors import HypergraphIntegrator
# Assuming Concept exists if needed for creating initial instance stream data
# from eventual.core.concept import Concept
from datetime import datetime

# Initialize streams (SensoryEventStream might still need Hypergraph for context in other uses,
# but DeltaStream no longer requires it directly)
# hypergraph_for_sensory = Hypergraph() # If needed by SensoryEventStream
# sensory_stream = SensoryEventStream(hypergraph_for_sensory)
# instance_stream = InstanceStream(sensory_stream)

# For demonstrating DeltaStream in isolation, let's use a mock InstanceStream output
# In a real pipeline, InstanceStream would provide this data.
class MockInstanceStream:
    def process(self):
        # Simulate instances with concept IDs and states over time
        return [
            {"concept_id": "light_1", "state": 0.2, "timestamp": datetime.now()},
            {"concept_id": "sound_2", "state": 0.5, "timestamp": datetime.now()},
            {"concept_id": "light_1", "state": 0.8, "timestamp": datetime.now()}, # Significant change for light
            {"concept_id": "sound_2", "state": 0.6, "timestamp": datetime.now()}, # Small change for sound
        ]

instance_stream = MockInstanceStream()

# Initialize delta stream (no hypergraph needed now)
delta_stream = DeltaStream(instance_stream, threshold=0.1)

# Compute deltas - now returns a list of ExtractedEvent objects
extracted_delta_events = delta_stream.compute_deltas()

print("Extracted Delta Events:", extracted_delta_events)

# To integrate these events into a hypergraph:
# hypergraph = Hypergraph()
# integrator = HypergraphIntegrator()
# # DeltaStream returns a list of ExtractedEvent, package it in a ProcessorOutput
# from eventual.processors.processor_output import ProcessorOutput
# delta_output = ProcessorOutput(extracted_events=extracted_delta_events)
# integrator.integrate(delta_output, hypergraph)
# print("Hypergraph state after integrating delta events:", hypergraph)

```
"""
from datetime import datetime
from typing import Optional

# Remove imports from eventual.core as DeltaStream no longer interacts directly with Hypergraph/Event
# from eventual.core import TemporalBoundary, Event, Hypergraph
from eventual.core.temporal_boundary import TemporalBoundary, TemporalBoundaryConfig # Keep TemporalBoundary as it's a helper
from eventual.streams.instance_stream import InstanceStream
from eventual.utils.numerical_properties import compute_delta

# Import the structured output format
from eventual.processors.processor_output import ExtractedEvent

class DeltaStream:
    """
    A class for computing changes between instances of sensory data to create a delta stream.

    The DeltaStream processes instances of sensory data, compares them to previous states,
    and generates deltas representing significant changes in concept states. These deltas
    are returned as structured `ExtractedEvent` objects for external integration.

    Attributes:
        instance_stream (InstanceStream): The stream of instances to process.
        temporal_boundary (TemporalBoundary): The temporal boundary detector for detecting significant changes.
        previous_states (dict[str, float]): A dictionary storing the previous state of each concept (keyed by concept ID).
    """

    def __init__(self, instance_stream: InstanceStream, threshold: float = 0.1):
        """
        Initialize the DeltaStream with an instance stream and threshold.

        Args:
            instance_stream (InstanceStream): The stream of instances to process.
            threshold (float): The threshold for detecting significant changes.
        """
        # Removed hypergraph from constructor
        self.instance_stream = instance_stream
        temporal_boundary_config = TemporalBoundaryConfig(threshold=threshold)
        self.temporal_boundary = TemporalBoundary(config=temporal_boundary_config)
        self.previous_states: dict[str, float] = {}

    def compute_deltas(self, initial_events) -> list[ExtractedEvent]:
        """
        Compute deltas between the current and previous states of concepts.

        Returns:
            list[ExtractedEvent]: A list of structured `ExtractedEvent` objects generated 
                                  from significant changes in concept states.
        """
        extracted_events: list[ExtractedEvent] = []
        instances = self.instance_stream.process(initial_events) # Assuming process() returns a list of dicts or similar

        for instance in instances:
            # Assuming instance is a dictionary with at least 'concept_id' and 'state'
            concept_id = instance.concept_id
            current_state = instance.value
            timestamp = instance.timestamp # Use instance timestamp

            if concept_id is None or current_state is None:
                print(f"Warning: Skipping instance due to missing 'concept_id' or 'state': {instance}")
                continue

            # Get the previous state of the concept using concept_id as key
            previous_state = self.previous_states.get(concept_id)

            if previous_state is not None:
                # Compute the delta between the current and previous states
                delta = compute_delta(previous_state, current_state)

                # Check if the delta exceeds the threshold
                if abs(delta) >= self.temporal_boundary.config.threshold:
                    # Create an ExtractedEvent for the significant change
                    # The concept is referred to by its ID (or name, if that's what the stream provides)
                    # DeltaStream doesn't need the full Concept object from the Hypergraph anymore.
                    phase_shift_event = ExtractedEvent(
                        # Use concept_id as the identifier for the event
                        concept_identifiers=[concept_id],
                        timestamp=timestamp, # Use the instance timestamp
                        delta=delta, 
                        event_type='state_change',
                        properties={
                            "source": "DeltaStream",
                            "delta_magnitude": abs(delta),
                            "previous_state": previous_state,
                            "current_state": current_state
                        }
                    )
                    extracted_events.append(phase_shift_event)
                    # Removed the direct call to hypergraph.add_event(event)

            # Update the previous state of the concept AFTER computing delta for the current instance
            self.previous_states[concept_id] = current_state

        print(f"DeltaStream computed {len(extracted_events)} significant delta events.")
        return extracted_events

# Note: The InstanceStream and SensoryEventStream classes in this module
# might also need to be reviewed and updated depending on their internal logic
# and interaction with the Hypergraph, if any.
# SensoryEventStream currently takes a Hypergraph in its __init__ - this might need review.
# InstanceStream takes a SensoryEventStream - its logic needs review if SensoryEventStream changes.
