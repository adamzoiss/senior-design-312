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
from src.handlers.peripheral_drivers.rfm69 import *
from src.managers.audio_manager import *
from src.managers.thread_manager import *
from src.utils.constants import *
import lgpio
import os

import scipy.signal as signal
import numpy as np

# Generate the Start Signal Packet
# 30 repetitions of 0x55, 0xAA (2 bytes each)
start_signal = bytes([0x55, 0xAA] * 30)

# Generate the Stop Signal Packet
# 30 repetitions of 0xAA, 0x55 (2 bytes each)
stop_signal = bytes([0xAA, 0x55] * 30)

# global frame_buffer
global frame_buffer, last_packet_time
frame_buffer = b""


# Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
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
    in_device_index=3,
    out_device_index=0,
)
am._open_output_stream()

am.volume = 100

# Queue to store received packets
packet_queue = queue.Queue()

handle = lgpio.gpiochip_open(0)

# Initialize Opus decoder
decoder = opuslib.Decoder(RATE, CHANNELS)

# # Clear the received audio file at the start of the program
# with open("received_audio.wav", "wb") as f:
#     pass


# def save_packet_to_file(packet, filename="received_audio.wav"):
#     with open(filename, "ab") as f:
#         f.write(packet)


def _callback(chip, gpio, level, timestamp):
    if rfm69.payload_ready:
        packet = rfm69.receive(timeout=None)
        if packet is not None:
            if packet == start_signal:
                # Empty the packet queue
                print("received start signal")
                while not packet_queue.empty():
                    packet_queue.get()
                # Empty the frame buffer
                frame_buffer = b""
            elif packet == stop_signal:
                print("received stop signal")
                # Empty the packet queue
                # while not packet_queue.empty():
                #     packet_queue.get()
                # # Empty the frame buffer
                # frame_buffer = b""
            else:
                print(packet)
                packet_queue.put(packet)
                # save_packet_to_file(packet)


# Define radio parameters.
RADIO_FREQ_MHZ = 433.0  # Frequency of the radio in Mhz. Must match your
# module! Can be a value like 915.0, 433.0, etc.
# Initialze RFM radio
rfm69 = RFM69(
    spi_bus=SPI_BUS,
    cs_pin=SPI_CS,
    reset_pin=RST,
    frequency=RADIO_FREQ_MHZ,
    handle=handle,
)

# Optionally set an encryption key (16 byte AES key). MUST match both
# on the transmitter and receiver (or be set to None to disable/the default).
rfm69.encryption_key = (
    b"\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08"
)
# configure the interrupt pin and event handling.
# RFM69_G0 = 22
lgpio.gpio_claim_alert(handle, G0, lgpio.RISING_EDGE)
recv_cb = lgpio.callback(handle, G0, lgpio.RISING_EDGE, _callback)

# Print out some chip state:
print("Temperature: {0}C".format(rfm69.temperature))
print("Frequency: {0}mhz".format(rfm69.frequency_mhz))
print("Bit rate: {0}kbit/s".format(rfm69.bitrate / 1000))
print("Frequency deviation: {0}hz".format(rfm69.frequency_deviation))

rfm69.listen()
print("Waiting for packets...")


last_packet_time = time.time()

try:
    while True:
        try:
            # Get next packet, wait up to BUFFER_TIMEOUT seconds
            packet = packet_queue.get(timeout=BUFFER_TIMEOUT)
            last_packet_time = time.time()  # Update last packet timestamp
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
                # print(f"len: {len(opus_frame)}")
                frame_buffer = frame_buffer[
                    2 + frame_size :
                ]  # Remove processed data

                # Decode and play audio
                try:
                    decoded_audio = decoder.decode(opus_frame, FRAME_SIZE)
                    am.write_output(decoded_audio)
                except opuslib.exceptions.OpusError as e:
                    print(f"Opus decoding error: {e} | len: {len(opus_frame)}")
                    if frame_buffer:
                        frame_buffer = b""

        except queue.Empty:
            # Timeout reached, check for lost packets
            if time.time() - last_packet_time > BUFFER_TIMEOUT:
                print("No data.")
                if frame_buffer:
                    frame_buffer = b""
                # silent_audio = b"\x00" * (
                #     FRAME_SIZE * 2
                # )  # Insert silence to maintain sync
                # am.output_stream.write(silent_audio)
                last_packet_time = time.time()
            # pass
        # the sleep time is arbitrary since any incomming packe will trigger an interrupt
        # and be received.
        # time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    recv_cb.cancel()
    lgpio.gpiochip_close(handle)
