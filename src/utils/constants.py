"""
Senior Project : Hardware Encryption Device
Team 312
File : interface_constants.py
Description: This will handle the constants for the interface/GPIO module.
"""

import pyaudio

"""
Option to enable logging to the terminal/console.
"""
EN_CONSOLE_LOGGING = True

"""
Application threads
"""
MAIN_THREAD = "MAIN"
DEBUG_THREAD = "DEBUG THREAD"
TRANSMIT_THREAD = "TRANSMIT THREAD"
RECEIVE_THREAD = "RECEIVE THREAD"

"""
ANO Navigation Encoder and button GPIO assignments and constants.
"""
SW_1 = 24  # GPIO pin for push button 1 - pin 18
SW_2 = 13  # GPIO pin for push button 2 - pin 33
SW_3 = 22  # GPIO pin for push button 3 - pin 15
SW_4 = 17  # GPIO pin for push button 4 - pin 11
SW_5 = 12  # GPIO pin for push button 5 - pin 32

ENC_A = 27  # GPIO pin for rotary encoder A - pin 13
ENC_B = 5  # GPIO pin for rotary encoder B - pin 29

# Debounce time in microseconds
DEBOUNCE_MICRO = 10000  # 10ms

"""
RFM69HCW Radio Transceiver GPIO assignments and constants.
"""
SPI_BUS = 0  # Used to specify the SPI devices for spidev
SPI_CS = 0  # GPIO pin for CE0 - pin 24

SPI_SCK = 0  # GPIO pin for SCK - pin 23
SPI_MISO = 0  # GPIO pin for MISO - pin 21
SPI_MOSI = 0  # GPIO pin for MOSI - pin 19

G0 = 25  # GPIO pin for G0 - pin 22
RST = 26  # GPIO pin for RST - pin 37

RADIO_FREQ_MHZ = 433.0  # Frequency of the radio in Mhz. Must match your
# Optionally set an encryption key (16 byte AES key). MUST match both
# on the transmitter and receiver (or be set to None to disable/the default).
ENCRYPTION_KEY = (
    b"\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08"
)

# 2-byte start sequence (can be any unique marker)
START_SEQUENCE = b"\xa5\x5a"
PACKET_SIZE = 60  # Radio transceiver byte limit
BUFFER_TIMEOUT = 1  # Max seconds to wait for a missing packet

"""
SSD1306 Display constants.
"""
# Display Address
I2C_BUS = 1  # I2C bus
I2C_SLAVE = 0x0703  # ioctl command to set device address
SSD1306_I2C_ADDR = 0x3C  # Common I2C address for SSD1306

PIXEL_WIDTH = 128
PIXEL_HEIGHT = 64

"""
Audio configuration constants.
"""
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
FRAME_SIZE = 960  # 20ms Opus frame at 48kHz
# Input and output device indices.
INPUT_DEV_INDEX = 1
OUTPUT_DEV_INDEX = 2
