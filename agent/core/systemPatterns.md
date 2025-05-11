## System Architecture and Design Patterns

The `Eventual` framework is built around an event-based hypergraph architecture, designed to model memory for LLM-based agents.

- **Event-Based System**: The core components are `Concept` and `Event` objects. Events act as hyperedges connecting concepts and recording changes or relationships between them.
- **Hypergraph Data Structure**: The `Hypergraph` class serves as the central repository for managing all concepts and events, forming a dynamic hypergraph structure.
- **Memory Modeling**: The hypergraph is specifically designed to serve as the primary data structure for modeling and managing the memory of an LLM agent.
- **Query Processing**: The system incorporates natural language processing capabilities (utilizing spaCy) within the `Hypergraph` to process queries and facilitate the retrieval of relevant concepts and events.
- **Persistence**: The architecture includes methods for serializing and deserializing the hypergraph, allowing the agent's memory state to be saved and loaded across sessions.