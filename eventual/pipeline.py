"""# Eventual Pipeline

The `eventual.pipeline` module orchestrates the different stages of data processing
within the Eventual framework. It can be configured to run various steps,
from data download and extraction to integration and output generation.

Following architectural refactoring, it now also demonstrates a text processing
and hypergraph integration flow using `TextProcessor` and `HypergraphIntegrator`.

## Configuration

The pipeline's behavior is controlled by a YAML configuration file.

```yaml
# example_config.yaml

languages:
  - code: en
    name: English
  - code: de
    name: German

steps: [1, 2, 3, 5, 11] # Example steps including the new text processing step (11)

data_sources:
  wikipedia:
    name: Wikipedia
    uri: http://example.com/wikipedia_dump.xml # Replace with actual URI
# Add other sources as needed

llm_settings:
  model: "gpt-4o" # LLM model for TextProcessor (if step 11 is included)
  temperature: 0.7
# Add other LLM parameters here
```

## Usage

Run the pipeline from the command line:

```bash
python -m eventual.pipeline example_config.yaml
```

If step `11` is included in the `steps` configuration, the text processing
and hypergraph integration example flow will be executed.

## Classes

### `EventualPipeline`
The main class that orchestrates the pipeline steps.

"""
import argparse
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field
import yaml  # For configuration
import requests  # For downloading files (example)
import pandas as pd  # For data manipulation (example)
from rdflib import Graph, URIRef, Literal  # For RDF/triple output (example)

# Import the new components
from .core.hypergraph import Hypergraph
from .processors.text_processor import TextProcessor
from .ingestors.hypergraph_integrator import HypergraphIntegrator
from .processors.processor_output import ProcessorOutput, ExtractedEvent # Import ExtractedEvent for phase shifts
from .data import DataExtractor, DataIntegrator # Existing imports

# Constants
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Data Classes (Existing)
@dataclass
class Language:
    code: str
    name: str

@dataclass
class Source:
    name: str
    uri: str

@dataclass
class Config:
    languages: list[Language] = field(default_factory=list)
    steps: set[int] = field(default_factory=set)
    data_sources: dict[str, Source] = field(default_factory=dict)
    llm_settings: dict = field(default_factory=dict) # Add LLM settings to config

# Pipeline Class
class EventualPipeline:
    def __init__(self, config: Config):
        self.config = config
        self.languages = config.languages
        self.data_sources = config.data_sources
        self.llm_settings = config.llm_settings # Store LLM settings
        self.hypergraph = Hypergraph() # Initialize the Hypergraph instance

    def download_files(self):
        """Step 1: Download raw data files (Example)."""
        print("Step 1: Downloading files...")
        for source in self.data_sources.values():
            print(f"Downloading from {source.name} ({source.uri})")
            # Use requests or wget to download files
            try:
                response = requests.get(source.uri, timeout=10)
                response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
                # Ensure the 'data' directory exists
                import os
                os.makedirs("data", exist_ok=True)
                with open(f"data/{source.name}.raw", "wb") as f:
                    f.write(response.content)
                print(f"Successfully downloaded {source.name}.")
            except requests.exceptions.RequestException as e:
                print(f"Error downloading {source.name}: {e}")
            except IOError as e:
                print(f"Error writing file for {source.name}: {e}")
        print("Download complete.")

    def extract_data(self):
        """Step 2: Extract event pages and relations (Example)."""
        print("Step 2: Extracting data...")
        # This part remains from the original pipeline example
        extractors = [
            # Assuming these classes/methods exist and work with the downloaded files
            # DataExtractor.extract_events_from_wikipedia(self.languages),
            # DataExtractor.extract_events_from_wikidata(self.languages),
            # DataExtractor.extract_events_from_dbpedia(self.languages),
            # DataExtractor.extract_events_from_yago(self.languages),           
        ]
        # for extractor in extractors:
        #     extractor.run()
        print("Extraction complete.")

    def integrate_data(self):
        """Step 3: Integrate data from multiple sources (Example)."""
        print("Step 3: Integrating data...")
        # This part remains from the original pipeline example
        # Assuming DataIntegrator exists and works with the extracted data
        # integrator = DataIntegrator(self.languages)
        # integrator.run()
        # Placeholder for demonstration:
        class MockIntegrator:
            def run(self):
                print("Running mock data integration.")
        MockIntegrator().run()
        print("Integration complete.")

    def _write_entities_and_events(self):
        """Step 5: Write entities and events (Example)."""
        print(f"Step 5: Writing entities and events...")
        # Example using rdflib - adapt as needed for actual hypergraph output
        graph = Graph()
        # Add entities and events from the self.hypergraph to the graph here if desired
        # For demonstration, using placeholder:
        graph.add((URIRef("http://example.org/event1"), URIRef("http://example.org/label"), Literal("Event 1")))
        try:
            os.makedirs("output", exist_ok=True)
            graph.serialize(destination="output/entities_and_events.ttl", format="turtle")
            print("Wrote output/entities_and_events.ttl")
        except Exception as e:
            print(f"Error writing output file: {e}")

    def _write_predefined_relations(self):
         """Step 6: Write predefined relations (Example)."""
         print(f"Step 6: Writing predefined relations...")
         graph = Graph()
         graph.add((URIRef("http://example.org/event1"), URIRef("http://example.org/hasTime"), Literal("2023-10-01")))
         try:
            os.makedirs("output", exist_ok=True)
            graph.serialize(destination="output/predefined_relations.ttl", format="turtle")
            print("Wrote output/predefined_relations.ttl")
         except Exception as e:
            print(f"Error writing output file: {e}")

    def _write_event_relations(self):
        """Step 7: Write event and entity relations (Example)."""
        print(f"Step 7: Writing event and entity relations...")
        graph = Graph()
        graph.add((URIRef("http://example.org/event1"), URIRef("http://example.org/relatedTo"), URIRef("http://example.org/event2")))
        try:
            os.makedirs("output", exist_ok=True)
            graph.serialize(destination="output/event_relations.ttl", format="turtle")
            print("Wrote output/event_relations.ttl")
        except Exception as e:
            print(f"Error writing output file: {e}")

    def _write_text_events(self):
        """Step 8: Write text events (Example)."""
        print(f"Step 8: Writing text events...")
        try:
            os.makedirs("output", exist_ok=True)
            with open("output/text_events.txt", "w") as f:
                f.write("Event 1: Description of event 1.") # Replace with actual text events from hypergraph if available
            print("Wrote output/text_events.txt")
        except Exception as e:
            print(f"Error writing output file: {e}")

    def _write_links(self):
         """Step 9: Write links (Example)."""
         print(f"Step 9: Writing links...")
         try:
            os.makedirs("output", exist_ok=True)
            with open("output/links.txt", "w") as f:
                f.write("http://example.org/event1 -> http://example.org/event2") # Replace with actual links from hypergraph if available
            print("Wrote output/links.txt")
         except Exception as e:
            print(f"Error writing output file: {e}")

    def _write_comentions(self):
         """Step 10: Write co-mentions (Example)."""
         print(f"Step 10: Writing co-mentions...")
         try:
            os.makedirs("output", exist_ok=True)
            with open("output/comentions.txt", "w") as f:
                f.write("Event 1 and Event 2 are co-mentioned.") # Replace with actual co-mentions from hypergraph if available
            print("Wrote output/comentions.txt")
         except Exception as e:
            print(f"Error writing output file: {e}")

    def _run_text_processing_flow(self):
        """Step 11: Run the text processing and hypergraph integration flow."""
        print("Step 11: Running text processing and hypergraph integration...")
        # Initialize TextProcessor with LLM settings from config
        processor = TextProcessor(config_path="eventual/config.yaml") # TextProcessor loads config internally
        integrator = HypergraphIntegrator()

        # Example Text Data
        text1 = "The quick brown fox jumps over the lazy dog."
        text2 = "A fast fox is agile. The dog was very lazy."
        text_llm = "Google released Gemini models. Gemini is a powerful AI model. Google is a tech company."

        print("--- Processing Text 1 (TF-IDF) ---")
        # Process text using TF-IDF method
        processor_output_tfidf = processor.extract_concepts(text1)
        # Integrate into the hypergraph
        integrator.integrate(processor_output_tfidf, self.hypergraph)
        print(f"Hypergraph state after Text 1 processing: {self.hypergraph}")

        print("--- Processing Text 2 (TF-IDF) ---")
        # Process text using TF-IDF method
        processor_output_tfidf_2 = processor.extract_concepts(text2)
        # Integrate into the hypergraph
        integrator.integrate(processor_output_tfidf_2, self.hypergraph)
        print(f"Hypergraph state after Text 2 processing: {self.hypergraph}")

        print("--- Detecting Phase Shifts (Text 1 vs Text 2) ---")
        # Detect phase shifts, which returns ExtractedEvents
        phase_shift_events = processor.detect_phase_shifts(text1, text2, delta_threshold=0.05)
        # Create a ProcessorOutput specifically for these events for integration
        phase_shift_output = ProcessorOutput(extracted_events=phase_shift_events)
        # Integrate phase shift events
        integrator.integrate(phase_shift_output, self.hypergraph)
        print(f"Hypergraph state after Phase Shift detection: {self.hypergraph}")

        print("--- Processing Text (LLM) ---")
        # Process text using LLM method
        # Note: This requires LLM configuration and API keys to be set up correctly.
        try:
            processor_output_llm = processor.extract_concepts_and_graph_llm(text_llm)
            # Integrate into the hypergraph
            integrator.integrate(processor_output_llm, self.hypergraph)
            print(f"Hypergraph state after LLM processing: {self.hypergraph}")
        except Exception as e:
            print(f"Skipping LLM processing due to error: {e}")
            print("Please ensure litellm is configured correctly with valid API keys.")

        print("Text processing and hypergraph integration complete.")
        # Optional: Add a step here to visualize or save the final hypergraph state


    def run(self):
        """Run the pipeline based on the configured steps."""
        print(f"Running Eventual pipeline at {datetime.now().strftime(DATE_FORMAT)}")

        # Ensure output directory exists if any write step is planned
        if any(step in self.config.steps for step in range(5, 11)):
             import os
             os.makedirs("output", exist_ok=True)
             # Note: The current write_output methods are placeholders
             # and would need to be adapted to query the self.hypergraph
             # if the text processing flow (step 11) is run and you want to output its results.

        if 1 in self.config.steps:
            self.download_files()
        if 2 in self.config.steps:
            self.extract_data()
        if 3 in self.config.steps:
            self.integrate_data()

        # Run existing output steps (5-10) - currently use placeholders
        for step in range(5, 11):
            if step in self.config.steps:
                # The original write_output methods are placeholders
                # They would need to be updated to read from the hypergraph if step 11 was run
                # For now, they remain as they were.
                if hasattr(self, f'_write_step{step}'): # Check if a dedicated method exists
                     getattr(self, f'_write_step{step}')()
                else:
                    # Call the generic write_output if no specific method is defined
                    self.write_output(step)

        # Run the new text processing flow if configured
        if 11 in self.config.steps:
            self._run_text_processing_flow()

        print("Pipeline execution complete.")

# Configuration Loader
def load_config(config_file: str) -> Config:
    """
    Loads pipeline configuration from a YAML file.
    """
    try:
        with open(config_file, "r") as f:
            config_data = yaml.safe_load(f)

        languages = [Language(code=lang["code"], name=lang["name"]) for lang in config_data.get("languages", [])]
        steps = set(config_data.get("steps", []))
        data_sources = {source["name"]: Source(name=source["name"], uri=source["uri"]) for source in config_data.get("data_sources", [])}
        llm_settings = config_data.get("llm_settings", {}) # Load LLM settings

        return Config(languages=languages, steps=steps, data_sources=data_sources, llm_settings=llm_settings)

    except FileNotFoundError:
        print(f"Error: Config file not found at {config_file}")
        raise
    except yaml.YAMLError as e:
        print(f"Error parsing config file {config_file}: {e}")
        raise

# Main Function
def main():
    parser = argparse.ArgumentParser(description="Run the Eventual pipeline.")
    parser.add_argument("config_file", help="Path to the configuration file.")
    args = parser.parse_args()

    try:
        config = load_config(args.config_file)
        pipeline = EventualPipeline(config)
        pipeline.run()
    except Exception as e:
        print(f"Pipeline execution failed: {e}")

if __name__ == "__main__":
    # Example of creating a dummy config.yaml if it doesn't exist,
    # so the example usage works out of the box.
    dummy_config_path = "eventual/config.yaml"
    if not os.path.exists(dummy_config_path):
        print(f"Creating a dummy config file at {dummy_config_path}")
        dummy_config_content = """
llm_settings:
  model: "gpt-4o"
  temperature: 0.7

languages:
  - code: en
    name: English

steps: [11] # Default to running the text processing example

data_sources: {}
"""
        try:
            # Ensure the eventual directory exists before writing
            os.makedirs("eventual", exist_ok=True)
            with open(dummy_config_path, "w") as f:
                f.write(dummy_config_content)
        except Exception as e:
            print(f"Error creating dummy config file: {e}")
            # Continue execution, load_config will likely fail or use defaults

    # Example of creating a dummy config file for the pipeline itself if it doesn't exist
    # This allows running `python -m eventual.pipeline dummy_pipeline_config.yaml`
    dummy_pipeline_config_path = "dummy_pipeline_config.yaml"
    if not os.path.exists(dummy_pipeline_config_path):
        print(f"Creating a dummy pipeline config file at {dummy_pipeline_config_path}")
        dummy_pipeline_config_content = """
languages:
  - code: en
    name: English

steps: [11] # Default to running the text processing example

data_sources: {}
"""
        try:
             with open(dummy_pipeline_config_path, "w") as f:
                f.write(dummy_pipeline_config_content)
        except Exception as e:
            print(f"Error creating dummy pipeline config file: {e}")

    main()
