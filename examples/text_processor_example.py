#!/usr/bin/env python3
"""
Example usage of the TextProcessor with a Hypergraph.

This script demonstrates how to use the TextProcessor to extract concepts
using both TF-IDF and LLM-based methods, and how to detect phase shifts,
all while populating a Hypergraph structure.

To run this example:
1. Ensure you have the required libraries installed: `pip install -r requirements.txt` (or install them manually: `pytest pytest-mock PyYAML scikit-learn spacy litellm`)
2. Download the spaCy language model: `python -m spacy download en_core_web_sm`
3. Create or update `eventual/config.yaml` with your LLM settings (including model and API key setup).
4. Run the script: `python examples/text_processor_example.py`
"""

from eventual.utils.text_processor import TextProcessor
from eventual.core.hypergraph import Hypergraph
from eventual.core.concept import Concept
from eventual.core.event import Event

# Initialize a hypergraph to store processed concepts and events
hypergraph = Hypergraph()

# Initialize the TextProcessor (loads LLM config from eventual/config.yaml)
# Make sure your LLM API keys are set as environment variables
processor = TextProcessor()

print("Initialized Hypergraph and TextProcessor.")

# --- Using the default spaCy/TF-IDF concept extraction ---
# Extract concepts from text using the default method (spaCy/TF-IDF)
# Pass the hypergraph to add detected concepts as nodes.
text_tfidf = "The light is too bright, and the sound is overwhelming. The sound is also very loud."
print(f"Processing text with TF-IDF: '{text_tfidf}'")
concepts_tfidf = processor.extract_concepts(text_tfidf, hypergraph=hypergraph)
print("Concepts (TF-IDF scores):", concepts_tfidf)
print("Hypergraph after TF-IDF processing (Concepts count):", len(hypergraph.concepts))
# print("Hypergraph concepts after TF-IDF:", hypergraph.concepts) # Uncomment for detailed view

# --- Using the LLM-based concept and graph extraction ---
# Extract concepts and build a graph using the LLM
# The detected concepts and relationships will be added to the hypergraph.
# Concepts are added as nodes, relationships as Events.
text_llm = "Google released Gemini models. Gemini is a powerful AI model. Google is a tech company."
print(f"Processing text with LLM: '{text_llm}'")
# Note: This requires a valid LLM configuration in eventual/config.yaml and API keys set.
try:
    processor.extract_concepts_and_graph_llm(text_llm, hypergraph)
    print("Hypergraph after LLM processing (Concepts count):", len(hypergraph.concepts))
    print("Hypergraph after LLM processing (Events count):", len(hypergraph.events))
    # print("Hypergraph concepts after LLM:", hypergraph.concepts) # Uncomment for detailed view
    # print("Hypergraph events after LLM:", hypergraph.events) # Uncomment for detailed view
except Exception as e:
    print(f"Skipping LLM processing due to error: {e}")
    print("Please ensure litellm is configured correctly with valid API keys.")

# --- Detecting Phase Shifts ---
# Detect phase shifts between two texts using the default method.
# Pass the hypergraph to add Events representing detected phase shifts.
text1 = "The room is dark and quiet."
text2 = "The room is now bright and noisy."
print(f"Detecting phase shifts between '{text1}' and '{text2}'")
# extract_concepts is called internally, which will add concepts to hypergraph if they don't exist
phase_shifts_data = processor.detect_phase_shifts(text1, text2, hypergraph=hypergraph, delta_threshold=0.1)
print("Phase Shifts Detected (Concept, Delta):", phase_shifts_data)
print("Hypergraph after Phase Shift detection (Concepts count):", len(hypergraph.concepts)) # Concepts might be added/updated indirectly
print("Hypergraph after Phase Shift detection (Events count):", len(hypergraph.events)) # New Events for phase shifts

# --- Inspecting the Hypergraph ---
print("--- Final Hypergraph Contents ---")
print(f"Total Concepts in Hypergraph: {len(hypergraph.concepts)}")
print(f"Total Events in Hypergraph: {len(hypergraph.events)}")

# Example of how to access concepts and events:
# for concept_id, concept in hypergraph.concepts.items():
#     print(f"Concept ID: {concept_id}, Name: {concept.name}, State: {concept.state}")
#     print(f"  Related Events Count: {len(concept.events)}")

# for event_id, event in hypergraph.events.items():
#      concept_names = [c.name for c in event.concepts]
#      print(f"Event ID: {event_id}, Timestamp: {event.timestamp}, Concepts: {concept_names}, Delta: {event.delta}, Metadata: {event.metadata}")
