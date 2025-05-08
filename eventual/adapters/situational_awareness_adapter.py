"""
# Situational Awareness Adapter

The `SituationalAwarenessAdapter` is responsible for retrieving relevant knowledge
from the `Hypergraph` and formatting it into a concise representation that can be
injected into an LLM agent's context window.

It acts as a bridge between the structured knowledge in the hypergraph and the
 kebutuhan contextual kebutuhan kontekstual LLM.

## Usage

```python
from eventual.core.hypergraph import Hypergraph
from eventual.adapters.situational_awareness_adapter import SituationalAwarenessAdapter
# Assuming you have a populated hypergraph instance
# from eventual.ingestors.hypergraph_integrator import HypergraphIntegrator
# from eventual.processors.chat_ingestor import ChatIngestor
# from eventual.processors.text_processor import TextProcessor

# Example: Create and populate a hypergraph (as done in pipeline or tests)
hypergraph = Hypergraph()
# ... populate hypergraph with concepts and events ...

# Initialize the adapter with the hypergraph
adapter = SituationalAwarenessAdapter(hypergraph=hypergraph)

# Generate context based on a query or the current state
query = "tell me about the recent events"
context_string = adapter.generate_context(query)

print("Generated Context for LLM:")
print(context_string)
```
"""
from typing import List, Tuple
from eventual.core.hypergraph import Hypergraph
from eventual.core.concept import Concept
from eventual.core.event import Event

class SituationalAwarenessAdapter:
    """
    Adapts hypergraph knowledge into a format suitable for LLM context.

    Retrieves relevant concepts and events from a Hypergraph instance and formats
    them into a string representation that can be injected into an LLM's prompt
    to enhance situational awareness.

    Attributes:
        _hypergraph (Hypergraph): The Hypergraph instance to retrieve knowledge from.
    """

    def __init__(self, hypergraph: Hypergraph):
        """
        Initialize the SituationalAwarenessAdapter.

        Args:
            hypergraph (Hypergraph): The Hypergraph instance containing the knowledge graph.
        """
        if not isinstance(hypergraph, Hypergraph):
            raise TypeError("hypergraph must be an instance of Hypergraph")
        self._hypergraph = hypergraph

    def generate_context(self, query: str) -> str:
        """
        Generates a context string based on a query by retrieving relevant knowledge.

        Args:
            query (str): The query string used to retrieve relevant information from the hypergraph.

        Returns:
            str: A formatted string containing relevant concepts and events.
                 Returns an empty string if no relevant knowledge is found.
        """
        relevant_concepts, relevant_events = self._hypergraph.retrieve_knowledge(query)

        context_parts: List[str] = []

        if relevant_concepts:
            concept_names = ", ".join(sorted([c.name for c in relevant_concepts]))
            context_parts.append(f"Concepts related to the query: {concept_names}.")

        if relevant_events:
            context_parts.append("Relevant Events:")
            for event in relevant_events:
                # Simple representation: Event ID, Concepts involved, Delta, and Metadata
                # This can be made more sophisticated depending on desired context detail
                concept_names_in_event = ", ".join(sorted([c.name for c in event.concepts]))
                description = f"Event {event.event_id}: Concepts [{concept_names_in_event}], Delta {event.delta:.2f}, Metadata {event.metadata}"
                context_parts.append(description)

        if not context_parts:
            return ""

        return "
".join(context_parts)

    # You might add other methods here for different context generation strategies,
    # e.g., generating context based on recent events, or combining multiple queries.
