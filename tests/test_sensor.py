import pytest
from datetime import datetime
from eventual.core.sensor import TextSensor, NumericalSensor, CompositeSensor

def test_text_sensor():
    sensor = TextSensor("text_sensor_1")
    reading = sensor.read_data("The light is too bright.")
    assert "light" in [concept.name for concept in reading.extracted_concepts]
    assert sensor.last_reading_timestamp is not None


def test_numerical_sensor():
    sensor = NumericalSensor("light_sensor_1", "light", units="lux")
    reading = sensor.read_data(0.7)
    assert "value" in reading
    assert reading["value"] == 0.7
    assert sensor.last_reading_timestamp is not None


def test_composite_sensor():
    text_sensor = TextSensor("text_sensor_1")
    light_sensor = NumericalSensor("light_sensor_1", "light", units="lux")
    composite_sensor = CompositeSensor("composite_sensor_1", {
        "text": text_sensor,
        "light": light_sensor
    })
    text_sensor.read_data("The light is too bright.")
    light_sensor.read_data(0.7)
    reading = composite_sensor.read_data()
    assert "readings" in reading
    assert "text" in reading["readings"]
    assert "light" in reading["readings"]
    assert composite_sensor.last_reading_timestamp is not None