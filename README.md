# eventual

An LLM powered toolkit for extracting Event-Driven Knowledge Graphs from arbitrary sources.

`eventual` is a Python library designed to facilitate the creation and manipulation of event-based hypergraphs. It provides tools for defining core concepts, handling data streams, integrating data from various sources, and leveraging the power of Large Language Models (LLMs) to extract structured knowledge in the form of knowledge graphs grounded in events.

## Features

*   **Event-Driven Hypergraphs:** Build and manage complex relationships using hypergraphs, where nodes represent concepts and hyperedges represent events connecting multiple concepts.
*   **Core Concepts:** Define and work with fundamental building blocks like Concepts, Events, Sensors, and Temporal Boundaries.
*   **Data Handling:** Includes modules for extracting and integrating data from various sources to populate the hypergraph.
*   **Data Streams:** Process and manage different types of data flow with specialized stream implementations (Delta Stream, Instance Stream, Sensory Event Stream).
*   **Utilities:** Helper functions for tasks such as numerical property handling and text processing.
*   **LLM Integration:** Designed to work in conjunction with LLMs for advanced knowledge extraction and graph population.

## Installation

Requires Python 3.6+.

You can install `eventual` using pip:

```bash
pip install eventual
```

Dependencies such as `numpy` and `pandas` will be installed automatically.

## Usage

The library provides modules for defining and interacting with the core components of the event-driven knowledge graph.

Here is a conceptual example of how you might use the library:

```python
from eventual.core.hypergraph import Hypergraph
from eventual.core.event import Event
from eventual.core.concept import Concept
from eventual.core.sensor import Sensor

# Create a hypergraph
graph = Hypergraph("MyEventKnowledgeGraph")

# Define concepts
person_concept = Concept("Person")
organization_concept = Concept("Organization")

graph.add_concept(person_concept)
graph.add_concept(organization_concept)

# Define an event type
hire_event_type = Event("HireEvent")

# Create an event instance
# This is a simplified representation; actual event creation might involve more details
hire_event = hire_event_type("John Doe hired by ExampleCorp")

# Add participants to the event (connecting concepts via the event)
hire_event.add_participant(person_concept, "John Doe")
hire_event.add_participant(organization_concept, "ExampleCorp")

# Add the event to the hypergraph
graph.add_event(hire_event)

# Example using a sensor (conceptual)
# sensor = Sensor("DocumentSensor")
# extracted_data = sensor.process("Article about John Doe joining ExampleCorp")
# graph.integrate_data(extracted_data) # Assuming an integration method exists
```

For more detailed examples, please refer to the `examples/` directory.

## Project Structure

*   `eventual/core/`: Contains the fundamental classes for `Concept`, `Event`, `Hypergraph`, `Sensor`, and `TemporalBoundary`.
*   `eventual/data/`: Modules for data `extractor` and `integrator`.
*   `eventual/streams/`: Implementations for different data stream types (`delta_stream`, `instance_stream`, `sensory_event_stream`).
*   `eventual/utils/`: Utility functions, including `numerical_properties` and `text_processor`.
*   `examples/`: Practical usage examples.
*   `tests/`: Unit tests.

## Contributing

Contributions are welcome! Please see the `CONTRIBUTING.md` file (if it exists, otherwise, mention standard process) for details on how to contribute.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

