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
from datetime import timedelta
# Assuming you have a populated hypergraph instance
# from eventual.ingestors.hypergraph_integrator import HypergraphIntegrator
# from eventual.processors.chat_ingestor import ChatIngestor
# from eventual.processors.text_processor import TextProcessor

# Example: Create and populate a hypergraph (as done in pipeline or tests)
hypergraph = Hypergraph()
# ... populate hypergraph with concepts and events ...

# Initialize the adapter with the hypergraph
adapter = SituationalAwarenessAdapter(hypergraph=hypergraph)

# Generate context based on a query and recent events (short-term memory)
query = "tell me about the user's recent activity"
recent_time_window = timedelta(minutes=5)
context_string = adapter.generate_context(query, recent_time_window=recent_time_window)

print("Generated Context for LLM:")
print(context_string)
```
"""
from typing import List, Tuple, Optional
from datetime import timedelta
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

    def generate_context(self, query: str, recent_time_window: Optional[timedelta] = None) -> str:
        """
        Generates a context string based on a query and optionally recent events.

        Retrieves concepts and events relevant to the query and recent events within
        the specified time window.

        Args:
            query (str): The query string used to retrieve relevant information from the hypergraph.
            recent_time_window (Optional[timedelta]): A timedelta to specify the window for recent events (short-term memory).
                                                     If None, only query-based retrieval is performed.

        Returns:
            str: A formatted string containing relevant concepts and events (short and long term).
                 Returns an empty string if no relevant knowledge is found.
        """\
        # Retrieve knowledge based on the query (represents potentially long-term relevant info)
        query_relevant_concepts, query_relevant_events = self._hypergraph.retrieve_knowledge(query)

        # Retrieve recent events (represents short-term memory)
        recent_events: List[Event] = []
        if recent_time_window is not None:
            recent_events = self._hypergraph.get_recent_events(recent_time_window)

        # Combine the retrieved knowledge
        # Use sets to avoid duplicates when combining
        combined_concepts = set(query_relevant_concepts)
        for event in recent_events:
             combined_concepts.update(event.concepts)

        combined_events = set(query_relevant_events).union(set(recent_events))

        context_parts: List[str] = []

        if combined_concepts:
            # Sort concepts by name for consistent output
            sorted_concepts = sorted(list(combined_concepts), key=lambda c: c.name)
            concept_names = ", ".join([c.name for c in sorted_concepts])
            # Adjust header based on whether query matched any concepts and if recent events were considered
            if query and recent_time_window is not None:
                 header = "Concepts related to the query and recent activity:"
            elif query:
                 header = "Concepts related to the query:"
            elif recent_time_window is not None:
                 header = "Concepts related to recent activity:"
            else:
                 header = "Concepts:" # Fallback

            context_parts.append(f"{header} {concept_names}.")

        if combined_events:
            context_parts.append("Relevant Events:")
            # Sort events by timestamp (most recent first) for consistent output
            sorted_events = sorted(list(combined_events), key=lambda e: e.timestamp, reverse=True)
            event_descriptions: List[str] = []
            for event in sorted_events:
                # Simple representation: Event ID, Concepts involved, Delta, and Metadata
                # This can be made more sophisticated depending on desired context detail
                concept_names_in_event = ", ".join(sorted([c.name for c in event.concepts]))
                description = f"Event {event.event_id}: Concepts [{concept_names_in_event}], Delta {event.delta:.2f}, Metadata {event.metadata}"
                event_descriptions.append(description)
            context_parts.append("""
""".join(event_descriptions))

        if not context_parts:
            return ""

        # Join with a separator (e.g., newline) between different parts of the context
        return """
""".join(context_parts)

    # You might add other methods here for different context generation strategies,
    # e.g., generating context based on specific concepts, or integrating summarization.
