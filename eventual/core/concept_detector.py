
import litellm
import os
import json
import yaml
from typing import Optional
from eventual.processors.processor_output import ProcessorOutput, ExtractedConcept, ExtractedEvent
from datetime import datetime
from uuid import uuid4 # Assuming we might need a temp ID if the ExtractedConcept doesn't provide one

class ConceptDetector:
    """
    Detects concepts and relationships in text using an LLM.

    Following refactoring, it now returns structured data (`ProcessorOutput`)
    for integration into a Hypergraph or other data store by a separate component.
    """
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

    def detect_concepts_and_build_graph(self, text: str) -> ProcessorOutput:
        """
        Detects concepts and relationships in text using an LLM based on configured settings.
        Returns structured data representing the extracted information.

        Args:
            text: The input text to process.

        Returns:
            ProcessorOutput: An object containing the extracted concepts and events/relationships.
            Returns an empty ProcessorOutput if detection fails or text is empty.
        """
        if not text:
            return ProcessorOutput()

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

        extracted_concepts = []
        extracted_events = []

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
                # ConceptDetector doesn't assign IDs, that's for the Integrator
                extracted_concepts.append(ExtractedConcept(name=concept_name))

            # Create ExtractedEvent instances for relationships
            for relation in relationships_list:
                if len(relation) == 2:
                    concept_a_name, concept_b_name = relation
                    # ExtractedEvent refers to concepts by their names
                    involved_concept_identifiers = [concept_a_name, concept_b_name]

                    # Create an ExtractedEvent representing the relationship
                    # Event ID is assigned by the Integrator
                    relationship_event = ExtractedEvent(
                        concept_identifiers=involved_concept_identifiers,
                        timestamp=datetime.now(),
                        delta=0.0, # No state change implied by just a relationship
                        event_type='relationship',
                        properties={
                            "source": "ConceptDetector_LLM", 
                            "relationship": f"{concept_a_name} <-> {concept_b_name}" # Store original names/relation
                         }
                    )
                    extracted_events.append(relationship_event)

        except Exception as e:
            print(f"Error during LLM call or concept extraction: {e}")
            # Continue and return whatever was extracted before the error, or an empty output

        # Return ProcessorOutput
        return ProcessorOutput(extracted_concepts=extracted_concepts, extracted_events=extracted_events)

# Example Usage (for testing, not part of the class)
# if __name__ == "__main__":
#     # Need a dummy config.yaml or ensure one exists for initialization
#     # Example of creating a dummy config.yaml if it doesn't exist
#     dummy_config_path = "eventual/config.yaml"
#     if not os.path.exists(dummy_config_path):
#         print(f"Creating a dummy config file at {dummy_config_path}")
#         dummy_config_content = """
# llm_settings:
#   model: "gpt-4o"
#   temperature: 0.7
# """
#         try:
#             # Ensure the eventual directory exists before writing
#             os.makedirs("eventual", exist_ok=True)
#             with open(dummy_config_path, "w") as f:
#                 f.write(dummy_config_content)
#         except Exception as e:
#             print(f"Error creating dummy config file: {e}")

#     detector = ConceptDetector()
#     sample_text = "Google released Gemini models. Gemini is a powerful AI model."
#     processor_output = detector.detect_concepts_and_build_graph(sample_text)
#     print("Extracted Concepts:", processor_output.extracted_concepts)
#     print("Extracted Events:", processor_output.extracted_events)

#     # To integrate this output:
#     # from eventual.core.hypergraph import Hypergraph
#     # from eventual.ingestors.hypergraph_integrator import HypergraphIntegrator
#     # hypergraph = Hypergraph()
#     # integrator = HypergraphIntegrator()
#     # integrator.integrate(processor_output, hypergraph)
#     # print("Hypergraph concepts after integration:", hypergraph.concepts)
#     # print("Hypergraph events after integration:", hypergraph.events)
