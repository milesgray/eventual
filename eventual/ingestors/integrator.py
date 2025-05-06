from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

# Use TYPE_CHECKING to avoid circular dependencies if Hypergraph imports Integrator later
if TYPE_CHECKING:
    from eventual.core.hypergraph import Hypergraph
    from eventual.processors.processor_output import ProcessorOutput

class BaseIntegrator(ABC):
    """
    Base class for all Integrators.

    Integrators are responsible for taking structured data produced by Processors
    and integrating it into a Hypergraph or other data store.
    """

    @abstractmethod
    def integrate(self, processor_output: "ProcessorOutput", hypergraph: "Hypergraph") -> None:
        """
        Integrates the data from a ProcessorOutput into the given Hypergraph.

        Args:
            processor_output (ProcessorOutput): The structured data output from a processor.
            hypergraph (Hypergraph): The Hypergraph instance to integrate data into.
        """
        pass

    # Could potentially add other abstract methods here for different types of integration,
    # e.g., integrate_concepts, integrate_events, etc., if needed.
