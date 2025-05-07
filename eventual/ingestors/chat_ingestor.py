"""
# ChatIngestor

The `ChatIngestor` module is responsible for taking raw chat messages,
processing them using a `TextProcessor`, and producing a standardized
`ProcessorOutput` object for further integration into the system.

This component acts as an initial processing layer for chat-based data.

## Usage

```python
from eventual.ingestors.chat_ingestor import ChatIngestor
from eventual.processors.text_processor import TextProcessor
# Assuming Hypergraph and HypergraphIntegrator are available for integration step
# from eventual.core.hypergraph import Hypergraph
# from eventual.ingestors.hypergraph_integrator import HypergraphIntegrator

# Initialize the TextProcessor (can be configured separately)
text_processor = TextProcessor()

# Initialize the ChatIngestor with the TextProcessor
chat_ingestor = ChatIngestor(text_processor=text_processor)

# Process a chat message
chat_message = "The user is experiencing slow response times."
processor_output = chat_ingestor.ingest(chat_message)

print("Chat Ingestor Output (ProcessorOutput):", processor_output)
print("Extracted Concepts:", processor_output.extracted_concepts)
print("Extracted Events:", processor_output.extracted_events)

# To integrate this into a hypergraph:
# hypergraph = Hypergraph()
# integrator = HypergraphIntegrator()
# integrator.integrate(processor_output, hypergraph)
# print("Hypergraph state after chat ingestion:", hypergraph)
```
"""
from typing import Optional
from eventual.processors.text_processor import TextProcessor
from eventual.processors.processor_output import ProcessorOutput

class ChatIngestor:
    """
    A class for ingesting chat messages and processing them using a TextProcessor.

    Takes raw chat messages as input, uses an internal TextProcessor instance
    to extract concepts and relationships, and returns a ProcessorOutput object.

    Attributes:
        _text_processor (TextProcessor): An instance of TextProcessor used for processing.
    """

    def __init__(self, text_processor: Optional[TextProcessor] = None):
        """
        Initialize the ChatIngestor.

        Args:
            text_processor (Optional[TextProcessor]): An optional TextProcessor instance to use.
                                                      If None, a new one will be initialized.
        """
        self._text_processor = text_processor if text_processor is not None else TextProcessor()

    def ingest(self, message: str) -> ProcessorOutput:
        """
        Ingest a chat message and process it to extract concepts and relationships.

        Args:
            message (str): The raw chat message text.

        Returns:
            ProcessorOutput: A structured object containing extracted concepts and events
                             from the chat message.
        """
        if not message:
            print("Warning: Empty chat message received.")
            return ProcessorOutput() # Return empty output for empty message

        # Use the TextProcessor to extract concepts (and potentially events if using LLM method later)
        # For now, we'll assume the basic TF-IDF concept extraction is the default.
        # If LLM-based graph extraction or phase shift detection is needed from chat messages,
        # this ingest method might need to be more sophisticated or offer more options.
        processor_output = self._text_processor.extract_concepts(message)
        
        print(f"ChatIngestor processed message. Extracted {len(processor_output.extracted_concepts)} concepts.")
        return processor_output
