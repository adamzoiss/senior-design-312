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

# Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
FRAME_SIZE = 960  # 20ms Opus frame at 48kHz
PACKET_SIZE = 60  # Radio transceiver limit
BUFFER_TIMEOUT = 2  # Max seconds to wait for a missing packet

tm = ThreadManager()
am = AudioManager(
    tm,
    frame_size=FRAME_SIZE,
    format=FORMAT,
    channels=1,
    sample_rate=RATE,
    in_device_index=4,
    out_device_index=0,
)
am._open_output_stream()

# Queue to store received packets
packet_queue = queue.Queue()

# Initialize Opus decoder
decoder = opuslib.Decoder(RATE, CHANNELS)

# Clear the received audio file at the start of the program
with open("received_audio.wav", "wb") as f:
    pass


def save_packet_to_file(packet, filename="received_audio.wav"):
    with open(filename, "ab") as f:
        f.write(packet)


def _callback(chip, gpio, level, timestamp):
    if rfm69.payload_ready:
        packet = rfm69.receive(timeout=None)
        if packet is not None:
            packet_queue.put(packet)


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
print("Waiting for packets...")

# global frame_buffer
global frame_buffer, last_packet_time
frame_buffer = b""
last_packet_time = time.time()

try:
    while True:
        try:
            # Get next packet, wait up to BUFFER_TIMEOUT seconds
            packet = packet_queue.get(timeout=BUFFER_TIMEOUT)
            # last_packet_time = time.time()  # Update last packet timestamp
            frame_buffer += packet  # Collect incoming packets

            # Process frames
            while len(frame_buffer) >= 2:
                frame_size = struct.unpack_from("H", frame_buffer, 0)[
                    0
                ]  # Read stored frame size

                # Ensure we have the full frame before processing
                if len(frame_buffer) < 2 + frame_size:
                    break  # Wait for more data

                # Extract full Opus frame
                opus_frame = frame_buffer[2 : 2 + frame_size]
                frame_buffer = frame_buffer[
                    2 + frame_size :
                ]  # Remove processed data

                # Decode and play audio
                try:
                    decoded_audio = decoder.decode(opus_frame, FRAME_SIZE)
                    am.output_stream.write(decoded_audio)
                except opuslib.exceptions.OpusError as e:
                    print(f"Opus decoding error: {e}")

        except queue.Empty:
            # Timeout reached, check for lost packets
            # if time.time() - last_packet_time > BUFFER_TIMEOUT:
            #     print("Warning: Packet loss detected, inserting silence.")
            #     silent_audio = b"\x00" * (
            #         FRAME_SIZE * 2
            #     )  # Insert silence to maintain sync
            #     # am.output_stream.write(silent_audio)
            #     last_packet_time = time.time()
            pass
        # the sleep time is arbitrary since any incomming packe will trigger an interrupt
        # and be received.
        # time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    recv_cb.cancel()
