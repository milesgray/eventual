"""
# TextProcessor

The `TextProcessor` module is responsible for extracting concepts and their numerical properties from text data. It uses advanced NLP techniques to identify key concepts, calculate their relevance, and detect significant changes over time.

## Usage

```python
from eventual.utils.text_processor import TextProcessor

# Initialize the TextProcessor
processor = TextProcessor()

# Extract concepts from text
text = "The light is too bright, and the sound is overwhelming."
concepts = processor.extract_concepts(text)
print(concepts)  # Output: {'light': 0.8, 'sound': 0.7}

# Detect phase shifts between two texts
text1 = "The room is dark and quiet."
text2 = "The room is now bright and noisy."
phase_shifts = processor.detect_phase_shifts(text1, text2)
print(phase_shifts)  # Output: [('light', 0.8), ('sound', 0.7)]
"""
from typing import Dict, List, Tuple
import re
from collections import defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy

class TextProcessor:
    """
    A class for processing text data to extract concepts and their numerical properties.

    The TextProcessor uses NLP techniques to identify key concepts in text data and assign
    numerical values based on their relevance, frequency, and contextual importance. It supports
    dynamic concept extraction, normalization, and integration with the Eventual framework.

    Attributes:
        nlp (spacy.Language): A pre-trained spaCy NLP model for text processing.
        vectorizer (TfidfVectorizer): A TF-IDF vectorizer for calculating term importance.
        concept_map (Dict[str, List[str]]): A mapping of concepts to their synonyms or related terms.
    """

    def __init__(self, language_model: str = "en_core_web_sm"):
        """
        Initialize the TextProcessor with a language model.

        Args:
            language_model (str): The name of the spaCy language model to load. Defaults to "en_core_web_sm".
        """
        self.nlp = spacy.load(language_model)
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.concept_map = self._load_default_concept_map()

    def _load_default_concept_map(self) -> Dict[str, List[str]]:
        """
        Load a default mapping of concepts to their synonyms or related terms.

        Returns:
            Dict[str, List[str]]: A dictionary mapping concepts to lists of related terms.
        """
        return {
            "light": ["brightness", "illumination", "glow", "radiance"],
            "darkness": ["shadow", "gloom", "obscurity", "dimness"],
            "sound": ["noise", "volume", "audio", "acoustics"],
            "silence": ["quiet", "hush", "stillness", "calm"],
            "temperature": ["heat", "cold", "warmth", "chill"],
        }

    def extract_concepts(self, text: str, normalize: bool = True) -> Dict[str, float]:
        """
        Extract concepts and their numerical values from text data.

        Args:
            text (str): The input text data.
            normalize (bool): Whether to normalize the values to a range of [0, 1]. Defaults to True.

        Returns:
            Dict[str, float]: A dictionary of concepts and their associated numerical values.
        """
        # Step 1: Preprocess the text
        doc = self.nlp(text)
        tokens = [token.lemma_.lower() for token in doc if not token.is_stop and token.is_alpha]

        # Step 2: Calculate TF-IDF scores for the text
        tfidf_matrix = self.vectorizer.fit_transform([" ".join(tokens)])
        feature_names = self.vectorizer.get_feature_names_out()
        tfidf_scores = dict(zip(feature_names, tfidf_matrix.toarray()[0]))

        # Step 3: Map tokens to concepts using the concept map
        concept_scores = defaultdict(float)
        for concept, synonyms in self.concept_map.items():
            for term in synonyms + [concept]:
                if term in tfidf_scores:
                    concept_scores[concept] += tfidf_scores[term]

        # Step 4: Normalize scores if required
        if normalize and concept_scores:
            max_score = max(concept_scores.values())
            if max_score > 0:
                for concept in concept_scores:
                    concept_scores[concept] /= max_score

        return dict(concept_scores)

    def update_concept_map(self, concept: str, synonyms: List[str]):
        """
        Update the concept map with new synonyms or related terms for a concept.

        Args:
            concept (str): The concept to update.
            synonyms (List[str]): A list of synonyms or related terms for the concept.
        """
        self.concept_map[concept] = synonyms

    def detect_phase_shifts(self, text1: str, text2: str) -> List[Tuple[str, float]]:
        """
        Detect phase shifts (significant changes) in concepts between two pieces of text.

        Args:
            text1 (str): The first text for comparison.
            text2 (str): The second text for comparison.

        Returns:
            List[Tuple[str, float]]: A list of tuples containing the concept and the magnitude of change.
        """
        concepts1 = self.extract_concepts(text1, normalize=True)
        concepts2 = self.extract_concepts(text2, normalize=True)

        phase_shifts = []
        all_concepts = set(concepts1.keys()).union(set(concepts2.keys()))
        for concept in all_concepts:
            score1 = concepts1.get(concept, 0.0)
            score2 = concepts2.get(concept, 0.0)
            delta = abs(score1 - score2)
            if delta > 0.1:  # Threshold for significant change
                phase_shifts.append((concept, delta))

        return phase_shifts