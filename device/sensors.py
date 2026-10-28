"""Real TMP102 sensor driver plus an explicitly selected synthetic demo backend."""

import math
import time


class SimulatedSensorSuite:
    """Provide a single interface for all monitored sensor measurements."""

    def __init__(self):
        # ticks_ms() is preferred over wall-clock time on MicroPython because
        # it is monotonic and designed to work correctly across tick wraparound.
        self.start_ms = time.ticks_ms()

    def info(self):
        return {"sensor": "simulated", "source": "synthetic"}

    def read(self):
        """Return one snapshot of temperature, vibration, and current.

        The sine waves make the values change slowly and predictably, which is
        useful for demos and automated host testing. Replace these expressions
        with real sensor-driver calls when hardware is available.
        """
        elapsed_ms = time.ticks_diff(time.ticks_ms(), self.start_ms)
        elapsed_s = elapsed_ms / 1000.0

        # Simulated temperature: approximately 24 C with a slow +/-0.5 C drift.
        temperature_c = 24.0 + 0.5 * math.sin(elapsed_s / 10.0)

        # Simulated vibration: small periodic movement around a 0.10 baseline.
        vibration = 0.10 + 0.02 * math.sin(elapsed_s * 2.0)

        # Simulated load current: approximately 80 mA with +/-5 mA variation.
        current_ma = 80.0 + 5.0 * math.sin(elapsed_s / 5.0)

        # Round values before transmission to keep UART messages compact and
        # stable while still retaining useful precision.
        return {
            "temp_c": round(temperature_c, 3),
            "vibration": round(vibration, 4),
            "current_ma": round(current_ma, 3),
        }


class SensorReadError(Exception):
    """A failed measurement; never substitute a synthetic or stale sample."""


class TMP102:
    """TMP102 normal mode, continuous conversion at 4 Hz."""

    def __init__(self, i2c, address=0x48):
        self.i2c = i2c
        self.address = address
        # Normal mode, continuous, 4 Hz. Alert settings use reset defaults.
        self.i2c.writeto_mem(address, 1, bytes([0x60, 0xA0]))
        time.sleep_ms(300)  # First conversion must complete before reading.

    def read_c(self):
        data = self.i2c.readfrom_mem(self.address, 0, 2)
        if len(data) != 2:
            raise OSError("SHORT_READ")
        if data[1] & 1:
            raise OSError("UNEXPECTED_EXTENDED_MODE")
        raw = ((data[0] << 8) | data[1]) >> 4
        if raw & 0x800:
            raw -= 4096
        value = raw * 0.0625
        if not -40 <= value <= 125:
            raise OSError("OUT_OF_RANGE")
        return value


class SensorSuite:
    """Real temperature only, with injectable bus and wrap-safe rate limiting."""

    def __init__(self, i2c=None, settings=None):
        if settings is None:
            import config as settings
        self.settings = settings
        self.driver = None
        self.i2c = i2c
        self.last_ms = None
        if settings.SAMPLE_PERIOD_MS < 250:
            raise ValueError("SAMPLE_PERIOD_MS must be >= 250")
        for value in (settings.TEMP_SCALE, settings.TEMP_OFFSET_C):
            if not math.isfinite(value):
                raise ValueError("Calibration must be finite")
        if settings.TEMP_SCALE <= 0:
            raise ValueError("TEMP_SCALE must be positive")

    def info(self):
        return {
            "sensor": "TMP102",
            "source": "hardware",
            "address": self.settings.TMP102_ADDRESS,
            "sda_pin": self.settings.I2C_SDA_PIN,
            "scl_pin": self.settings.I2C_SCL_PIN,
            "i2c_freq_hz": self.settings.I2C_FREQ_HZ,
            "sample_period_ms": self.settings.SAMPLE_PERIOD_MS,
            "temp_scale": self.settings.TEMP_SCALE,
            "temp_offset_c": self.settings.TEMP_OFFSET_C,
            "units": "degC",
        }

    def read(self):
        now = time.ticks_ms()
        if self.last_ms is not None:
            if time.ticks_diff(now, self.last_ms) < self.settings.SAMPLE_PERIOD_MS:
                raise SensorReadError("RATE_LIMIT")
        self.last_ms = now
        try:
            if self.driver is None:
                if self.i2c is None:
                    from machine import I2C, Pin

                    self.i2c = I2C(
                        self.settings.I2C_ID,
                        sda=Pin(self.settings.I2C_SDA_PIN),
                        scl=Pin(self.settings.I2C_SCL_PIN),
                        freq=self.settings.I2C_FREQ_HZ,
                    )
                self.driver = TMP102(self.i2c, self.settings.TMP102_ADDRESS)
            raw = self.driver.read_c()
            calibrated = raw * self.settings.TEMP_SCALE + self.settings.TEMP_OFFSET_C
            if not math.isfinite(calibrated):
                raise OSError("INVALID_CALIBRATION_RESULT")
            return {"temp_c": round(calibrated, 4), "raw_temp_c": raw}
        except (OSError, ValueError) as exc:
            self.driver = None  # Reconfigure after reconnect on the next request.
            raise SensorReadError("TMP102_READ_FAILED:" + str(exc))


class AnalogSensorSuite:
    """Linear analog temperature backend using an injected read_u16() ADC.

    Voltage = raw / 65535 * full scale; temperature = (voltage - zero) / slope.
    No TMP102 assumptions or synthetic fallback; uses the same command interface.
    """

    def __init__(self, adc, settings):
        self.adc = adc
        self.settings = settings
        self.last_ms = None
        values = (
            settings.ANALOG_FULL_SCALE_V,
            settings.ANALOG_VOLTS_PER_C,
            settings.ANALOG_ZERO_C_V,
            settings.TEMP_SCALE,
            settings.TEMP_OFFSET_C,
        )
        if not all(math.isfinite(value) for value in values):
            raise ValueError("Analog calibration must be finite")
        if (
            settings.ANALOG_FULL_SCALE_V <= 0
            or settings.ANALOG_VOLTS_PER_C <= 0
            or settings.TEMP_SCALE <= 0
            or settings.SAMPLE_PERIOD_MS < 0
        ):
            raise ValueError("Invalid analog configuration")

    def info(self):
        s = self.settings
        return {
            "sensor": "analog",
            "source": "hardware",
            "units": "degC",
            "sample_period_ms": s.SAMPLE_PERIOD_MS,
            "full_scale_v": s.ANALOG_FULL_SCALE_V,
            "volts_per_c": s.ANALOG_VOLTS_PER_C,
            "zero_c_v": s.ANALOG_ZERO_C_V,
            "temp_scale": s.TEMP_SCALE,
            "temp_offset_c": s.TEMP_OFFSET_C,
        }

    def read(self):
        now = time.ticks_ms()
        s = self.settings
        if self.last_ms is not None and time.ticks_diff(now, self.last_ms) < s.SAMPLE_PERIOD_MS:
            raise SensorReadError("RATE_LIMIT")
        self.last_ms = now
        try:
            raw = self.adc.read_u16()
            if not 0 <= raw <= 65535:
                raise ValueError("ADC_OUT_OF_RANGE")
            voltage = raw / 65535 * s.ANALOG_FULL_SCALE_V
            temperature = (voltage - s.ANALOG_ZERO_C_V) / s.ANALOG_VOLTS_PER_C
            calibrated = temperature * s.TEMP_SCALE + s.TEMP_OFFSET_C
            if not math.isfinite(calibrated):
                raise ValueError("INVALID_CALIBRATION_RESULT")
            return {"temp_c": round(calibrated, 4), "raw_temp_c": temperature}
        except (OSError, ValueError) as exc:
            raise SensorReadError("ANALOG_READ_FAILED:" + str(exc))
