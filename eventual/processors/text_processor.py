"""
# TextProcessor

The `TextProcessor` module is responsible for extracting concepts and their numerical properties from text data. It uses advanced NLP techniques and potentially LLM calls to identify key concepts, calculate their relevance, and detect significant changes over time. Following the refactoring, it now returns standardized data structures (`ProcessorOutput`) instead of directly modifying a hypergraph.

## Usage

```python
from eventual.utils.text_processor import TextProcessor
# Assuming Hypergraph, Concept, Event, and an Integrator class are available elsewhere
# from eventual.core import Hypergraph, Concept, Event
# from eventual.ingestors import HypergraphIntegrator

# Initialize the TextProcessor (loads LLM config from eventual/config.yaml)
processor = TextProcessor()

# --- Using the default spaCy/TF-IDF concept extraction ---
# Extract concepts from text using the default method (spaCy/TF-IDF)
# The processor now returns extracted data, it does NOT modify a hypergraph directly.
text_tfidf = "The light is too bright, and the sounds are overwhelming. The sounding is also very loud."
print("
--- TF-IDF Concept Extraction ---")
processor_output_tfidf = processor.extract_concepts(text_tfidf)
print("Extracted Concepts (TF-IDF scores - based on lemmas):", processor_output_tfidf.extracted_concepts)
# To integrate this data into a hypergraph, you would pass it to an Integrator:
# hypergraph = Hypergraph()
# integrator = HypergraphIntegrator()
# integrator.integrate(processor_output_tfidf, hypergraph)
# print("Hypergraph concepts after TF-IDF:", {c.name: c.state for c in hypergraph.concepts.values()}) # Show concept names (lemmas) and states

# --- Using the LLM-based concept and graph extraction ---
# Extract concepts and build a graph using the LLM
# The processor now returns extracted data, it does NOT modify a hypergraph directly.
text_llm = "Google released Gemini models. Gemini is a powerful AI model. Google is a tech company. Releasing models is complex."
print("
--- LLM Concept and Graph Extraction ---")
# Note: This requires a valid LLM configuration in eventual/config.yaml and API keys set.
try:
    processor_output_llm = processor.extract_concepts_and_graph_llm(text_llm)
    print("Extracted Concepts from LLM:", processor_output_llm.extracted_concepts)
    print("Extracted Events from LLM:", processor_output_llm.extracted_events)
    # To integrate this data into a hypergraph:
    # hypergraph_llm = Hypergraph() # Or use the same hypergraph instance
    # integrator_llm = HypergraphIntegrator()
    # integrator_llm.integrate(processor_output_llm, hypergraph_llm)
    # print("Hypergraph concepts after LLM:", {c.name: c.state for c in hypergraph_llm.concepts.values()})
    # print("Hypergraph events after LLM:", [(event.event_id, {c.name for c in event.concepts}) for event in hypergraph_llm.events.values()])

except Exception as e:
    print(f"Skipping LLM processing due to error: {e}")
    print("Please ensure litellm is configured correctly with valid API keys.")

# --- Detecting Phase Shifts ---
# Detect phase shifts between two texts using the default method.
# The processor now returns extracted data, it does NOT modify a hypergraph directly.
text1 = "The room was dark and quiet."
text2 = "The room is now bright and noisy."
print(f"
Detecting phase shifts between '{text1}' and '{text2}'")
# extract_concepts is called internally, it will return ProcessorOutput, 
# and detect_phase_shifts will return ExtractedEvent objects representing the shifts.
phase_shifts_events = processor.detect_phase_shifts(text1, text2, delta_threshold=0.1)
print("Extracted Phase Shift Events (Concept Lemma, Delta):", [(e.concept_identifiers[0], e.delta) for e in phase_shifts_events if e.concept_identifiers])
# To integrate phase shift events:
# hypergraph_phases = Hypergraph() # Or use the same hypergraph instance
# integrator_phases = HypergraphIntegrator()
# # You would likely need a method in Integrator to handle a list of specific event objects
# # integrator_phases.integrate_events(phase_shifts_events, hypergraph_phases)
# # Concepts involved in these events would be added when integrating the events.

```

## Configuration

The `TextProcessor` loads LLM configuration from `eventual/config.yaml`. Ensure this file exists
and contains an `llm_settings` section with parameters like `model`, `temperature`, `top_p`, etc.

```yaml
# eventual/config.yaml

llm_settings:
  model: "gpt-4o" # Or your preferred litellm-supported model
  temperature: 0.7
  top_p: 1.0
  # Add other model-specific parameters as needed
```

Ensure your environment variables are set correctly for the chosen LLM provider (e.g., `OPENAI_API_KEY`).

## Classes

### `TextProcessor`
A class for processing text data to extract concepts and their numerical properties, designed to work with an external Hypergraph via an Integrator.

"""
from typing import Optional
import re
from collections import defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
import litellm
import os
import json
import yaml
from uuid import uuid4
from datetime import datetime

# Import the new processor output dataclasses
from eventual.processors.processor_output import ProcessorOutput, ExtractedConcept, ExtractedEvent

# Assuming Concept and Event classes are available in eventual.core (though TextProcessor won't instantiate them directly anymore)
# from eventual.core.hypergraph import Hypergraph
# from eventual.core.concept import Concept
# from eventual.core.event import Event

class TextProcessor:
    """
    A class for processing text data to extract concepts and their numerical properties.

    The TextProcessor uses NLP techniques and LLM calls to identify key concepts in text data
    and assign numerical values or identify relationships. It now returns structured data
    representing the extracted information, which can then be integrated into a Hypergraph
    or other data store by a separate component (e.g., an Integrator).

    It supports dynamic concept extraction, normalization, using lemmatization
    to handle different word forms.

    Attributes:
        nlp (spacy.Language): A pre-trained spaCy NLP model for text processing.
        vectorizer (TfidfVectorizer): A TF-IDF vectorizer for calculating term importance.
        concept_map (dict[str, list[str]]): A mapping of concepts (lemmas) to their synonyms or related terms (used in the default method).
        llm_settings (dict): Settings loaded from config.yaml for LLM calls.
    """

    def __init__(self, language_model: str = "en_core_web_sm", config_path="eventual/config.yaml"):
        """
        Initialize the TextProcessor with a language model and configuration.

        Loads LLM configuration from the specified YAML file.

        Args:
            language_model (str): The name of the spaCy language model to load. Defaults to "en_core_web_sm".
            config_path (str): The path to the configuration file for LLM settings. Defaults to "eventual/config.yaml".
        """
        self.nlp = spacy.load(language_model)
        self.vectorizer = TfidfVectorizer(stop_words="english")
        # Ensure concept map keys are lemmas
        self.concept_map = {self._get_lemma(k): [self._get_lemma(s) for s in v] for k, v in self._load_default_concept_map().items()}
        self.llm_settings = self._load_llm_config(config_path)

        # Ensure API keys are set up as environment variables for litellm
        # litellm picks these up automatically based on the model used.
        # e.g., export OPENAI_API_KEY='YOUR_API_KEY'

    def _get_lemma(self, text: str) -> str:
        """Gets the root form (lemma) of a single word or short phrase.

        Args:
            text: The input text.

        Returns:
            The lemma of the text.
        """
        if not text:
            return ""
        # Process the text with spaCy and return the lemma of the first token
        doc = self.nlp(text)
        if doc and doc[0]:
            return doc[0].lemma_.lower()
        return text.lower() # Fallback to lower case if lemmatization fails

    def _load_default_concept_map(self) -> dict[str, list[str]]:
        """
        Load a default mapping of concepts to their synonyms or related terms.

        Note: The keys and values of this map should ideally be in their root forms (lemmas).

        Returns:
            dict[str, list[str]]: A dictionary mapping concepts (lemmas) to lists of related terms (lemmas).
        """
        return {
            "light": ["brightness", "illumination", "glow", "radiance"],
            "darkness": ["shadow", "gloom", "obscurity", "dimness", "dark"], 
            "sound": ["noise", "volume", "audio", "acoustics", "noisy"], 
            "silence": ["quiet", "hush", "stillness", "calm", "silent"], 
            "temperature": ["heat", "cold", "warmth", "chill"],
        }

    def _load_llm_config(self, config_path: str) -> dict:
        """
        Loads LLM configuration from a YAML file.

        Looks for an 'llm_settings' section in the YAML file.

        Args:
            config_path: The path to the configuration file.

        Returns:
            dict: A dictionary containing LLM settings. Returns default settings if file is not found or parsing fails.
        """
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                # Provide default LLM settings if not found in config
                llm_settings = config.get("llm_settings", {})
                if not llm_settings:
                     print(f"Warning: 'llm_settings' not found in {config_path}. Using default LLM settings.")
                     llm_settings = {
                        "model": "gpt-4o", # Default model
                        "temperature": 0.7,
                        "top_p": 1.0,
                    }
                return llm_settings

        except FileNotFoundError:
            print(f"Warning: Config file not found at {config_path}. Using default LLM settings.")
            return {
                "model": "gpt-4o", # Default model
                "temperature": 0.7,
                "top_p": 1.0,
            }
        except yaml.YAMLError as e:
            print(f"Error parsing config file {config_path}: {e}. Using default LLM settings.")
            return {
                "model": "gpt-4o", # Default model
                "temperature": 0.7,
                "top_p": 1.0,
            }

    def extract_concepts(self, text: str, normalize: bool = True) -> ProcessorOutput:
        """
        Extract concepts and their numerical values from text data using spaCy and TF-IDF.

        Args:
            text (str): The input text data.
            normalize (bool): Whether to normalize the values to a range of [0, 1]. Defaults to True.

        Returns:
            ProcessorOutput: An object containing the extracted concepts as ExtractedConcept instances.
        """
        if not text:
            return ProcessorOutput()

        # Step 1: Preprocess the text and get tokens as lemmas
        doc = self.nlp(text)
        tokens_lemma = [token.lemma_.lower() for token in doc if not token.is_stop and token.is_alpha]

        # Step 2: Calculate TF-IDF scores for the text using lemmas
        if not tokens_lemma:
            return ProcessorOutput()

        try:
            self.vectorizer.fit([" ".join(tokens_lemma)])
            tfidf_matrix = self.vectorizer.transform([" ".join(tokens_lemma)])
            feature_names = self.vectorizer.get_feature_names_out()
            tfidf_scores = dict(zip(feature_names, tfidf_matrix.toarray()[0]))
        except ValueError: # Handle empty vocabulary case
             return ProcessorOutput()

        # Step 3: Map lemmas to concepts using the concept map (which uses lemmas as keys)
        concept_scores = defaultdict(float)
        for concept_lemma, synonyms_lemmas in self.concept_map.items():
            # Check both the concept lemma itself and its synonyms
            for term_lemma in synonyms_lemmas + [concept_lemma]:
                 if term_lemma in tfidf_scores:
                    concept_scores[concept_lemma] += tfidf_scores[term_lemma]

        # Step 4: Normalize scores if required
        if normalize and concept_scores:
            max_score = max(concept_scores.values())
            if max_score > 0:
                for concept_lemma in concept_scores:
                    concept_scores[concept_lemma] /= max_score

        # Step 5: Create ExtractedConcept instances
        extracted_concepts = []
        for concept_lemma, score in concept_scores.items():
            # Do not assign concept_id here; that's the Integrator's job
            extracted_concepts.append(ExtractedConcept(name=concept_lemma, initial_state=score))

        # Return ProcessorOutput
        return ProcessorOutput(extracted_concepts=extracted_concepts)

    def extract_concepts_and_graph_llm(self, text: str) -> ProcessorOutput:
        """
        Detects concepts and relationships in text using an LLM based on configured settings.
        Returns structured data representing the extracted information.

        Args:
            text: The input text to process.

        Returns:
            ProcessorOutput: An object containing the extracted concepts and events/relationships.
        """
        if not text:
            print("Warning: Invalid input text.")
            return ProcessorOutput()

        # Define the prompt for the LLM
        # Instruct the LLM to provide concepts and relationships using root forms (lemmas).
        prompt = f"""Analyze the following text and extract key concepts and their relationships.
        Please output the concepts and relationships in a JSON format.
        The JSON should have two keys: "concepts" and "relationships".
        "concepts" should be a list of strings, where each string is a key concept found in the text in its root form (lemma).
        "relationships" should be a list of lists, where each inner list contains two strings [concept_A, concept_B] indicating that concept_A is related to concept_B. Both concept names should be in their root form (lemma).
        Only include concepts and relationships that are directly mentioned or strongly implied in the text.

        Text:
        {text}

        JSON Output:
        """

        extracted_concepts = []
        extracted_events = []

        try:
            # Call the LLM using litellm with configured parameters
            response = litellm.completion(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts concepts and relationships from text and formats them as JSON, providing concept names in their root form (lemma)."},
                    {"role": "user", "content": prompt}
                ],
                # Use default model if llm_settings is empty or doesn't have 'model'
                model=self.llm_settings.get("model", "gpt-4o"),
                temperature=self.llm_settings.get("temperature", 0.7),
                top_p=self.llm_settings.get("top_p", 1.0),
                # Pass other potential LLM parameters from self.llm_settings
                **{k: v for k, v in self.llm_settings.items() if k not in ["model", "temperature", "top_p"]}
            )

            # Extract and parse the JSON string from the response
            response_content = response.choices[0].message.content.strip()

            # Handle cases where the LLM might include markdown like ```json ```
            if response_content.startswith("```json"):
                response_content = response_content[len("```json"):].rstrip("```")

            # Handle cases where the response might be wrapped in other text or is not valid JSON
            try:
                data = json.loads(response_content)
            except json.JSONDecodeError as e:
                 print(f"Error decoding JSON from LLM response: {e}")
                 print("LLM Response content:", response_content) # Print the raw response for debugging
                 return ProcessorOutput() # Return empty output on JSON error

            concepts_list = data.get("concepts", [])
            relationships_list = data.get("relationships", [])

            # Create ExtractedConcept instances
            for concept_name in concepts_list:
                concept_lemma = self._get_lemma(concept_name) # Get lemma of LLM concept name
                # Do not assign concept_id here; that's the Integrator's job
                extracted_concepts.append(ExtractedConcept(name=concept_lemma))

            # Create ExtractedEvent instances for relationships
            for relation in relationships_list:
                if len(relation) == 2:
                    concept_a_name, concept_b_name = relation
                    concept_a_lemma = self._get_lemma(concept_a_name) # Get lemma
                    concept_b_lemma = self._get_lemma(concept_b_name) # Get lemma

                    # ExtractedEvent refers to concepts by their names (lemmas in this case)
                    # The Integrator will resolve these names to actual Concept objects in the hypergraph.
                    involved_concept_identifiers = [concept_a_lemma, concept_b_lemma]

                    # Create an ExtractedEvent representing the relationship
                    # Do not assign event_id here; that's the Integrator's job
                    relationship_event = ExtractedEvent(
                        concept_identifiers=involved_concept_identifiers,
                        timestamp=datetime.now(),
                        delta=0.0, # No state change implied by just a relationship
                        event_type='relationship',
                        properties={
                            "source": "LLM_concept_extraction", 
                            "relationship_type": "generic_relation" # Could be more specific if LLM provides it
                         }
                    )
                    extracted_events.append(relationship_event)

        except Exception as e:
            print(f"Error during LLM call: {e}")
            # Continue and return whatever was extracted before the error, or an empty output

        # Return ProcessorOutput
        return ProcessorOutput(extracted_concepts=extracted_concepts, extracted_events=extracted_events)


    def update_concept_map(self, concept: str, synonyms: list[str]):
        """
        Update the concept map with new synonyms or related terms for a concept.
        This is used by the default extract_concepts method.

        Args:
            concept (str): The concept (will be lemmatized) to update.
            synonyms (list[str]): A list of synonyms or related terms (will be lemmatized) for the concept.
        """
        concept_lemma = self._get_lemma(concept)
        synonyms_lemmas = [self._get_lemma(s) for s in synonyms]
        self.concept_map[concept_lemma] = synonyms_lemmas

    def detect_phase_shifts(self, text1: str, text2: str, delta_threshold: float = 0.1) -> list[ExtractedEvent]:
        """
        Detect phase shifts (significant changes) in concepts between two pieces of text
        using the default spaCy/TF-IDF based concept extraction.
        Returns a list of ExtractedEvent objects for detected shifts.

        The concepts themselves are extracted by calling `extract_concepts` internally,
        but this method focuses on identifying the *change* and representing it as an event.

        Args:
            text1 (str): The first text for comparison.
            text2 (str): The second text for comparison.
            delta_threshold (float): The minimum change in concept score to consider a phase shift. Defaults to 0.1.

        Returns:
            list[ExtractedEvent]: A list of ExtractedEvent objects representing the phase shifts.
        """
        # Use extract_concepts to get scores for both texts. 
        # It now returns ProcessorOutput, but we only need the concept scores for comparison here.
        concepts1_output = self.extract_concepts(text1, normalize=True)
        concepts2_output = self.extract_concepts(text2, normalize=True)

        # Convert ExtractedConcept lists to dictionaries for easier score lookup
        concepts1_scores = {c.name: c.initial_state for c in concepts1_output.extracted_concepts}
        concepts2_scores = {c.name: c.initial_state for c in concepts2_output.extracted_concepts}

        phase_shift_events = []
        all_concepts_lemmas = set(concepts1_scores.keys()).union(set(concepts2_scores.keys()))
        
        for concept_lemma in all_concepts_lemmas:
            score1 = concepts1_scores.get(concept_lemma, 0.0)
            score2 = concepts2_scores.get(concept_lemma, 0.0)
            delta = score2 - score1 # Use directional delta for the event

            if abs(delta) > delta_threshold:  # Check against the threshold
                 # Create an ExtractedEvent for the phase shift
                 # The event involves the concept that changed, identified by its lemma (name)
                 involved_concept_identifiers = [concept_lemma]

                 # Create an ExtractedEvent representing the phase shift
                 # Do not assign event_id here; that's the Integrator's job
                 phase_shift_event = ExtractedEvent(
                     concept_identifiers=involved_concept_identifiers,
                     timestamp=datetime.now(),
                     delta=delta, 
                     event_type='phase_shift',
                     properties={
                         "source": "TFIDF_phase_shift_detection", 
                         "delta_magnitude": abs(delta),
                         "text1_score": score1,
                         "text2_score": score2
                     }
                 )
                 phase_shift_events.append(phase_shift_event)

        return phase_shift_events
