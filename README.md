# eventual

An LLM powered toolkit for building Event-Driven Knowledge Graphs for AI Agent Situational Awareness in Chat Scenarios.

`eventual` is a Python library designed to facilitate the creation and manipulation of event-based hypergraphs, specifically tailored for providing enhanced situational awareness to LLM-based agents in chat environments. It processes conversational data to build and update a dynamic knowledge graph, enabling agents to access and utilize relevant context grounded in past interactions and events.

## Features

*   **Event-Driven Hypergraphs:** Build and manage complex relationships using hypergraphs, where nodes represent concepts and hyperedges represent events connecting multiple concepts. This serves as the agent's dynamic memory.
*   **Chat Message Ingestion:** Process raw chat messages to extract concepts and relationships relevant to the conversation.
*   **Knowledge Retrieval:** Query the event hypergraph to retrieve relevant concepts and events based on the current conversational context or specific queries.
*   **Situational Awareness Adapter:** Format retrieved knowledge from the hypergraph into a concise representation suitable for injection into an LLM agent's context window.
*   **Persistence:** Save and load the hypergraph to maintain the agent's memory across sessions.
*   **Long-Term Memory Handling:** Distinguish and manage short-term (recent) and long-term (older, relevant) memories within the hypergraph for efficient context provision.
*   **Core Concepts:** Define and work with fundamental building blocks like Concepts, Events, Sensors (adaptable for chat input), and Temporal Boundaries.
*   **Data Handling & Streams:** Includes modules for processing and managing data flow, adaptable for sequential chat messages.
*   **LLM Integration:** Designed to integrate with LLMs by providing a structured, contextually relevant representation of the conversation history and related knowledge.

## Installation

Requires Python 3.6+.

You can install `eventual` using pip:

```bash
pip install eventual
```

Dependencies such as `numpy`, `pandas`, and `spacy` (for text processing) will be installed automatically.

## Usage

The library provides components to build a pipeline for processing chat messages and utilizing the resulting knowledge graph.

Here is a conceptual example of how you might use the library in a chat scenario:

```python
from eventual.core.hypergraph import Hypergraph
from eventual.ingestors.chat_ingestor import ChatIngestor
from eventual.adapters.situational_awareness_adapter import SituationalAwarenessAdapter
from eventual.context.context_injector import ContextInjector
from eventual.persistence.hypergraph_persistence import HypergraphPersistence
from eventual.processors.text_processor import TextProcessor
from datetime import timedelta

# --- Setup (typically done once per agent instance or session load) ---
# Initialize persistence manager and load existing hypergraph or create a new one
persistence_manager = HypergraphPersistence()
HYPERGRAPH_FILE = ".gemini/agent_memory.json"
hypergraph = persistence_manager.load_hypergraph(HYPERGRAPH_FILE)
if hypergraph is None:
    print("No existing memory found, creating a new hypergraph.")
    hypergraph = Hypergraph()

# Initialize components
text_processor = TextProcessor() # Can be initialized with specific config
chat_ingestor = ChatIngestor(text_processor=text_processor)
awareness_adapter = SituationalAwarenessAdapter(hypergraph=hypergraph)
context_injector = ContextInjector()

# --- Processing a User Message (in a chat loop) ---
user_message = "The user wants to book a flight to London next week."

# 1. Ingest the chat message to extract concepts and events
processor_output = chat_ingestor.ingest(user_message)

# 2. Integrate the extracted knowledge into the hypergraph
# Assuming HypergraphIntegrator is used within a pipeline or separately
# from eventual.ingestors.hypergraph_integrator import HypergraphIntegrator
# integrator = HypergraphIntegrator()
# integrator.integrate(processor_output, hypergraph)
# print(f"Hypergraph state after ingestion: {hypergraph}")
# Note: In a real scenario, integration might happen after each message or batched.

# 3. Retrieve relevant knowledge (short-term and long-term)
# You might formulate a query based on the user_message or agent's goal
retrieval_query = "what is the user asking about?"
recent_window = timedelta(minutes=10) # Define recent memory window

knowledge_context = awareness_adapter.generate_context(retrieval_query, recent_time_window=recent_window)

# 4. Inject the context for the LLM
full_context_for_llm = context_injector.inject_context(knowledge_context, user_message)

print("
--- Full Context for LLM ---")
print(full_context_for_llm)

# --- Save (periodically or at end of session) ---
# persistence_manager.save_hypergraph(hypergraph, HYPERGRAPH_FILE)
# print(f"Hypergraph memory saved to {HYPERGRAPH_FILE}")

```

For more detailed examples and pipeline configuration, please refer to the `examples/` directory.

## Project Structure

*   `eventual/core/`: Fundamental classes (`Concept`, `Event`, `Hypergraph`, `Sensor`, `TemporalBoundary`).
*   `eventual/data/`: Modules for data extraction and integration (generic pipeline steps).
*   `eventual/streams/`: Data stream implementations (`delta_stream`, `instance_stream`, `sensory_event_stream`).
*   `eventual/utils/`: Utility functions (`numerical_properties`, `text_processor`).
*   `eventual/ingestors/`: Components for ingesting specific data types (`chat_ingestor`, `hypergraph_integrator`).
*   `eventual/adapters/`: Components for adapting hypergraph data (`situational_awareness_adapter`).
*   `eventual/context/`: Components for preparing LLM context (`context_injector`).
*   `eventual/persistence/`: Components for saving and loading the hypergraph (`hypergraph_persistence`).
*   `examples/`: Practical usage examples.
*   `tests/`: Unit tests.

## Contributing

Contributions are welcome! Please see the `CONTRIBUTING.md` file (if it exists, otherwise, mention standard process) for details on how to contribute.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
