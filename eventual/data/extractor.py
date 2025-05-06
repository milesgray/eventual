import requests
import pandas as pd
from dataclasses import dataclass

@dataclass
class Event:
    id: str
    label: str
    description: str
    source: str

@dataclass
class Relation:
    subject_id: str
    predicate: str
    object_id: str

class DataExtractor:
    @staticmethod
    def extract_events_from_wikipedia(languages: list[str]) -> list[Event]:
        """
        Extract events from Wikipedia for the given languages.
        """
        events = []
        for lang in languages:
            # Example: Fetch events from Wikipedia API
            url = f"https://{lang}.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "list": "categorymembers",
                "cmtitle": "Category:Events",
                "cmlimit": 10,  # Limit for demonstration
                "format": "json"
            }
            response = requests.get(url, params=params).json()
            for page in response.get("query", {}).get("categorymembers", []):
                event = Event(
                    id=page["pageid"],
                    label=page["title"],
                    description=f"Event from Wikipedia ({lang})",
                    source="Wikipedia"
                )
                events.append(event)
        return events

    @staticmethod
    def extract_events_from_wikidata(languages: list[str]) -> list[Event]:
        """
        Extract events from Wikidata for the given languages.
        """
        events = []
        # Example: Query Wikidata for events
        query = """
        SELECT ?event ?eventLabel WHERE {
          ?event wdt:P31/wdt:P279* wd:Q1190554.  # Events
          SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
        }
        LIMIT 10
        """
        url = "https://query.wikidata.org/sparql"
        headers = {"Accept": "application/json"}
        response = requests.get(url, headers=headers, params={"query": query}).json()
        for result in response.get("results", {}).get("bindings", []):
            event = Event(
                id=result["event"]["value"].split("/")[-1],
                label=result["eventLabel"]["value"],
                description="Event from Wikidata",
                source="Wikidata"
            )
            events.append(event)
        return events

    @staticmethod
    def extract_events_from_dbpedia(languages: list[str]) -> list[Event]:
        """
        Extract events from DBpedia for the given languages.
        """
        events = []
        for lang in languages:
            # Example: Query DBpedia for events
            query = """
            SELECT ?event ?label WHERE {
              ?event a dbo:Event.
              ?event rdfs:label ?label.
              FILTER(LANG(?label) = "%s")
            }
            LIMIT 10
            """ % lang
            url = f"http://{lang}.dbpedia.org/sparql"
            headers = {"Accept": "application/json"}
            response = requests.get(url, headers=headers, params={"query": query}).json()
            for result in response.get("results", {}).get("bindings", []):
                event = Event(
                    id=result["event"]["value"].split("/")[-1],
                    label=result["label"]["value"],
                    description="Event from DBpedia",
                    source="DBpedia"
                )
                events.append(event)
        return events

    @staticmethod
    def extract_events_from_yago(languages: list[str]) -> list[Event]:
        """
        Extract events from YAGO for the given languages.
        """
        events = []
        # Example: Query YAGO for events (hypothetical API)
        url = "https://yago-knowledge.org/api/events"
        response = requests.get(url).json()
        for event_data in response.get("events", []):
            event = Event(
                id=event_data["id"],
                label=event_data["label"],
                description="Event from YAGO",
                source="YAGO"
            )
            events.append(event)
        return events

    @staticmethod
    def extract_relations_from_wikidata() -> list[Relation]:
        """
        Extract relations between entities from Wikidata.
        """
        relations = []
        # Example: Query Wikidata for relations
        query = """
        SELECT ?subject ?predicate ?object WHERE {
          ?subject ?predicate ?object.
          FILTER(STRSTARTS(STR(?predicate), "http://www.wikidata.org/prop/direct/"))
        }
        LIMIT 10
        """
        url = "https://query.wikidata.org/sparql"
        headers = {"Accept": "application/json"}
        response = requests.get(url, headers=headers, params={"query": query}).json()
        for result in response.get("results", {}).get("bindings", []):
            relation = Relation(
                subject_id=result["subject"]["value"].split("/")[-1],
                predicate=result["predicate"]["value"].split("/")[-1],
                object_id=result["object"]["value"].split("/")[-1]
            )
            relations.append(relation)
        return relations