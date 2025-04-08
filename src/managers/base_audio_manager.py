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

    crypto_manager : CryptoManager
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

        # # Added this for monitor support
        # if self.audio.get_device_count() > 7:
        #     self.logger.info(
        #         "The program is running under the assumption that it is plugged in to a monitor."
        #     )
        #     self.input_device_index = in_device_index
        #     self.output_device_index = 3
        # else:
        #     self.input_device_index = in_device_index
        #     self.output_device_index = out_device_index

        self.input_stream = None
        self.output_stream = None

        # Initialize the crypto_manager
        self.crypto_manager = CryptoManager()

        self.volume = 100  # Volume in %
        self.thread_manager = thread_manager

        # Create Opus encoder
        self.encoder = opuslib.Encoder(
            self.RATE, self.CHANNELS, application=opuslib.APPLICATION_AUDIO
        )

        # Decode Opus audio
        self.decoder = opuslib.Decoder(self.RATE, self.CHANNELS)

        # Starting gain for normalization
        self.current_gain = CURRENT_GAIN
        # Audio processing parameters
        self.set_audio_processing(
            enable_normalization=ENABLE_NORMALIZATION,
            enable_noise_gate=ENABLE_NOISE_GATE,
            target_rms=TARGET_RMS,
            noise_gate_threshold=NOISE_GATE_THRESHOLD,
            smoothing_factor=SMOOTHING_FACTOR,
        )

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

    def set_audio_processing(
        self,
        enable_normalization=None,
        enable_noise_gate=None,
        target_rms=None,
        noise_gate_threshold=None,
        smoothing_factor=None,
    ):
        """
        Configure audio processing parameters.

        Parameters
        ----------
        enable_normalization : bool, optional
            Enable or disable audio normalization.
        enable_noise_gate : bool, optional
            Enable or disable noise gate.
        target_rms : int, optional
            Target RMS value for normalization.
        noise_gate_threshold : int, optional
            RMS threshold below which audio is considered noise.
        smoothing_factor : float, optional
            Factor for smoothing normalization (0-1, higher = smoother).
        """
        if enable_normalization is not None:
            self.enable_normalization = enable_normalization
        if enable_noise_gate is not None:
            self.enable_noise_gate = enable_noise_gate
        if target_rms is not None:
            self.target_rms = target_rms
        if noise_gate_threshold is not None:
            self.noise_gate_threshold = noise_gate_threshold
        if smoothing_factor is not None:
            # Clamp between 0 and 1
            self.smoothing_factor = min(max(smoothing_factor, 0.0), 1.0)

        self.logger.info(
            f"\n\tAudio processing updated: normalization={self.enable_normalization}, "
            f"\tnoise_gate={self.enable_noise_gate}, target_rms={self.target_rms}, "
            f"\tnoise_threshold={self.noise_gate_threshold}, smoothing={self.smoothing_factor}"
        )

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
            del self.input_stream
            self.input_stream = None

    def close_output_stream(self):
        """
        Close the audio output streams.
        """
        # Close output stream if it is open
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
            del self.output_stream
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
        Applies normalization and noise gate if enabled.

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

        # Apply audio processing if enabled
        if self.enable_normalization or self.enable_noise_gate:
            # Calculate current RMS (audio level)
            rms = np.sqrt(np.mean(np.square(audio_data.astype(np.float32))))

            # Apply noise gate if enabled
            if self.enable_noise_gate and rms < self.noise_gate_threshold:
                # If below threshold, attenuate audio to reduce noise
                audio_data = np.zeros_like(audio_data)

            # Apply normalization if enabled and we're above noise gate threshold
            if self.enable_normalization and (
                not self.enable_noise_gate or rms >= self.noise_gate_threshold
            ):
                if rms > 0:
                    # Calculate target gain
                    # Avoid division by zero
                    target_gain = self.target_rms / (rms + 1e-10)

                    # Smooth the gain adjustment to prevent abrupt volume changes
                    self.current_gain = (
                        self.smoothing_factor * self.current_gain
                        + (1 - self.smoothing_factor) * target_gain
                    )

                    # Limit gain to avoid excessive amplification of quiet sounds
                    self.current_gain = min(self.current_gain, 10.0)

                    # Apply gain
                    audio_data = (
                        audio_data.astype(np.float32) * self.current_gain
                    ).astype(np.int16)

        # Apply manual volume control
        volume_scalar = self.volume / 100
        audio_data = (audio_data * volume_scalar).astype(np.int16)

        # Convert back to bytes
        data = audio_data.tobytes()
        try:
            self.output_stream.write(data)
        except Exception as e:
            self.logger.error(f"Exception: [{e}]")

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
