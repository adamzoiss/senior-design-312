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

from src.managers.base_audio_manager import *

# Path and file names for the file types.
PATH = "./audio_files/"
AUDIO_FILE = PATH + "audio.wav"
ENCRYPTED_AUDIO_FILE = PATH + "encrypted_audio.bin"
ENCRYPTED_AUDIO_STREAM_FILE = PATH + "encrypted_audio_stream.wav"
DECRYPTED_AUDIO_FILE = PATH + "decrypted_audio.wav"
DECRYPTED_AUDIO_STREAM_FILE = PATH + "decrypted_audio_stream.wav"


class AudioManager(BaseAudioManager):
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
        Initialize the AudioManager instance and configure default audio settings.
        """

        # Call the BaseAudioManager init
        super().__init__(
            thread_manager,
            frame_size,
            format,
            channels,
            sample_rate,
            in_device_index,
            out_device_index,
        )

        # Set up logging
        self.logger: logging = Logger(
            "AudioManager",
            console_level=logging.INFO,
            console_logging=EN_CONSOLE_LOGGING,
        )

        self.logger.info("AudioManager initialized.")

    def monitor_audio(self, stop_event: threading.Event):
        """
        Continuously monitor and play audio from the microphone.

        This method plays the audio captured from the microphone through the output device.

        Raises
        ------
        KeyboardInterrupt
            Stops monitoring when Ctrl+C is pressed.
        """
        self.logger.info(f"Monitoring audio | {self.volume}%")

        try:
            # Open the streams
            if self.audio.get_device_count() == 0:
                self.logger.warning("Can not open streams if no audio device.")
                return
            else:
                self.open_streams()

            # Monitor the audio
            while not stop_event.is_set():
                data = self.input_stream.read(
                    self.CHUNK, exception_on_overflow=False
                )
                ###############################################################
                # Convert to NumPy array
                audio_data = np.frombuffer(data, dtype=np.int16)
                # Apply volume scaling
                volume_scalar = (self.volume / 100) * 4
                audio_data = (audio_data * volume_scalar).astype(np.int16)
                # Convert back to bytes
                data = audio_data.tobytes()
                ###############################################################
                # Encrypt --> decrypt --> write to output stream
                encrypted_data = self.crypto_manager.encrypt(data)
                decrypted_data = self.crypto_manager.decrypt(encrypted_data)
                self.output_stream.write(decrypted_data)
        except KeyboardInterrupt:
            self.logger.info("\nMonitoring stopped.\n")
        finally:
            self.close_streams()
            self.logger.info("Monitoring stopped.")

    def record_audio(self, output_file=AUDIO_FILE, monitoring=False):
        """
        Record audio from the microphone and save it to a WAV file.

        Parameters
        ----------
        output_file : str, optional
            The name of the output WAV file (default is "recorded_audio.wav").
        monitoring : bool, optional
            If True, play back the recorded audio while recording (default is False).
        """
        # Get the parent directory of the current script
        parent_dir = get_proj_root()
        # Create the target folder path in the parent directory
        output_dir = os.path.join(parent_dir, PATH)
        # Construct the full path for the output file
        output_file_path = os.path.join(
            output_dir, os.path.basename(output_file)
        )
        # Ensure that the path exists, and if doesn't is created.
        ensure_path(str(output_dir))

        try:
            self.logger.debug("Recording... Press Ctrl+C to stop.")
            self.open_streams()
            frames = []  # List to store recorded frames
            try:
                while True:
                    # Capture audio data from the input stream
                    data = self.input_stream.read(
                        self.CHUNK, exception_on_overflow=False
                    )
                    frames.append(data)
                    # Playback the captured data
                    if monitoring:
                        self.output_stream.write(data)
            except KeyboardInterrupt:
                self.logger.debug("\nRecording stopped.")
                # Save recorded audio to a WAV file
                with wave.open(output_file, "wb") as wf:
                    wf.setnchannels(self.CHANNELS)
                    wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                    wf.setframerate(self.RATE)
                    wf.writeframes(b"".join(frames))
                self.logger.debug(f"Audio saved to {output_file}")
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
        finally:
            self.close_streams()

    def record_encrypted_audio(
        self, output_file=ENCRYPTED_AUDIO_STREAM_FILE, monitoring=False
    ):
        """
        Record audio, encrypt it, and save it to a file.

        Parameters
        ----------
        output_file : str, optional
            The name of the output encrypted file (default is "recorded_audio_encrypted.wav").
        monitoring : bool, optional
            If True, play back the recorded audio while recording (default is False).
        """
        # Get the parent directory of the current script
        parent_dir = get_proj_root()
        # Create the target folder path in the parent directory
        output_dir = os.path.join(parent_dir, PATH)
        # Construct the full path for the output file
        output_file_path = os.path.join(
            output_dir, os.path.basename(output_file)
        )
        # Ensure that the path exists, and if doesn't is created.
        ensure_path(str(output_dir))

        try:
            self.logger.debug("Recording... Press Ctrl+C to stop.")
            self.open_streams()
            frames = []
            try:
                while True:
                    data = self.input_stream.read(
                        self.CHUNK, exception_on_overflow=False
                    )
                    encrypted_data = self.crypto_manager.encrypt(data)
                    frames.append(encrypted_data)
                    if monitoring:
                        self.output_stream.write(data)
            except KeyboardInterrupt:
                self.logger.debug("\nRecording stopped.")
                with wave.open(output_file, "wb") as wf:
                    wf.setnchannels(self.CHANNELS)
                    wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                    wf.setframerate(self.RATE)
                    wf.writeframes(b"".join(frames))
                self.logger.debug(f"Audio saved to {output_file}")
        except PermissionError:
            self.logger.warning(
                f"Permission denied: Unable to write to {output_file}"
            )
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
        finally:
            self.close_streams()

    def encrypt_file(
        self, input_file=AUDIO_FILE, output_file=ENCRYPTED_AUDIO_FILE
    ):
        """
        Encrypt an audio file and save the encrypted data to a new file.

        Parameters
        ----------
        input_file : str, optional
            The path to the input audio file to be encrypted (default is "audio.wav").
        output_file : str, optional
            The path to the output file where the encrypted audio will be saved (default is "encrypted_audio.bin").
        """
        # Get the parent directory of the current script
        parent_dir = get_proj_root()
        # Create the target folder path in the parent directory
        output_dir = os.path.join(parent_dir, PATH)
        # Construct the full path for the output file
        output_file_path = os.path.join(
            output_dir, os.path.basename(output_file)
        )
        # Ensure that the path exists, and if doesn't is created.
        ensure_path(str(output_dir))

        # Construct the full path for the input file
        input_file_path = os.path.join(
            output_dir, os.path.basename(input_file)
        )

        # Check if the input file exists
        if not os.path.exists(input_file_path):
            self.logger.error(f"Error: {input_file_path} does not exist.")
            return

        with open(input_file_path, "rb") as f:
            audio_data = f.read()

        crypto_manager = CryptoManager()
        encrypted_data = crypto_manager.encrypt(audio_data)

        with open(output_file_path, "wb") as f:
            f.write(encrypted_data)

        self.logger.debug(f"Encrypted audio saved to {output_file}")

    def decrypt_audio_file(
        self, input_file=ENCRYPTED_AUDIO_FILE, output_file=DECRYPTED_AUDIO_FILE
    ):
        """
        Decrypt an encrypted audio file and save the decrypted audio to a new file.

        Parameters
        ----------
        input_file : str, optional
            The encrypted audio file to decrypt (default is "recorded_audio_encrypted.wav").
        output_file : str, optional
            The name of the output WAV file to save decrypted audio (default is "recorded_audio_decrypted.wav").
        """
        # Get the parent directory of the current script
        parent_dir = get_proj_root()
        # Create the target folder path in the parent directory
        output_dir = os.path.join(parent_dir, PATH)
        # Construct the full path for the output file
        output_file_path = os.path.join(
            output_dir, os.path.basename(output_file)
        )
        # Ensure that the path exists, and if doesn't is created.
        ensure_path(str(output_dir))

        # Construct the full path for the input file
        input_file_path = os.path.join(
            output_dir, os.path.basename(input_file)
        )

        # Check if the input file exists
        if not os.path.exists(input_file_path):
            self.logger.error(f"Error: {input_file_path} does not exist.")
            return

        try:
            self.logger.debug(f"Decrypting {input_file}...")
            # Read encrypted data from the file
            with open(input_file, "rb") as encrypted_file:
                encrypted_data = encrypted_file.read()

            # Decrypt the audio data
            decrypted_data = self.crypto_manager.decrypt(encrypted_data)

            # Write the decrypted data to a WAV file
            with wave.open(output_file, "wb") as wf:
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                wf.setframerate(self.RATE)
                wf.writeframes(decrypted_data)

            self.logger.debug(f"Decrypted audio saved to {output_file}")
        except Exception as e:
            self.logger.error(f"An error occurred during decryption: {e}")

    def decrypt_audio_file_chunked(
        self,
        input_file=ENCRYPTED_AUDIO_STREAM_FILE,
        output_file=DECRYPTED_AUDIO_STREAM_FILE,
    ):
        """
        Decrypt an encrypted audio file (chunked frames) and save the decrypted audio to a new file.

        Parameters
        ----------
        input_file : str, optional
            The encrypted audio file to decrypt (default is "recorded_audio_encrypted.wav").
        output_file : str, optional
            The file to save the decrypted audio (default is "recorded_audio_decrypted.wav").
        """
        # Get the parent directory of the current script
        parent_dir = get_proj_root()
        # Create the target folder path in the parent directory
        output_dir = os.path.join(parent_dir, PATH)
        # Construct the full path for the output file
        output_file_path = os.path.join(
            output_dir, os.path.basename(output_file)
        )
        # Ensure that the path exists, and if doesn't is created.
        ensure_path(str(output_dir))

        # Construct the full path for the input file
        input_file_path = os.path.join(
            output_dir, os.path.basename(input_file)
        )

        # Check if the input file exists
        if not os.path.exists(input_file_path):
            self.logger.error(f"Error: {input_file_path} does not exist.")
            return

        try:
            self.logger.debug(f"Decrypting {input_file}...")
            decrypted_frames = []

            # Open the encrypted audio file
            with wave.open(input_file, "rb") as wf:
                # Get parameters from the encrypted file
                num_channels = wf.getnchannels()
                sample_width = wf.getsampwidth()
                frame_rate = wf.getframerate()
                num_frames = wf.getnframes()

                # Read and decrypt frames chunk by chunk
                for _ in range(0, num_frames, self.CHUNK):
                    encrypted_chunk = wf.readframes(self.CHUNK)
                    decrypted_chunk = self.crypto_manager.decrypt(
                        encrypted_chunk
                    )
                    decrypted_frames.append(decrypted_chunk)

            # Write the decrypted frames to a new WAV file
            with wave.open(output_file, "wb") as wf:
                wf.setnchannels(num_channels)
                wf.setsampwidth(sample_width)
                wf.setframerate(frame_rate)
                wf.writeframes(b"".join(decrypted_frames))

            self.logger.debug(f"Decrypted audio saved to {output_file}")
        except Exception as e:
            self.logger.error(f"An error occurred during decryption: {e}")

    def record_encoded_audio(self):
        """
        Record audio from the microphone, encode it using the Opus codec, and save it to a file.

        This method records audio from the microphone, encodes it using the Opus codec,
        and saves the encoded audio to a file.

        Raises
        ------
        KeyboardInterrupt
            Stops recording when Ctrl+C is pressed.
        """
        # Get the parent directory of the current script
        parent_dir = get_proj_root()
        # Create the target folder path in the parent directory
        output_dir = os.path.join(parent_dir, PATH)
        # Construct the full path for the output file
        output_file = os.path.join(output_dir, "recorded_audio.opus")
        # Ensure that the path exists, and if doesn't is created.
        ensure_path(str(output_dir))

        # Open the input stream
        self.open_input_stream()

        # Open file to write encoded audio
        with open(output_file, "wb") as file:
            print("Recording... Press Ctrl+C to stop.")
            try:
                while True:
                    data = self.input_stream.read(
                        self.CHUNK, exception_on_overflow=False
                    )
                    encoded = self.encoder.encode(data, self.CHUNK)

                    # Write the length of the encoded frame first (to aid decoding)
                    file.write(
                        struct.pack("H", len(encoded))
                    )  # Store frame size (2 bytes)
                    file.write(encoded)  # Store actual Opus frame data
            except KeyboardInterrupt:
                print("\nRecording stopped.")
                # Close input stream
                self.input_stream.stop_stream()
                self.input_stream.close()

    def play_encoded_audio(self):
        """
        Play back audio that has been encoded using the Opus codec.

        This method reads an Opus-encoded audio file, decodes it using the Opus codec,
        and plays back the decoded audio.
        """
        # Get the parent directory of the current script
        parent_dir = get_proj_root()
        # Create the target folder path in the parent directory
        output_dir = os.path.join(parent_dir, PATH)
        # Construct the full path for the output file
        input_file = os.path.join(output_dir, "recorded_audio.opus")

        self.open_output_stream()

        # Open file to read encoded audio
        with open(input_file, "rb") as file:
            encoded_data = file.read()

        # Decode Opus audio
        decoded_frames = []
        offset = 0

        while offset < len(encoded_data):
            try:
                # Read stored frame size first
                frame_size = struct.unpack_from("H", encoded_data, offset)[0]
                offset += 2  # Move past the frame size bytes

                # Extract frame data
                chunk = encoded_data[offset : offset + frame_size]
                offset += frame_size  # Move past the actual frame data

                # Decode the frame
                decoded = self.decoder.decode(chunk, self.CHUNK)
                decoded_frames.append(decoded)
            except (opuslib.exceptions.OpusError, struct.error) as e:
                print(f"Opus decoding error: {e}")
                break

        # Combine all decoded frames
        decoded_audio = b"".join(decoded_frames)

        # Play back the decoded audio
        self.output_stream.write(decoded_audio)

        # Close output stream
        self.output_stream.stop_stream()
        self.output_stream.close()


if __name__ == "__main__":
    tm = ThreadManager()
    handler = AudioManager(
        tm,
        frame_size=960,
        format=pyaudio.paInt16,
        channels=1,
        sample_rate=16000,
        in_device_index=1,
        out_device_index=2,
    )

    print(
        (
            "1. Monitor audio\n"
            "2. Record audio\n"
            "3. Record & encrypt an audio stream\n"
            "4. Discover devices\n"
            "5. Encrypt an audio file\n"
            "6. Decrypt an audio file\n"
            "7. Decrypt an audio stream\n"
            "8. Record & encode audio\n"
            "9. Play encoded audio"
        )
    )

    choice = input("Choose an option (1/2/3/4/5/6/7/8/9/): ").strip()

    try:
        if choice == "1":
            handler.thread_manager.start_thread(
                "Audio Monitor", handler.monitor_audio
            )
            input("Press Enter to stop monitoring.")
            handler.thread_manager.stop_thread("Audio Monitor")
        elif choice == "2":
            handler.record_audio()
        elif choice == "3":
            # handler.record_encrypted_audio()
            choice = input("AES or RSA? (1/2): ").strip()
            if choice == "1":
                handler.record_encrypted_audio()
            elif choice == "2":
                print("Not available yet.")
            else:
                print("Invalid choice.")
        elif choice == "4":
            handler.find_devices()
        elif choice == "5":
            handler.encrypt_file()
        elif choice == "6":
            handler.decrypt_audio_file()
        elif choice == "7":
            choice = input("AES or RSA? (1/2): ").strip()
            if choice == "1":
                handler.decrypt_audio_file_chunked()
            elif choice == "2":
                print("Not available yet.")
            else:
                print("Invalid choice.")
        elif choice == "8":
            handler.record_encoded_audio()
        elif choice == "9":
            handler.play_encoded_audio()
        else:
            print("Invalid choice.")
    finally:
        handler.thread_manager.stop_all_threads()
        handler.terminate()
