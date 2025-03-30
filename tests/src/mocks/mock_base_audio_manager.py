import pyaudio
import wave
import os
from unittest.mock import MagicMock
from src.managers.base_audio_manager import BaseAudioManager

FILE = "tests/src/audio/48k_960.wav"


class MockBaseAudioManager(BaseAudioManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mock_audio_file = FILE
        self._mock_pyaudio()

    def _mock_pyaudio(self):
        """
        Mock the pyaudio.PyAudio class and its methods.
        """
        self.audio = MagicMock(spec=pyaudio.PyAudio)
        self.input_stream = MagicMock()
        self.output_stream = MagicMock()

        # Mock the open method to return the mocked input stream
        self.audio.open.return_value = self.input_stream

        # Read the entire mock audio file into memory
        with wave.open(self.mock_audio_file, "rb") as wf:
            self.audio_data = wf.readframes(wf.getnframes())

        # Mock the read method to read data from the in-memory copy
        self.input_stream.read.side_effect = self._mock_read

    def _mock_read(self, num_frames, exception_on_overflow=False):
        """
        Mock read method to read data from the in-memory copy of the audio file.
        """
        chunk_size = num_frames * 2
        data = self.audio_data[:chunk_size]
        self.audio_data = self.audio_data[chunk_size:]
        return data

    def open_input_stream(self):
        """
        Open the mock audio input stream.
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

    def read_input_stream(self, num_frames):
        """
        Read data from the mock audio input stream.
        """
        try:
            data = self.input_stream.read(num_frames)
            return data
        except Exception as e:
            self.logger.warning(
                f"Encountered exception while reading stream: {e}"
            )
            return None

    def close_input_stream(self):
        """
        Close the mock audio input stream.
        """
        if self.input_stream:
            self.input_stream.close()
            self.input_stream = None
