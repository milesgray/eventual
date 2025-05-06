"""
## Sensors

The `sensor` module provides a flexible and extensible framework for handling sensory data. It includes:

- **`Sensor`**: The abstract base class for all sensors.
- **`TextSensor`**: Processes text data and extracts concepts.
- **`NumericalSensor`**: Handles numerical data and normalizes it.
- **`CompositeSensor`**: Combines data from multiple sensors.

### Example Usage

```python
from eventual.sensor import TextSensor, NumericalSensor, CompositeSensor

# Create a text sensor
text_sensor = TextSensor("text_sensor_1")
text_reading = text_sensor.read_data("The light is too bright.")

# Create a numerical sensor
light_sensor = NumericalSensor("light_sensor_1", "light", units="lux")
light_reading = light_sensor.read_data(0.7)

# Create a composite sensor
composite_sensor = CompositeSensor("composite_sensor_1", {
    "text": text_sensor,
    "light": light_sensor
})
composite_reading = composite_sensor.read_data()
```
"""
from abc import ABC, abstractmethod
from typing import Any, Optional
from datetime import datetime

class Sensor(ABC):
    """
    Abstract base class for all sensors in the Eventual framework.

    A Sensor represents a source of sensory data, which can be of any type (e.g., text, light, sound).
    Sensors are responsible for reading raw data and emitting it in a standardized format for further processing.

    Attributes:
        sensor_id (str): A unique identifier for the sensor.
        sensor_type (str): The type of sensor (e.g., "text", "light").
        last_reading (Optional[dict[str, Any]]): The most recent reading from the sensor.
        last_reading_timestamp (Optional[datetime]): The timestamp of the last reading.
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
        self.last_reading: Optional[dict[str, Any]] = None
        self.last_reading_timestamp: Optional[datetime] = None

    @abstractmethod
    def read_data(self) -> dict[str, Any]:
        """
        Read raw data from the sensor and return it in a standardized format.

        Returns:
            dict[str, Any]: A dictionary containing the sensor reading and metadata.
                            Example: {"value": 0.5, "units": "lux", "timestamp": datetime.now()}
        """
        pass

    def get_last_reading(self) -> Optional[dict[str, Any]]:
        """
        Get the most recent reading from the sensor.

        Returns:
            Optional[dict[str, Any]]: The last reading, or None if no reading has been taken.
        """
        return self.last_reading

    def __repr__(self):
        return f"Sensor(sensor_id={self.sensor_id}, type={self.sensor_type}, last_reading={self.last_reading})"


class TextSensor(Sensor):
    """
    A sensor for processing text data.

    This sensor extracts concepts and numerical properties from text input, making it suitable
    for use in natural language processing tasks.
    """

    def __init__(self, sensor_id: str):
        super().__init__(sensor_id, "text")

    def read_data(self, text: str) -> dict[str, Any]:
        """
        Process text data and extract relevant information.

        Args:
            text (str): The raw text input.

        Returns:
            dict[str, Any]: A dictionary containing the extracted concepts and metadata.
                            Example: {"concepts": {"light": 1.0, "darkness": 0.0}, "timestamp": datetime.now()}
        """
        from eventual.utils.text_processor import extract_concepts

        concepts = extract_concepts(text)
        self.last_reading = {
            "concepts": concepts,
            "timestamp": datetime.now()
        }
        self.last_reading_timestamp = datetime.now()
        return self.last_reading


class NumericalSensor(Sensor):
    """
    A sensor for processing numerical data.

    This sensor handles data from sources like light sensors, temperature sensors, etc.
    It normalizes the data and associates it with a concept.
    """

    def __init__(self, sensor_id: str, sensor_type: str, units: str = "units"):
        """
        Initialize a NumericalSensor.

        Args:
            sensor_id (str): A unique identifier for the sensor.
            sensor_type (str): The type of sensor (e.g., "light", "temperature").
            units (str): The units of measurement for the sensor data (e.g., "lux", "°C").
        """
        super().__init__(sensor_id, sensor_type)
        self.units = units

    def read_data(self, value: float) -> dict[str, Any]:
        """
        Process numerical data and return it in a standardized format.

        Args:
            value (float): The raw numerical value from the sensor.

        Returns:
            dict[str, Any]: A dictionary containing the normalized value and metadata.
                            Example: {"value": 0.5, "units": "lux", "timestamp": datetime.now()}
        """
        from eventual.utils.numerical_properties import normalize_value

        normalized_value = normalize_value(value, 0, 1)  # Normalize to [0, 1]
        self.last_reading = {
            "value": normalized_value,
            "units": self.units,
            "timestamp": datetime.now()
        }
        self.last_reading_timestamp = datetime.now()
        return self.last_reading


class CompositeSensor(Sensor):
    """
    A sensor that combines data from multiple sensors into a single reading.

    This sensor is useful for scenarios where multiple sensory inputs need to be processed together,
    such as combining light and sound data to detect a specific event.
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

    def read_data(self) -> dict[str, Any]:
        """
        Read data from all child sensors and combine it into a single reading.

        Returns:
            dict[str, Any]: A dictionary containing the combined sensor readings and metadata.
                            Example: {"light": 0.5, "sound": 0.8, "timestamp": datetime.now()}
        """
        combined_reading = {}
        for sensor_id, sensor in self.child_sensors.items():
            reading = sensor.read_data()
            combined_reading[sensor_id] = reading
        self.last_reading = {
            "readings": combined_reading,
            "timestamp": datetime.now()
        }
        self.last_reading_timestamp = datetime.now()
        return self.last_reading