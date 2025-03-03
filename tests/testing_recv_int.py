# SPDX-FileCopyrightText: 2020 Tony DiCola, Jerry Needell for Adafruit Industries
# SPDX-License-Identifier: MIT

# Example using Interrupts to send a message and then wait indefinitely for messages
# to be received. Interrupts are used only for receive. sending is done with polling.
# This example is for systems that support interrupts like the Raspberry Pi with "blinka"
# CircuitPython does not support interrupts so it will not work on  Circutpython boards
import time
import queue
import numpy as np
import pyaudio

# import adafruit_rfm69
from src.managers.rf_manager import *
from src.managers.audio_manager import *
from src.managers.thread_manager import *
import lgpio
import os

import scipy.signal as signal
import numpy as np


# Clear the received audio file at the start of the program
with open("received_audio.mp3", "wb") as f:
    pass


def save_packet_to_file(packet, filename="received_audio.mp3"):
    with open(filename, "ab") as f:
        f.write(packet)
        write_packet_to_output_stream(packet)


def _callback(chip, gpio, level, timestamp):
    # print(
    #     (
    #         f"Chip: {chip} | "
    #         f"GPIO{gpio} | "
    #         f"Level: {level} | "
    #         f"Timestamp: {timestamp}"
    #     )
    # )
    if rfm69.payload_ready:
        packet = rfm69.receive(timeout=None)
        if packet is not None:

            save_packet_to_file(packet)


# Define radio parameters.
RADIO_FREQ_MHZ = 433.0  # Frequency of the radio in Mhz. Must match your
# module! Can be a value like 915.0, 433.0, etc.
# Initialze RFM radio
rfm69 = RFM69(0, 1, 25, RADIO_FREQ_MHZ)

# Optionally set an encryption key (16 byte AES key). MUST match both
# on the transmitter and receiver (or be set to None to disable/the default).
rfm69.encryption_key = (
    b"\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08"
)
# configure the interrupt pin and event handling.
RFM69_G0 = 22
lgpio.gpio_claim_alert(rfm69.handle, RFM69_G0, lgpio.RISING_EDGE)
recv_cb = lgpio.callback(rfm69.handle, RFM69_G0, lgpio.RISING_EDGE, _callback)

# Print out some chip state:
print("Temperature: {0}C".format(rfm69.temperature))
print("Frequency: {0}mhz".format(rfm69.frequency_mhz))
print("Bit rate: {0}kbit/s".format(rfm69.bitrate / 1000))
print("Frequency deviation: {0}hz".format(rfm69.frequency_deviation))

rfm69.listen()


# Send a packet.  Note you can only send a packet up to 60 bytes in length.
# This is a limitation of the radio packet size, so if you need to send larger
# amounts of data you will need to break it into smaller send calls.  Each send
# call will wait for the previous one to finish before continuing.
# rfm69.send(bytes("Hello world!\r\n", "utf-8"), keep_listening=True)
# print("Sent hello world message!")
# If you don't wawnt to send a message to start you can just start lintening

# Wait to receive packets.  Note that this library can't receive data at a fast
# rate, in fact it can only receive and process one 60 byte packet at a time.
# This means you should only use this for low bandwidth scenarios, like sending
# and receiving a single message at a time.
print("Waiting for audio...")

try:
    # the loop is where you can do any desire processing
    # the global variable packet_received can be used to determine if a packet was received.
    while True:
        # the sleep time is arbitrary since any incomming packe will trigger an interrupt
        # and be received.
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    recv_cb.cancel()
