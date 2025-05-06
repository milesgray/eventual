from typing import TYPE_CHECKING, List, Optional
from uuid import uuid4
from datetime import datetime

from eventual.ingestors.integrator import BaseIntegrator

# Use TYPE_CHECKING to avoid circular dependencies
if TYPE_CHECKING:
    from eventual.core.hypergraph import Hypergraph
    from eventual.core.concept import Concept
    from eventual.core.event import Event
    from eventual.processors.processor_output import ProcessorOutput, ExtractedConcept, ExtractedEvent

# Import concrete Concept and Event for instantiation
from eventual.core.concept import Concept # type: ignore
from eventual.core.event import Event # type: ignore

class HypergraphIntegrator(BaseIntegrator):
    """
    An Integrator specifically designed to integrate data into a Hypergraph.
    """

    def integrate(self, processor_output: "ProcessorOutput", hypergraph: "Hypergraph") -> None:
        """
        Integrates the data from a ProcessorOutput into the given Hypergraph.

        This involves adding concepts and events/relationships extracted by a processor.

        Args:
            processor_output (ProcessorOutput): The structured data output from a processor.
            hypergraph (Hypergraph): The Hypergraph instance to integrate data into.
        """
        print(f"Integrating data: {len(processor_output.extracted_concepts)} concepts, {len(processor_output.extracted_events)} events.")

        # 1. Integrate Concepts
        # Add all extracted concepts to the hypergraph first, ensuring uniqueness.
        # This is important so that events can refer to these concepts.
        integrated_concepts: List[Concept] = []
        for ext_concept in processor_output.extracted_concepts:
            # Use add_concept_if_not_exists to handle potential duplicates by name or ID
            # Assign a temporary ID if not provided in the extracted concept, Hypergraph will handle actual ID if new
            concept_to_add = Concept(
                concept_id=ext_concept.concept_id if ext_concept.concept_id else f"concept_{uuid4().hex}",
                name=ext_concept.name,
                initial_state=ext_concept.initial_state, # Use initial_state from extracted data
                properties=ext_concept.properties # Include any extracted properties
            )
            try:
                # add_concept_if_not_exists returns the existing or newly added concept
                integrated_concept = hypergraph.add_concept_if_not_exists(concept_to_add)
                integrated_concepts.append(integrated_concept) # Keep track of concepts that are definitely in the hypergraph
                # print(f"Integrated concept: {integrated_concept.name} (ID: {integrated_concept.concept_id})") # Optional logging
            except ValueError as e:
                 # This might happen if a concept with the same ID or name but different attributes exists
                 # Depending on desired behavior, this might need more sophisticated handling (e.g., merging)
                 print(f"Warning: Could not integrate concept '{ext_concept.name}' (ID: {ext_concept.concept_id}): {e}")


        # 2. Integrate Events
        # Resolve concept identifiers and create/add events
        for ext_event in processor_output.extracted_events:
            involved_concepts: List[Concept] = []
            all_concepts_found = True

            # Resolve concept identifiers to actual Concept objects in the hypergraph
            for concept_id_or_name in ext_event.concept_identifiers:
                # Try to get by ID first if it looks like a UUID, otherwise by name
                # This requires a heuristic or explicit typing in ExtractedEvent if both are possible
                # Assuming concept_identifiers are primarily names (lemmas) from TextProcessor for now
                resolved_concept = hypergraph.get_concept_by_name(concept_id_or_name)

                if resolved_concept:
                    involved_concepts.append(resolved_concept)
                else:
                    print(f"Warning: Concept '{concept_id_or_name}' for event {ext_event.event_id if ext_event.event_id else '[new event]'} not found in hypergraph. Skipping event integration.")
                    all_concepts_found = False
                    break # Cannot integrate this event if a concept is missing

            if all_concepts_found and involved_concepts:
                # Create the actual Event object
                event_to_add = Event(
                    event_id=ext_event.event_id if ext_event.event_id else f"event_{uuid4().hex}",
                    timestamp=ext_event.timestamp,
                    concepts=set(involved_concepts), # Event expects a set of Concept objects
                    delta=ext_event.delta,
                    metadata=ext_event.properties # Using properties field for metadata
                )

                try:
                    hypergraph.add_event(event_to_add)
                    # print(f"Integrated event: {event_to_add.event_id} involving {[c.name for c in involved_concepts]}") # Optional logging
                except ValueError as e:
                    print(f"Warning: Could not integrate event {event_to_add.event_id}: {e}")

        print("Integration complete.")
