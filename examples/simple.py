from eventual.core import Concept, Event, Hypergraph, TemporalBoundary
from eventual.streams import SensoryEventStream

# Initialize hypergraph and temporal boundary
hypergraph = Hypergraph()
temporal_boundary = TemporalBoundary(threshold=0.1)

# Create a concept
light_concept = Concept(concept_id="light_1", name="light", initial_state=1.0)
hypergraph.add_concept(light_concept)

# Simulate a change in state
new_state = 0.0
event = temporal_boundary.detect_event(light_concept, new_state)
if event:
    hypergraph.add_event(event)
    light_concept.update_state(new_state)

print(hypergraph)