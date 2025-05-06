import argparse
from datetime import datetime
from typing import List, Set, Dict
from dataclasses import dataclass
import yaml  # For configuration
import requests  # For downloading files
import pandas as pd  # For data manipulation
from rdflib import Graph, URIRef, Literal  # For RDF/triple output

from .data import DataExtractor, DataIntegrator

# Constants
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Data Classes
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
    languages: List[Language]
    steps: Set[int]
    data_sources: Dict[str, Source]

# Pipeline Class
class EventualPipeline:
    def __init__(self, config: Config):
        self.config = config
        self.languages = config.languages
        self.data_sources = config.data_sources
        self.all_event_pages_dataset = None

    def download_files(self):
        """Step 1: Download raw data files."""
        print("Step 1: Downloading files...")
        for source in self.data_sources.values():
            print(f"Downloading from {source.name} ({source.uri})")
            # Use requests or wget to download files
            response = requests.get(source.uri)
            with open(f"data/{source.name}.raw", "wb") as f:
                f.write(response.content)
        print("Download complete.")

    def extract_data(self):
        """Step 2: Extract event pages and relations."""
        print("Step 2: Extracting data...")
        extractors = [
            DataExtractor.extract_events_from_wikipedia(self.languages),
            DataExtractor.extract_events_from_wikidata(self.languages),
            DataExtractor.extract_events_from_dbpedia(self.languages),
            DataExtractor.extract_events_from_yago(self.languages),
        ]
        for extractor in extractors:
            extractor.run()
        print("Extraction complete.")

    def integrate_data(self):
        """Step 3: Integrate data from multiple sources."""
        print("Step 3: Integrating data...")
        integrator = DataIntegrator(self.languages)
        integrator.run()
        print("Integration complete.")

    def write_output(self, step: int):
        """Steps 5-10: Write output based on the step."""
        print(f"Step {step}: Writing output...")
        if step == 5:
            self._write_entities_and_events()
        elif step == 6:
            self._write_predefined_relations()
        elif step == 7:
            self._write_event_relations()
        elif step == 8:
            self._write_text_events()
        elif step == 9:
            self._write_links()
        elif step == 10:
            self._write_comentions()
        print(f"Step {step} complete.")

    def _write_entities_and_events(self):
        """Step 5: Write entities and events."""
        graph = Graph()
        # Add entities and events to the graph
        graph.add((URIRef("http://example.org/event1"), URIRef("http://example.org/label"), Literal("Event 1")))
        graph.serialize(destination="output/entities_and_events.ttl", format="turtle")

    def _write_predefined_relations(self):
        """Step 6: Write predefined relations (times, locations, etc.)."""
        graph = Graph()
        # Add predefined relations to the graph
        graph.add((URIRef("http://example.org/event1"), URIRef("http://example.org/hasTime"), Literal("2023-10-01")))
        graph.serialize(destination="output/predefined_relations.ttl", format="turtle")

    def _write_event_relations(self):
        """Step 7: Write event and entity relations."""
        graph = Graph()
        # Add event relations to the graph
        graph.add((URIRef("http://example.org/event1"), URIRef("http://example.org/relatedTo"), URIRef("http://example.org/event2")))
        graph.serialize(destination="output/event_relations.ttl", format="turtle")

    def _write_text_events(self):
        """Step 8: Write text events."""
        with open("output/text_events.txt", "w") as f:
            f.write("Event 1: Description of event 1.\n")

    def _write_links(self):
        """Step 9: Write links."""
        with open("output/links.txt", "w") as f:
            f.write("http://example.org/event1 -> http://example.org/event2\n")

    def _write_comentions(self):
        """Step 10: Write co-mentions."""
        with open("output/comentions.txt", "w") as f:
            f.write("Event 1 and Event 2 are co-mentioned.\n")

    def run(self):
        """Run the pipeline based on the configured steps."""
        print(f"Running EventKG pipeline at {datetime.now().strftime(DATE_FORMAT)}")
        if 1 in self.config.steps:
            self.download_files()
        if 2 in self.config.steps:
            self.extract_data()
        if 3 in self.config.steps:
            self.integrate_data()
        for step in range(5, 11):
            if step in self.config.steps:
                self.write_output(step)
        print("Pipeline execution complete.")

# Configuration Loader
def load_config(config_file: str) -> Config:
    with open(config_file, "r") as f:
        config_data = yaml.safe_load(f)
    languages = [Language(code=lang["code"], name=lang["name"]) for lang in config_data["languages"]]
    steps = set(config_data["steps"])
    data_sources = {source["name"]: Source(name=source["name"], uri=source["uri"]) for source in config_data["data_sources"]}
    return Config(languages=languages, steps=steps, data_sources=data_sources)

# Main Function
def main():
    parser = argparse.ArgumentParser(description="Run the Eventual pipeline.")
    parser.add_argument("config_file", help="Path to the configuration file.")
    args = parser.parse_args()

    config = load_config(args.config_file)
    pipeline = EventualPipeline(config)
    pipeline.run()

if __name__ == "__main__":
    main()