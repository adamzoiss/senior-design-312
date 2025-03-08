"""
Senior Project : Hardware Encryption Device
Team 312
File : audio_manager.py
Description: This is the audio driver for the project. By itself it is able to record and monitor
    audio from a usb mic/headphone set. It is also able to encrypt and decrypt.
    The audio file or stream itself may be encrypted and decrypted. This provides a lot of
    flexibility down the line.
"""

import pyaudio
import wave
import opuslib
import numpy as np
import os
import threading
import struct

from src.managers.crypto_manager import CryptoManager
from src.utils.utils import *
from src.logging.logger import *
from src.managers.thread_manager import ThreadManager
from src.utils.constants import *

# Path and file names for the file types.
PATH = "./audio_files/"
AUDIO_FILE = PATH + "audio.wav"
ENCRYPTED_AUDIO_FILE = PATH + "encrypted_audio.bin"
ENCRYPTED_AUDIO_STREAM_FILE = PATH + "encrypted_audio_stream.wav"
DECRYPTED_AUDIO_FILE = PATH + "decrypted_audio.wav"
DECRYPTED_AUDIO_STREAM_FILE = PATH + "decrypted_audio_stream.wav"


class BaseAudioManager:
    """
    Driver that handles the audio input and output.
    The user must specify the index of the USB mic and headphones.
    To discover what index, run the driver and select option 3.

    Attributes
    ----------
    CHUNK : int
        Number of audio frames per buffer. (Lower means less latency)
    FORMAT : pyaudio.paInt16
        Format of audio data (16-bit audio in this case).
    CHANNELS : int
        Number of audio channels (1 for mono).
    RATE : int
        Sampling rate in Hz.

    audio : pyaudio.PyAudio
        PyAudio instance for managing audio streams.
    input_device_index : int or None
        Index of the input device.
    output_device_index : int or None
        Index of the output device.

    input_stream : pyaudio.Stream or None
        Stream object for audio input.
    output_stream : pyaudio.Stream or None
        Stream object for audio output.

    encryptor : CryptoManager
        Instance of the CryptoManager for encryption and decryption.
    """

    def __init__(
        self,
        thread_manager: ThreadManager,
        frame_size=FRAME_SIZE,
        format=FORMAT,
        channels=CHANNELS,
        sample_rate=RATE,
        in_device_index=INPUT_DEV_INDEX,
        out_device_index=OUTPUT_DEV_INDEX,
    ):
        """
        Initialize the BaseAudioManager instance and configure default audio settings.
        """
        # Set up logging
        self.logger: logging = Logger(
            "BaseAudioManager",
            console_level=logging.INFO,
            console_logging=EN_CONSOLE_LOGGING,
        )

        self.CHUNK = frame_size  # Affects latency for monitoring
        self.FORMAT = format
        self.CHANNELS = channels
        self.RATE = sample_rate

        self.audio = pyaudio.PyAudio()
        self.input_device_index = in_device_index  #! THIS VALUE CAN CHANGE
        self.output_device_index = out_device_index  #! THIS VALUE CAN CHANGE

        self.input_stream = None
        self.output_stream = None

        # Initialize the encryptor
        self.encryptor = CryptoManager()

        self.volume = 50  # Volume in %
        self.thread_manager = thread_manager

        # Create Opus encoder
        self.encoder = opuslib.Encoder(
            self.RATE, self.CHANNELS, application=opuslib.APPLICATION_AUDIO
        )

        # Decode Opus audio
        self.decoder = opuslib.Decoder(self.RATE, self.CHANNELS)

        self.logger.info("BaseAudioManager initialized.")

    def __del__(self):
        """
        Destructor method that ensures proper termination of resources.
        This method is called when the object is about to be destroyed. It ensures
        that the `terminate` method is called to release any resources or perform
        any necessary cleanup.
        Notes
        -----
        The `__del__` method is not guaranteed to be called for objects that still
        exist when the interpreter exits. It is recommended to use context managers
        or explicit cleanup methods instead of relying on `__del__`.
        """

        self.close_streams()
        self.terminate()
        # self.logger.info("BaseAudioManager cleaned up & deleted.")

    def terminate(self):
        """
        Terminate the PyAudio instance.

        This method releases all resources allocated by PyAudio to ensure proper cleanup.
        """
        # Terminate the PyAudio session
        self.audio.terminate()

    def open_input_stream(self):
        """
        Open the audio input stream.
        """
        try:
            self.input_stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                input_device_index=self.input_device_index,
                frames_per_buffer=self.CHUNK,
            )
        except Exception as e:
            self.logger.warning(
                f"Encountered exception with input stream: {e}"
            )

    def open_output_stream(self):
        """
        Open the audio output stream.
        """
        try:
            self.output_stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                output=True,
                output_device_index=self.output_device_index,
                frames_per_buffer=self.CHUNK,
            )
        except Exception as e:
            self.logger.warning(
                f"Encountered exception with output stream: {e}"
            )

    def open_streams(self):
        """
        Open the audio input and output streams.
        """
        # Configure and open the input stream
        self.open_input_stream()
        # Configure and open the output stream
        self.open_output_stream()

    def close_input_stream(self):
        """
        Close the audio input stream.
        """
        # Close input stream if it is open
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
            self.input_stream = None

    def close_output_stream(self):
        """
        Close the audio output streams.
        """
        # Close output stream if it is open
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
            self.output_stream = None

    def close_streams(self):
        """
        Close the audio input and output streams.
        """
        self.close_input_stream()
        self.close_output_stream()

    def find_devices(self):
        """
        Display all available audio input and output devices.
        """
        for i in range(self.audio.get_device_count()):
            dev = self.audio.get_device_info_by_index(i)
            self.logger.info(
                f"{i}: {dev['name']} - {dev['maxInputChannels']} in / {dev['maxOutputChannels']} out"
            )

    def write_output(self, data, volume=None):
        """
        Writes audio data to the output stream with the specified volume.
        Parameters
        ----------
        data : bytes
            The audio data to be written to the output stream.
        volume : int, optional
            The volume level to apply to the audio data (default is 50).
        Raises
        ------
        Exception
            If there is an error writing to the output stream.
        """

        # Update volume
        if volume is not None:
            self.volume = volume
        # Convert to NumPy array
        audio_data = np.frombuffer(data, dtype=np.int16)
        # Apply volume scaling
        volume_scalar = (self.volume / 100) * 10
        audio_data = (audio_data * volume_scalar).astype(np.int16)
        # Convert back to bytes
        data = audio_data.tobytes()
        try:
            self.output_stream.write(data)
        except Exception as e:
            print(f"Exception: [{e}]")

    def encode(self, data: bytes) -> bytes:
        """
        Encodes the given data using the specified encoder and chunk size.
        Parameters
        ----------
        data : bytes
            The data to be encoded.
        Returns
        -------
        bytes
            The encoded data.
        """

        return self.encoder.encode(data, self.CHUNK)

    def decode(self, data: bytes) -> bytes:
        """
        Decodes the given audio data.
        Parameters
        ----------
        data : bytes
            The audio data to decode.
        Returns
        -------
        bytes
            The decoded audio data.
        """

        return self.decoder.decode(data, self.CHUNK)


if __name__ == "__main__":
    tm = ThreadManager()
    handler = BaseAudioManager(tm)
    del handler
    del tm
