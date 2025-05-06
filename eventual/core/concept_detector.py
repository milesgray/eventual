
import litellm
import os
import json
import yaml

class ConceptDetector:
    def __init__(self, config_path="eventual/config.yaml"):
        """
        Initializes the ConceptDetector with configuration from a YAML file.

        Args:
            config_path: The path to the configuration file.
        """
        self.config = self._load_config(config_path)
        self.llm_settings = self.config.get("llm_settings", {})
        if not self.llm_settings:
            print("Warning: 'llm_settings' not found in config. Using default LLM settings.")
            self.llm_settings = {
                "model": "gpt-4o", # Default model
                "temperature": 0.7,
                "top_p": 1.0,
            }

        # Ensure API keys are set up as environment variables
        # litellm picks these up automatically based on the model used.
        # e.g., export OPENAI_API_KEY='YOUR_API_KEY'

    def _load_config(self, config_path):
        """Loads configuration from a YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Error: Config file not found at {config_path}. Using default settings.")
            return {}
        except yaml.YAMLError as e:
            print(f"Error parsing config file {config_path}: {e}. Using default settings.")
            return {}

    def detect_concepts_and_build_graph(self, text: str) -> dict:
        """
        Detects concepts in text using an LLM based on configured settings
        and builds a dynamic graph.

        Args:
            text: The input text to process.

        Returns:
            A dictionary representing the concept graph, where keys are concepts
            and values are lists of related concepts. Returns an empty dictionary
            if concept detection fails or text is empty.
        """
        if not text:
            return {}

        # Define the prompt for the LLM
        # We ask the LLM to output concepts and relationships in a simple, parsable format.
        # Asking for JSON output is generally robust for parsing.
        prompt = f"""Analyze the following text and extract key concepts and their relationships.
        Please output the concepts and relationships in a JSON format.
        The JSON should have two keys: "concepts" and "relationships".
        "concepts" should be a list of strings, where each string is a key concept found in the text.
        "relationships" should be a list of lists, where each inner list contains two strings [concept_A, concept_B] indicating that concept_A is related to concept_B.
        Only include concepts and relationships that are directly mentioned or strongly implied in the text.

        Text:
        {text}

        JSON Output:
        """

        try:
            # Call the LLM using litellm with configured parameters
            response = litellm.completion(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts concepts and relationships from text."},
                    {"role": "user", "content": prompt}
                ],
                **self.llm_settings # Pass LLM parameters from config
            )

            # Extract the JSON string from the response
            response_content = response.choices[0].message.content.strip()

            # Attempt to parse the JSON output
            if response_content.startswith("```json"):
                response_content = response_content[len("```json"):].rstrip("```")

            data = json.loads(response_content)

            concepts = data.get("concepts", [])
            relationships = data.get("relationships", [])

            # Build the graph dictionary
            concept_graph = {}
            for concept in concepts:
                concept_graph[concept] = []

            for relation in relationships:
                if len(relation) == 2:
                    concept_a, concept_b = relation
                    if concept_a in concept_graph:
                        concept_graph[concept_a].append(concept_b)
                    # Optional: add bidirectional relationship
                    # if concept_b in concept_graph:
                    #     concept_graph[concept_b].append(concept_a)

            return concept_graph

        except Exception as e:
            print(f"Error during LLM call or concept extraction: {e}")
            # Return an empty graph in case of failure
            return {}

# Example Usage (for testing, not part of the class)
# if __name__ == "__main__":
#     detector = ConceptDetector()
#     sample_text = "Google released Gemini models. Gemini is a powerful AI model."
#     graph = detector.detect_concepts_and_build_graph(sample_text)
#     print(json.dumps(graph, indent=2))
