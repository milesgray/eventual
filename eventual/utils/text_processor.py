"""
# TextProcessor

The `TextProcessor` module is responsible for extracting concepts and their numerical properties from text data. It uses advanced NLP techniques and potentially LLM calls to identify key concepts, calculate their relevance, and detect significant changes over time, storing these within a hypergraph structure.

## Usage

```python
from eventual.utils.text_processor import TextProcessor
from eventual.core import Hypergraph, Concept, Event

# Initialize a hypergraph to store processed concepts and events
hypergraph = Hypergraph()

# Initialize the TextProcessor (loads LLM config from eventual/config.yaml)
processor = TextProcessor()

# --- Using the default spaCy/TF-IDF concept extraction ---
# Extract concepts from text using the default method (spaCy/TF-IDF)
# This will also add the concepts to the hypergraph using their root forms (lemmas).
text_tfidf = "The light is too bright, and the sounds are overwhelming. The sounding is also very loud."
print("
--- TF-IDF Concept Extraction ---")
concepts_tfidf = processor.extract_concepts(text_tfidf, hypergraph=hypergraph)
print("Concepts (TF-IDF scores - based on lemmas):", concepts_tfidf)
print("Hypergraph after TF-IDF processing (Concepts count):", len(hypergraph.concepts))
print("Hypergraph concepts after TF-IDF:", {c.name: c.state for c in hypergraph.concepts.values()}) # Show concept names (lemmas) and states

# --- Using the LLM-based concept and graph extraction ---
# Extract concepts and build a graph using the LLM
# The detected concepts and relationships will be added to the hypergraph using their root forms (lemmas).
# Concepts are added as nodes, relationships as Events.
text_llm = "Google released Gemini models. Gemini is a powerful AI model. Google is a tech company. Releasing models is complex."
print("
--- LLM Concept and Graph Extraction ---")
# Note: This requires a valid LLM configuration in eventual/config.yaml and API keys set.
try:
    processor.extract_concepts_and_graph_llm(text_llm, hypergraph)
    print("Hypergraph after LLM processing (Concepts count):", len(hypergraph.concepts))
    print("Hypergraph after LLM processing (Events count):", len(hypergraph.events))
    print("Hypergraph concepts after LLM:", {c.name: c.state for c in hypergraph.concepts.values()}) # Show concept names (lemmas) and states
    print("Hypergraph events after LLM:", [(event.event_id, {c.name for c in event.concepts}) for event in hypergraph.events.values()]) # Show events and involved concept lemmas
except Exception as e:
    print(f"Skipping LLM processing due to error: {e}")
    print("Please ensure litellm is configured correctly with valid API keys.")

# --- Detecting Phase Shifts ---
# Detect phase shifts between two texts using the default method.
# Pass the hypergraph to add Events representing detected phase shifts.
text1 = "The room was dark and quiet."
text2 = "The room is now bright and noisy."
print(f"
Detecting phase shifts between '{text1}' and '{text2}'")
# extract_concepts is called internally, which will add concepts to hypergraph if they don't exist
phase_shifts_data = processor.detect_phase_shifts(text1, text2, hypergraph=hypergraph, delta_threshold=0.1)
print("Phase Shifts Detected (Concept Lemma, Delta):", phase_shifts_data)
print("Hypergraph after Phase Shift detection (Concepts count):", len(hypergraph.concepts)) # Concepts might be added/updated indirectly
print("Hypergraph after Phase Shift detection (Events count):", len(hypergraph.events)) # New Events for phase shifts

# --- Inspecting the Hypergraph ---
print("
--- Final Hypergraph Contents ---")
print(f"Total Concepts in Hypergraph: {len(hypergraph.concepts)}")
print(f"Total Events in Hypergraph: {len(hypergraph.events)}")

# Example of how to access concepts and events:
# for concept_id, concept in hypergraph.concepts.items():
#     print(f"Concept ID: {concept_id}, Name (Lemma): {concept.name}, State: {concept.state}")
#     print(f"  Related Events Count: {len(concept.events)}")

# for event_id, event in hypergraph.events.items():
#      concept_lemmas = [c.name for c in event.concepts]
#      print(f"Event ID: {event_id}, Timestamp: {event.timestamp}, Concepts (Lemmas): {concept_lemmas}, Delta: {event.delta}, Metadata: {event.metadata}")
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
A class for processing text data to extract concepts and their numerical properties, integrating with a Hypergraph.

"""
from typing import Dict, List, Tuple, Any, Optional
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

# Assuming Concept and Event classes are available in eventual.core
from eventual.core.hypergraph import Hypergraph
from eventual.core.concept import Concept
from eventual.core.event import Event

class TextProcessor:
    """
    A class for processing text data to extract concepts and their numerical properties.

    The TextProcessor uses NLP techniques and LLM calls to identify key concepts in text data
    and assign numerical values or build relationships within a hypergraph structure.
    It supports dynamic concept extraction, normalization, and integration with the Eventual framework,
    using lemmatization to handle different word forms.

    Attributes:
        nlp (spacy.Language): A pre-trained spaCy NLP model for text processing.
        vectorizer (TfidfVectorizer): A TF-IDF vectorizer for calculating term importance.
        concept_map (Dict[str, List[str]]): A mapping of concepts (lemmas) to their synonyms or related terms (used in the default method).
        llm_settings (Dict): Settings loaded from config.yaml for LLM calls.
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

    def _load_default_concept_map(self) -> Dict[str, List[str]]:
        """
        Load a default mapping of concepts to their synonyms or related terms.

        Note: The keys and values of this map should ideally be in their root forms (lemmas).

        Returns:
            Dict[str, List[str]]: A dictionary mapping concepts (lemmas) to lists of related terms (lemmas).
        """
        return {
            "light": ["brightness", "illumination", "glow", "radiance"],
            "darkness": ["shadow", "gloom", "obscurity", "dimness", "dark"], 
            "sound": ["noise", "volume", "audio", "acoustics", "noisy"], 
            "silence": ["quiet", "hush", "stillness", "calm", "silent"], 
            "temperature": ["heat", "cold", "warmth", "chill"],
        }

    def _load_llm_config(self, config_path: str) -> Dict:
        """
        Loads LLM configuration from a YAML file.

        Looks for an 'llm_settings' section in the YAML file.

        Args:
            config_path: The path to the configuration file.

        Returns:
            Dict: A dictionary containing LLM settings. Returns default settings if file is not found or parsing fails.
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

    def extract_concepts(self, text: str, hypergraph: Optional[Hypergraph] = None, normalize: bool = True) -> Dict[str, float]:
        """
        Extract concepts and their numerical values from text data using spaCy and TF-IDF.
        Optionally adds detected concepts (lemmas) to a provided Hypergraph with their scores as initial state.

        Args:
            text (str): The input text data.
            hypergraph (Optional[Hypergraph]): The Hypergraph instance to add concepts to. Defaults to None.
            normalize (bool): Whether to normalize the values to a range of [0, 1]. Defaults to True.

        Returns:
            Dict[str, float]: A dictionary of concepts (lemmas) and their associated numerical values.
        """
        if not text:
            return {}

        # Step 1: Preprocess the text and get tokens as lemmas
        doc = self.nlp(text)
        tokens_lemma = [token.lemma_.lower() for token in doc if not token.is_stop and token.is_alpha]

        # Step 2: Calculate TF-IDF scores for the text using lemmas
        if not tokens_lemma:
            return {}

        try:
            self.vectorizer.fit([" ".join(tokens_lemma)])
            tfidf_matrix = self.vectorizer.transform([" ".join(tokens_lemma)])
            feature_names = self.vectorizer.get_feature_names_out()
            tfidf_scores = dict(zip(feature_names, tfidf_matrix.toarray()[0]))
        except ValueError: # Handle empty vocabulary case
             return {}

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

        # Step 5: Add/ensure concepts (lemmas) in the hypergraph if provided
        if hypergraph is not None and isinstance(hypergraph, Hypergraph):
            for concept_lemma, score in concept_scores.items():
                # Check if concept already exists by name (lemma)
                existing_concept = None
                # Iterate through concepts in the hypergraph and compare names (lemmas)
                for existing_c in hypergraph.concepts.values():
                    if existing_c.name.lower() == concept_lemma.lower(): # Ensure case-insensitive check
                        existing_concept = existing_c
                        break
                        
                if not existing_concept:
                    # Add new concept to hypergraph with initial state from score
                    new_concept_id = f"concept_{uuid4().hex}"
                    new_concept = Concept(concept_id=new_concept_id, name=concept_lemma.lower(), initial_state=score) # Use lemma as concept name
                    hypergraph.add_concept(new_concept)
                    # print(f"Added concept from TF-IDF to hypergraph: {new_concept.name} (State: {new_concept.state})") # Optional logging
                # Else: Concept already exists, for this method we don't update state based on single text score

        return dict(concept_scores)

    def extract_concepts_and_graph_llm(self, text: str, hypergraph: Hypergraph):
        """
        Detects concepts and relationships in text using an LLM based on configured settings
        and adds them to the provided hypergraph.

        Concepts are added as nodes and relationships as events connecting concepts, using their root forms (lemmas).

        Args:
            text: The input text to process.
            hypergraph: The Hypergraph instance to add concepts and events to.
        """
        if not text or not isinstance(hypergraph, Hypergraph):
            print("Warning: Invalid input text or hypergraph object.")
            return

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
                 return # Exit the function if JSON is invalid

            concepts_list = data.get("concepts", [])
            relationships_list = data.get("relationships", [])

            # Add concepts to the hypergraph, using lemmas
            for concept_name in concepts_list:
                concept_lemma = self._get_lemma(concept_name) # Get lemma of LLM concept name

                # Check if concept already exists in the hypergraph by name (lemma)
                existing_concept = None
                for existing_c in hypergraph.concepts.values():
                    if existing_c.name.lower() == concept_lemma.lower(): # Ensure case-insensitive check
                        existing_concept = existing_c
                        break

                if not existing_concept:
                    # Create a new concept if it doesn't exist, using the lemma as the name
                    new_concept_id = f"concept_{uuid4().hex}"
                    new_concept = Concept(concept_id=new_concept_id, name=concept_lemma, initial_state=0.0) 
                    hypergraph.add_concept(new_concept)
                    # print(f"Added new concept from LLM to hypergraph: {new_concept.name}") # Optional logging
                # Else: Concept already exists, use it for relationships

            # Add relationships as events to the hypergraph, using lemmas to find concepts
            for relation in relationships_list:
                if len(relation) == 2:
                    concept_a_name, concept_b_name = relation
                    concept_a_lemma = self._get_lemma(concept_a_name) # Get lemma
                    concept_b_lemma = self._get_lemma(concept_b_name) # Get lemma

                    # Find the corresponding Concept objects in the hypergraph by lemma (name)
                    concept_a_obj = None
                    concept_b_obj = None

                    # Search through the hypergraph's concepts
                    for concept_obj in hypergraph.concepts.values():
                        if concept_obj.name.lower() == concept_a_lemma.lower(): # Check against lemma
                            concept_a_obj = concept_obj
                        if concept_obj.name.lower() == concept_b_lemma.lower(): # Check against lemma
                            concept_b_obj = concept_obj
                        if concept_a_obj and concept_b_obj:
                            break # Found both, can stop searching

                    if concept_a_obj and concept_b_obj:
                        # Create an event representing the relationship
                        event_id = f"event_{uuid4().hex}"
                        # An event needs a set of concepts it involves
                        involved_concepts = {concept_a_obj, concept_b_obj}
                        # Delta can be 0 or a small value; reason indicates origin
                        relationship_event = Event(
                            event_id=event_id,
                            timestamp=datetime.now(),
                            concepts=involved_concepts,
                            delta=0.0, # No state change implied by just a relationship
                            metadata={"source": "LLM_concept_extraction", "relationship": f"{concept_a_lemma} <-> {concept_b_lemma}"}
                        )
                        # Check if a similar event already exists between these two concepts based on their lemmas
                        event_exists = False
                        for concept_obj in involved_concepts:
                            for existing_event in concept_obj.events:
                                # Check if the set of concepts in the existing event (based on lemmas) matches the current pair
                                existing_event_concept_lemmas = {c.name.lower() for c in existing_event.concepts}
                                current_concept_lemmas = {c.name.lower() for c in involved_concepts}
                                if existing_event_concept_lemmas == current_concept_lemmas:
                                     event_exists = True
                                     break
                            if event_exists:
                                break # No need to check further if duplicate found

                        if not event_exists:
                             hypergraph.add_event(relationship_event)
                             # print(f"Added event to hypergraph between {concept_a_lemma} and {concept_b_lemma}") # Optional logging
                        # else:
                             # print(f"Skipping duplicate event between {concept_a_lemma} and {concept_b_lemma}") # Optional logging

                    else:
                        # This case should be less likely now that we add all LLM concepts first and use lemmas for lookup
                        print(f"Warning: Could not find concepts (lemmas) for relationship {[concept_a_lemma, concept_b_lemma]} in hypergraph. Skipping event creation.")

        except Exception as e:
            print(f"Error during LLM call or hypergraph update: {e}")


    def update_concept_map(self, concept: str, synonyms: List[str]):
        """
        Update the concept map with new synonyms or related terms for a concept.
        This is used by the default extract_concepts method.

        Args:
            concept (str): The concept (will be lemmatized) to update.
            synonyms (List[str]): A list of synonyms or related terms (will be lemmatized) for the concept.
        """
        concept_lemma = self._get_lemma(concept)
        synonyms_lemmas = [self._get_lemma(s) for s in synonyms]
        self.concept_map[concept_lemma] = synonyms_lemmas

    def detect_phase_shifts(self, text1: str, text2: str, hypergraph: Optional[Hypergraph] = None, delta_threshold: float = 0.1) -> List[Tuple[str, float]]:
        """
        Detect phase shifts (significant changes) in concepts between two pieces of text
        using the default spaCy/TF-IDF based concept extraction.
        Optionally adds corresponding Events to a provided Hypergraph for detected shifts.

        Concepts involved in phase shifts are added to the hypergraph if they don't exist
        (via the internal call to `extract_concepts`). An Event is created for each concept
        exceeding the delta threshold, representing the change.
        Concepts and deltas in the returned list are based on concept lemmas.

        Args:
            text1 (str): The first text for comparison.
            text2 (str): The second text for comparison.
            hypergraph (Optional[Hypergraph]): The Hypergraph instance to add phase shift Events to. Defaults to None.
            delta_threshold (float): The minimum change in concept score to consider a phase shift. Defaults to 0.1.

        Returns:
            List[Tuple[str, float]]: A list of tuples containing the concept lemma and the magnitude of change (delta).
            The delta is directional (score2 - score1) when a hypergraph is provided, otherwise absolute.
        """
        # Use extract_concepts to get scores for both texts. Pass hypergraph to ensure concepts (lemmas) are added.
        concepts1 = self.extract_concepts(text1, hypergraph=hypergraph, normalize=True)
        concepts2 = self.extract_concepts(text2, hypergraph=hypergraph, normalize=True)

        phase_shifts_data = []
        all_concepts_lemmas = set(concepts1.keys()).union(set(concepts2.keys()))
        
        # Process and add phase shift events if hypergraph is provided
        if hypergraph is not None and isinstance(hypergraph, Hypergraph):
            for concept_lemma in all_concepts_lemmas:
                score1 = concepts1.get(concept_lemma, 0.0)
                score2 = concepts2.get(concept_lemma, 0.0)
                delta = score2 - score1 # Use directional delta for events and returned data when hypergraph is used

                # Find the concept in the hypergraph (should exist after calling extract_concepts) by lemma (name)
                existing_concept = None
                for existing_c in hypergraph.concepts.values():
                    if existing_c.name.lower() == concept_lemma.lower(): # Check against lemma
                        existing_concept = existing_c
                        break
                
                if existing_concept and abs(delta) > delta_threshold:  # Check against the threshold
                    # Append directional delta to the returned list
                    phase_shifts_data.append((concept_lemma, delta))

                    # Create an event for the phase shift
                    event_id = f"event_{uuid4().hex}"
                    # The event involves the concept that changed
                    involved_concepts = {existing_concept}
                    # The delta of the event represents the change in the concept's state/score
                    phase_shift_event = Event(
                        event_id=event_id,
                        timestamp=datetime.now(),
                        concepts=involved_concepts,
                        delta=delta, 
                        metadata={
                            "source": "TFIDF_phase_shift_detection", 
                            "concept_lemma": concept_lemma, # Store lemma in metadata
                            "delta_magnitude": abs(delta),
                            "text1_score": score1,
                            "text2_score": score2
                        }
                    )
                    hypergraph.add_event(phase_shift_event)
                    # print(f"Added phase shift event for {concept_lemma} with delta {delta}") # Optional logging

        else: # If no hypergraph is provided, just return the phase shifts data as before (absolute delta)
             for concept_lemma in all_concepts_lemmas:
                score1 = concepts1.get(concept_lemma, 0.0)
                score2 = concepts2.get(concept_lemma, 0.0)
                delta = abs(score1 - score2) # Return absolute delta for backward compatibility
                if delta > delta_threshold:  # Check against the threshold
                    phase_shifts_data.append((concept_lemma, delta))

        return phase_shifts_data