"""
# Context Injector

The `ContextInjector` is responsible for taking the relevant knowledge retrieved
by the `SituationalAwarenessAdapter` and formatting it along with the user's
query into a single context string that can be provided to an LLM.

This component prepares the final input string for the LLM, combining historical
knowledge and the current query.

## Usage

```python
from eventual.adapters.situational_awareness_adapter import SituationalAwarenessAdapter
from eventual.core.hypergraph import Hypergraph
from eventual.context.context_injector import ContextInjector

# Assuming you have a populated hypergraph and an initialized adapter
hypergraph = Hypergraph()
# ... populate hypergraph ...
adapter = SituationalAwarenessAdapter(hypergraph=hypergraph)

# Generate the knowledge context from the adapter
query = "What is the user's mood?"
knowledge_context = adapter.generate_context(query)

# Initialize the injector
injector = ContextInjector()

# Inject the context with the user's query
user_query = "I am feeling happy today."
full_context_for_llm = injector.inject_context(knowledge_context, user_query)

print("Full Context for LLM:")
print(full_context_for_llm)
```
"""
from typing import List

class ContextInjector:
    """
    Prepares the final context string for an LLM by combining knowledge context and the user query.
    """
    def __init__(self):
        """
        Initialize the ContextInjector.
        """
        pass # No specific initialization needed for this basic version

    def inject_context(self, knowledge_context: str, user_query: str) -> str:
        """
        Combines the knowledge context and the user query into a single string.

        Args:
            knowledge_context (str): The formatted knowledge context from the SituationalAwarenessAdapter.
            user_query (str): The user's current query or message.

        Returns:
            str: A single string containing both the knowledge context and the user query,
                 formatted for LLM input.
        """
        # Simple concatenation for now. More sophisticated formatting can be added later,
        # e.g., using specific tokens or structures to delineate context sections.
        if knowledge_context:
            # Add a separator if there is knowledge context to distinguish it from the query
            return f"""{knowledge_context}

User Query: {user_query}"""
        else:
            # If no knowledge context, just return the user query
            return user_query
