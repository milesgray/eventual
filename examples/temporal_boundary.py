from eventual.core import Concept, Hypergraph
from eventual.streams import SensoryEventStream
from eventual.core import TemporalBoundary, TemporalBoundaryConfig

# Initialize hypergraph and temporal boundary
hypergraph = Hypergraph()
config = TemporalBoundaryConfig(threshold=0.1, decay_factor=0.9, dynamic_threshold=True)
temporal_boundary = TemporalBoundary(config)

# Create a concept
light_concept = Concept(concept_id="light_1", name="light", initial_state=1.0)
hypergraph.add_concept(light_concept)

# Simulate a change in state
new_state = 0.5
event = temporal_boundary.detect_event(light_concept, new_state)
if event:
    hypergraph.add_event(event)
    light_concept.update_state(new_state)

print(hypergraph)