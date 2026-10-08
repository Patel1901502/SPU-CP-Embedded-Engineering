"""ESP32 MicroPython boot-time configuration.

MicroPython automatically executes ``boot.py`` before ``main.py`` after a
power-on reset or software reset. Keep this file small and deterministic so
hardware reaches a known state before the application starts.
"""

import gc

import machine

# Run the ESP32 CPU at 160 MHz. This is a reasonable balance between
# application performance and power consumption for this demonstration.
machine.freq(160_000_000)

# Reclaim any temporary objects created while the MicroPython runtime starts.
# Doing this before main.py leaves the largest practical heap for the app.
gc.collect()
