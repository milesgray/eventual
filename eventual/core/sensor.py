"""
## Sensors

The `sensor` module provides a flexible and extensible framework for handling sensory data. It includes:

- **`Sensor`**: The abstract base class for all sensors.
- **`TextSensor`**: Processes text data and extracts concepts, returning a structured output for integration.
- **`NumericalSensor`**: Handles numerical data and normalizes it.
- **`CompositeSensor`**: Combines data from multiple sensors.

### Example Usage

```python
from eventual.core.sensor import TextSensor, NumericalSensor, CompositeSensor # Updated import path
# Assuming ProcessorOutput, Hypergraph and HypergraphIntegrator are available
# from eventual.processors.processor_output import ProcessorOutput
# from eventual.core.hypergraph import Hypergraph
# from eventual.ingestors.hypergraph_integrator import HypergraphIntegrator

# Create a text sensor
text_sensor = TextSensor("text_sensor_1")

# Read text data - the sensor now returns ProcessorOutput
text_reading_output = text_sensor.read_data("The light is too bright.")
print("Text Sensor Output (ProcessorOutput):", text_reading_output)
# To integrate this into a hypergraph:
# hypergraph = Hypergraph()
# integrator = HypergraphIntegrator()
# integrator.integrate(text_reading_output, hypergraph)
# print("Hypergraph concepts after TextSensor reading:", {c.name: c.state for c in hypergraph.concepts.values()})

# Create a numerical sensor
light_sensor = NumericalSensor("light_sensor_1", "light", units="lux")
light_reading = light_sensor.read_data(0.7)
print("Numerical Sensor Reading:", light_reading)

# Create a composite sensor
# Note: CompositeSensor still returns a dict of readings from child sensors,
# this output would need a dedicated integrator or processor to convert
# to ProcessorOutput for hypergraph integration if necessary.
composite_sensor = CompositeSensor("composite_sensor_1", {
    "text": text_sensor,
    "light": light_sensor
})
# Reading composite data will call read_data on child sensors
# composite_reading = composite_sensor.read_data()
# print("Composite Sensor Reading:", composite_reading)
```
"""
from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime
from dataclasses import dataclass, field

# Import the new processor output dataclasses
from eventual.processors.processor_output import ProcessorOutput, ExtractedConcept, ExtractedEvent

# Assuming TextProcessor is available
from eventual.processors.text_processor import TextProcessor # Updated import path and name likely

class Sensor(ABC):
    """
    Abstract base class for all sensors in the Eventual framework.

    A Sensor represents a source of sensory data, which can be of any type (e.g., text, light, sound).
    Sensors are responsible for reading raw data and emitting it in a standardized format for further processing.
    """

    def __init__(self, sensor_id: str, sensor_type: str):
        """
        Initialize a Sensor.

        Args:
            sensor_id (str): A unique identifier for the sensor.
            sensor_type (str): The type of sensor (e.g., "text", "light").
        """
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        # last_reading should ideally be a standardized format, but for generic Sensor base class,
        # keeping it flexible as dict[str, any] for now.
        self.last_reading: Optional[dict[str, any]] = None
        self.last_reading_timestamp: Optional[datetime] = None

    @abstractmethod
    # Note: The return type is generalized as dict[str, any] in the base class,
    # but concrete implementations like TextSensor should return more specific types (like ProcessorOutput).
    def read_data(self, *args, **kwargs) -> dict[str, any]:
        """
        Read raw data from the sensor and return it.

        The specific arguments and return format depend on the sensor type.
        Concrete sensor implementations should override this method with appropriate type hints.

        Returns:
            dict[str, any]: A dictionary containing the sensor reading and metadata.
                            Example: {"value": 0.5, "units": "lux", "timestamp": datetime.now()}
            ProcessorOutput: (For sensors like TextSensor that perform extraction)
        """
        pass

    def get_last_reading(self) -> Optional[dict[str, any]]:
        """
        Get the most recent reading from the sensor.

        Returns:
            Optional[dict[str, any]]: The last reading, or None if no reading has been taken.
        """
        return self.last_reading

    def __repr__(self):
        return f"Sensor(sensor_id={self.sensor_id}, type={self.sensor_type}, last_reading={'...' if self.last_reading else None})"


class TextSensor(Sensor):
    """
    A sensor for processing text data.

    This sensor uses a TextProcessor to extract concepts and relationships from text input
    and returns the results as a `ProcessorOutput` object.
    """

    def __init__(self, sensor_id: str, text_processor: Optional[TextProcessor] = None):
        """
        Initialize a TextSensor.

        Args:
            sensor_id (str): A unique identifier for the sensor.
            text_processor (Optional[TextProcessor]): An optional TextProcessor instance to use.
                                                      If None, a new one will be initialized.
        """
        super().__init__(sensor_id, "text")
        # TextSensor now HAS-A TextProcessor, rather than importing and calling a function
        self._text_processor = text_processor if text_processor is not None else TextProcessor()

    def read_data(self, text: str) -> ProcessorOutput:
        """
        Process text data using the TextProcessor and return structured output.

        Args:
            text (str): The raw text input.

        Returns:
            ProcessorOutput: A structured object containing extracted concepts and events.
        """
        print(f"TextSensor '{self.sensor_id}' reading data...")
        # Use the internal TextProcessor instance
        processor_output = self._text_processor.extract_concepts(text) # Assuming extract_concepts is the primary method
        # Note: TextSensor currently only uses extract_concepts (TF-IDF). 
        # If LLM or phase shift functionality is needed via the sensor, 
        # additional methods or a different sensor design might be required.
        
        # Store a representation of the reading; ProcessorOutput is the new standardized output for this sensor
        self.last_reading = {"processor_output": processor_output}
        self.last_reading_timestamp = datetime.now()
        
        print(f"TextSensor '{self.sensor_id}' read data. Extracted {len(processor_output.extracted_concepts)} concepts, {len(processor_output.extracted_events)} events.")
        return processor_output


class NumericalSensor(Sensor):
    """
    A sensor for processing numerical data.

    This sensor handles data from sources like light sensors, temperature sensors, etc.
    It normalizes the data and associates it with a concept (concept name stored).
    It returns a dictionary with the processed numerical value and associated concept name.
    """

    def __init__(self, sensor_id: str, concept_name: str, units: str = "units"):
        """
        Initialize a NumericalSensor.

        Args:
            sensor_id (str): A unique identifier for the sensor.
            concept_name (str): The name of the concept this sensor is associated with (e.g., "light", "temperature").
            units (str): The units of measurement for the sensor data (e.g., "lux", "°C").
        """
        # Sensor type is numerical, but we also associate it with a concept name
        super().__init__(sensor_id, "numerical") 
        self.concept_name = concept_name # Store the associated concept name
        self.units = units

    def read_data(self, value: float) -> dict[str, any]:
        """
        Process numerical data and return it in a standardized format.

        Args:
            value (float): The raw numerical value from the sensor.

        Returns:
            dict[str, any]: A dictionary containing the normalized value, associated concept name, units, and metadata.
                            Example: {"concept_name": "light", "value": 0.5, "units": "lux", "timestamp": datetime.now()}
        """
        from eventual.utils.numerical_properties import normalize_value

        # Assuming normalization range [0, 1] is standard for concept state update
        normalized_value = normalize_value(value, 0, 1)  
        
        reading_data = {
            "concept_name": self.concept_name, # Include the associated concept name
            "value": normalized_value,
            "units": self.units,
            "timestamp": datetime.now()
        }

        self.last_reading = reading_data
        self.last_reading_timestamp = datetime.now()
        
        print(f"NumericalSensor '{self.sensor_id}' read data for concept '{self.concept_name}': {normalized_value} {self.units}")
        return reading_data


class CompositeSensor(Sensor):
    """
    A sensor that combines data from multiple sensors into a single reading.

    This sensor is useful for scenarios where multiple sensory inputs need to be processed together.
    It returns a dictionary mapping child sensor IDs to their readings.
    Note: The output format is a dictionary of readings, not a unified ProcessorOutput,
    as the combination logic might be sensor-specific and require further processing.
    """

    def __init__(self, sensor_id: str, child_sensors: dict[str, Sensor]):
        """
        Initialize a CompositeSensor.

        Args:
            sensor_id (str): A unique identifier for the sensor.
            child_sensors (dict[str, Sensor]): A dictionary of child sensors, keyed by their IDs.
        """
        super().__init__(sensor_id, "composite")
        self.child_sensors = child_sensors

    def read_data(self) -> dict[str, any]:
        """
        Read data from all child sensors and combine it into a single reading.

        Returns:
            dict[str, any]: A dictionary containing the combined sensor readings and metadata.
                            Example: {"readings": {"text_sensor_1": {...}, "light_sensor_1": {...}}, "timestamp": datetime.now()}
        """
        print(f"CompositeSensor '{self.sensor_id}' reading data from child sensors...")
        combined_reading = {}
        for sensor_id, sensor in self.child_sensors.items():
            # Note: This assumes child sensors' read_data methods don't require specific args,
            # or that this composite sensor can provide them if needed.
            # It also collects whatever format the child sensor returns.
            try:
                reading = sensor.read_data() # Pass any necessary args here if required by child sensors
                combined_reading[sensor_id] = reading
            except Exception as e:
                 print(f"Error reading data from child sensor '{sensor_id}': {e}")
                 combined_reading[sensor_id] = {"error": str(e)}

        reading_data = {
            "readings": combined_reading,
            "timestamp": datetime.now()
        }
        self.last_reading = reading_data
        self.last_reading_timestamp = datetime.now()
        
        print(f"CompositeSensor '{self.sensor_id}' finished reading data.")
        return reading_data

# Example Usage (for testing, not part of the class)
# if __name__ == "__main__":
#     # Example demonstrating the updated TextSensor output
#     text_sensor = TextSensor("my_text_sensor")
#     text_output = text_sensor.read_data("The quick brown fox jumps.")
#     print("Text Sensor Output:", text_output)
#     print("Extracted Concepts:", text_output.extracted_concepts)
#     print("Extracted Events:", text_output.extracted_events)

#     # Example demonstrating NumericalSensor
#     light_sensor = NumericalSensor("my_light_sensor", "light", units="lux")
#     light_output = light_sensor.read_data(0.85)
#     print("Numerical Sensor Output:", light_output)

#     # Example demonstrating CompositeSensor (requires TextProcessor config)
#     try:
#          # Ensure eventual/config.yaml exists with llm_settings if TextSensor uses LLM
#          # You might need to create a dummy config file for this example to run standalone
#          text_sensor_for_composite = TextSensor("composite_text_sensor")
#          numerical_sensor_for_composite = NumericalSensor("composite_num_sensor", "temp", units="C")
#          composite = CompositeSensor("my_composite_sensor", {
#              "text_input": text_sensor_for_composite,
#              "numerical_input": numerical_sensor_for_composite
#          })
#          # Note: To run composite.read_data(), you would need to provide inputs to the child sensors
#          # before calling read_data on the composite, or modify CompositeSensor to accept input.
#          # As is, calling composite.read_data() will call read_data on the child sensors with no args,
#          # which might not work depending on the child sensor's implementation.
#          # A better design might be composite.read_data(*inputs_for_child_sensors)
#          print("Composite Sensor initialized.")
#          # Example of how you *would* use it if read_data took input:
#          # composite_result = composite.read_data("input for text sensor", 0.5) # This doesn't work with current CompositeSensor.read_data signature
#     except Exception as e:
#          print(f"Could not run composite sensor example: {e}")
#          print("Ensure eventual/config.yaml exists and child sensors can be initialized.")

