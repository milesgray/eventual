from dataclasses import dataclass
from .extractor import DataExtractor, Event, Relation

@dataclass
class IntegratedEvent:
    id: str
    labels: dict[str, str]  # Language -> Label
    descriptions: dict[str, str]  # Language -> Description
    sources: list[str]  # list of sources (e.g., Wikipedia, Wikidata)

@dataclass
class IntegratedRelation:
    subject_id: str
    predicate: str
    object_id: str
    sources: list[str]  # list of sources

class DataIntegrator:
    def __init__(self, languages: list[str]):
        self.languages = languages
        self.events: dict[str, IntegratedEvent] = {}  # Event ID -> IntegratedEvent
        self.relations: list[IntegratedRelation] = []

    def integrate_events(self, events: list['Event']):
        """
        Integrate events from multiple sources.
        """
        for event in events:
            if event.id not in self.events:
                # Create a new integrated event
                self.events[event.id] = IntegratedEvent(
                    id=event.id,
                    labels={event.source: event.label},
                    descriptions={event.source: event.description},
                    sources=[event.source]
                )
            else:
                # Merge with existing event
                integrated_event = self.events[event.id]
                integrated_event.labels[event.source] = event.label
                integrated_event.descriptions[event.source] = event.description
                if event.source not in integrated_event.sources:
                    integrated_event.sources.append(event.source)

    def integrate_relations(self, relations: list['Relation']):
        """
        Integrate relations from multiple sources.
        """
        for relation in relations:
            # Check if the relation already exists
            existing_relation = next(
                (r for r in self.relations if
                 r.subject_id == relation.subject_id and
                 r.predicate == relation.predicate and
                 r.object_id == relation.object_id),
                None
            )
            if existing_relation:
                # Add the source to the existing relation
                if relation.source not in existing_relation.sources:
                    existing_relation.sources.append(relation.source)
            else:
                # Create a new integrated relation
                self.relations.append(IntegratedRelation(
                    subject_id=relation.subject_id,
                    predicate=relation.predicate,
                    object_id=relation.object_id,
                    sources=[relation.source]
                ))

    def resolve_conflicts(self):
        """
        Resolve conflicts in event labels and descriptions.
        For example, prefer Wikidata labels over Wikipedia labels.
        """
        for event in self.events.values():
            # Prefer Wikidata labels if available
            if "Wikidata" in event.labels:
                preferred_label = event.labels["Wikidata"]
                event.labels = {"preferred": preferred_label}
            # Prefer Wikidata descriptions if available
            if "Wikidata" in event.descriptions:
                preferred_description = event.descriptions["Wikidata"]
                event.descriptions = {"preferred": preferred_description}

    def run(self):
        """
        Run the integration process.
        """
        print("Integrating data...")
        # Example: Integrate events from multiple sources
        self.integrate_events(DataExtractor.extract_events_from_wikipedia(self.languages))
        self.integrate_events(DataExtractor.extract_events_from_wikidata(self.languages))
        self.integrate_events(DataExtractor.extract_events_from_dbpedia(self.languages))
        self.integrate_events(DataExtractor.extract_events_from_yago(self.languages))

        # Example: Integrate relations from Wikidata
        self.integrate_relations(DataExtractor.extract_relations_from_wikidata())

        # Resolve conflicts
        self.resolve_conflicts()

        print("Integration complete.")