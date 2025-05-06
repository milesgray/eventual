from datetime import datetime
from uuid import uuid4
from eventual.core import Hypergraph, Concept, Event

# Initialize a hypergraph
hypergraph = Hypergraph()

# Create concepts
light_concept = Concept(concept_id="light_1", name="light", initial_state=1.0)
darkness_concept = Concept(concept_id="darkness_1", name="darkness", initial_state=0.0)

# Add concepts to the hypergraph
hypergraph.add_concept(light_concept)
hypergraph.add_concept(darkness_concept)

# Create an event
event = Event(
    event_id=str(uuid4()),
    timestamp=datetime.now(),
    concepts={light_concept, darkness_concept},
    delta=0.5
)

# Add the event to the hypergraph
hypergraph.add_event(event)

# Query related concepts
related_concepts = hypergraph.find_related_concepts("light_1")
print(related_concepts)  # Output: {Concept(concept_id=darkness_1, name=darkness, state=0.0)}