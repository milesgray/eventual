## Refactoring Roadmap

This roadmap outlines the steps to transition from the current architecture to the proposed one. It's phased to allow for incremental development and testing.

**Phase 1: Strengthen the Core (Hypergraph)**

*   **Task 1.1: Enhance `Hypergraph` Lookup:**
    *   *Goal:* Add efficient `get_concept_by_name` and `get_concept_by_id` methods to `eventual/core/hypergraph.py`.
    *   *Details:* Modify internal storage (e.g., use dictionaries `{id: concept}` and `{name: id}`).
    *   *Tests:* Write unit tests for the new lookup methods, covering found and not-found cases.
*   **Task 1.2: Implement `add_concept_if_not_exists` in `Hypergraph`:**
    *   *Goal:* Create a method in `Hypergraph` that checks for a concept by name/ID and adds it only if it doesn't exist, returning the existing or newly added concept.
    *   *Details:* This encapsulates the common "check then add" pattern.
    *   *Tests:* Write unit tests for this method, ensuring it handles both cases (concept exists, concept doesn't exist) correctly.
*   **Task 1.3: Add `add_event` Method to `Hypergraph`:**
    *   *Goal:* Ensure a clean method exists to add events to the hypergraph.
    *   *Details:* This method should handle linking the event to relevant concepts internally.
    *   *Tests:* Write unit tests for adding events.

**Phase 2: Decouple Processors from Hypergraph**

*   **Task 2.1: Define Processor Output Structure:**
    *   *Goal:* Define standardized data structures (e.g., dataclasses or simple dictionaries) for the output of processors, detailing extracted concepts and relationships.
    *   *Details:* This structure should contain all information needed by an Integrator to update the Hypergraph.
*   **Task 2.2: Refactor `TextProcessor` Output:**
    *   *Goal:* Modify the `process` method in `eventual/utils/text_processor.py` to return the extracted information using the structure defined in Task 2.1, *without* modifying the `Hypergraph`.
    *   *Details:* Remove the code that directly interacts with `hypergraph.concepts.values()` and `hypergraph.add_concept`.
    *   *Tests:* Update/add unit tests for `TextProcessor` to assert its output structure and content are correct based on input text.

**Phase 3: Introduce and Refactor Integrators**

*   **Task 3.1: Create `Integrator` Base Class/Interface:**
    *   *Goal:* Define a base class or interface for Integrators in `eventual/data/integrator.py` (or a new `eventual.ingestors` module).
    *   *Details:* This interface should define a method like `integrate(processed_data_batch, hypergraph)`.
*   **Task 3.2: Implement `HypergraphIntegrator`:**
    *   *Goal:* Create a concrete `Integrator` class responsible for updating the `Hypergraph` based on the output of Processors.
    *   *Details:* This class will take the Processor output structure (from Task 2.1) and use the enhanced `Hypergraph` methods (from Phase 1) to add/update concepts and events.
    *   *Tests:* Write unit tests for `HypergraphIntegrator`, ensuring it correctly translates processed data into Hypergraph updates.

**Phase 4: Update Pipeline and Data Flow**

*   **Task 4.1: Refactor `Pipeline` Orchestration:**
    *   *Goal:* Modify `eventual/pipeline.py` to connect Processors and Integrators according to the new architecture.
    *   *Details:* The pipeline will now pass the `Hypergraph` instance to the `Integrator` (or the Integrator could hold a reference) and pass Processor outputs to the Integrator.
    *   *Tests:* Update pipeline integration tests to reflect the new data flow.

**Phase 5: Review and Refactor Other Components**

*   **Task 5.1: Review and Update Other Core/Data Components:**
    *   *Goal:* Examine files like `concept_detector.py`, `sensor.py`, `extractor.py`, `integrator.py` (if not fully refactored in Phase 3), etc.
    *   *Details:* Ensure they adhere to the principles of encapsulation and single responsibility. Update their interaction with the `Hypergraph` to use the new interface.
    *   *Tests:* Add/update unit tests for these components.
*   **Task 5.2: Review and Update Stream Components:**
    *   *Goal:* Examine files in `eventual/streams/`.
    *   *Details:* Ensure they interact with the `Hypergraph` via its public interface or potentially subscribe to events (if Phase 6 is undertaken).
    *   *Tests:* Add/update unit tests for stream components.

**Phase 6: Optional Event Bus Integration (for advanced decoupling/scalability)**

*   **Task 6.1: Introduce Event Bus Mechanism:**
    *   *Goal:* Implement a simple in-memory event bus or integrate a library.
    *   *Details:* Define event classes (e.g., `ConceptExtractedEvent`, `RelationshipFoundEvent`).
*   **Task 6.2: Modify Processors to Publish Events:**
    *   *Goal:* Change Processors to publish events to the bus instead of returning data structures directly.
    *   *Details:* Processors will need access to the event bus instance.
*   **Task 6.3: Modify Integrators and Streams to Subscribe:**
    *   *Goal:* Change Integrators and Streams to subscribe to relevant events on the bus.
    *   *Details:* Integrators update the `Hypergraph` when they receive events. Streams update their state or emit data when receiving events.
*   **Task 6.4: Update Pipeline to Manage Event Bus:**
    *   *Goal:* The Pipeline becomes responsible for setting up the event bus and registering subscribers.

**Phase 7: Comprehensive Testing and Documentation**

*   **Task 7.1: Full System Integration Testing:**
    *   *Goal:* Run end-to-end tests covering various data flows and use cases.
*   **Task 7.2: Performance Profiling:**
    *   *Goal:* Identify and address any performance bottlenecks introduced or highlighted by the refactoring.
*   **Task 7.3: Update Documentation (Memory Bank):**
    *   *Goal:* Update `.Gemini/core/systemPatterns.md` to describe the new architecture, component roles, and data flow.
    *   *Goal:* Update `.Gemini/core/progress.md` to reflect the completion of the refactoring.