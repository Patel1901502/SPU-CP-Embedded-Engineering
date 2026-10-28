"""Hardware composition root. Injected objects are never reconfigured."""

from sensors import AnalogSensorSuite, SensorSuite, SimulatedSensorSuite
from service import UARTService


def create_service(settings, uart=None, sensors=None, led=None):
    if sensors is None:
        if settings.SENSOR_BACKEND == "tmp102":
            sensors = SensorSuite(settings=settings)
        elif settings.SENSOR_BACKEND == "simulated":
            sensors = SimulatedSensorSuite()
        elif settings.SENSOR_BACKEND == "analog":
            from machine import ADC, Pin

            adc = ADC(Pin(settings.ANALOG_TEMP_PIN))
            adc.atten(settings.ANALOG_ADC_ATTEN)
            sensors = AnalogSensorSuite(adc, settings)
        else:
            raise ValueError("Unknown SENSOR_BACKEND: " + settings.SENSOR_BACKEND)
    if uart is None:
        from machine import UART

        uart = UART(settings.UART_ID, **settings.UART_OPTIONS)
    if led is None:
        from machine import Pin

        led = Pin(settings.LED_PIN, Pin.OUT)
    return UARTService(uart, sensors, led, settings.UART_MAX_COMMAND_BYTES)
