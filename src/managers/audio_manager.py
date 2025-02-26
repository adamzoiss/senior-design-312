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
import numpy as np
import os

from src.managers.crypto_manager import CryptoManager
from src.utils.utils import *

# Path and file names for the file types.
PATH = "./audio_files/"
AUDIO_FILE = PATH + "audio.wav"
ENCRYPTED_AUDIO_FILE = PATH + "encrypted_audio.bin"
ENCRYPTED_AUDIO_STREAM_FILE = PATH + "encrypted_audio_stream.wav"
DECRYPTED_AUDIO_FILE = PATH + "decrypted_audio.wav"
DECRYPTED_AUDIO_STREAM_FILE = PATH + "decrypted_audio_stream.wav"
RSA_ENCRYPTED_AUDIO_FILE = PATH + "RSA_encrypted_audio.bin"
RSA_ENCRYPTED_AUDIO_STREAM_FILE = PATH + "RSA_encrypted_audio_stream.wav"
RSA_DECRYPTED_AUDIO_FILE = PATH + "RSA_decrypted_audio.wav"
RSA_DECRYPTED_AUDIO_STREAM_FILE = PATH + "RSA_decrypted_audio_stream.wav"
HYBRID_ENCRYPTED_AUDIO_FILE = PATH + "HYBRID_encrypted_audio.bin"
HYBRID_ENCRYPTED_AUDIO_STREAM_FILE = PATH + "HYBRID_encrypted_audio_stream.wav"
HYBRID_DECRYPTED_AUDIO_FILE = PATH + "HYBRID_decrypted_audio.wav"
HYBRID_DECRYPTED_AUDIO_STREAM_FILE = PATH + "HYBRID_decrypted_audio_stream.wav"


class AudioManager:
    """
    Driver that handles the audio input and output.
    The user must specify the index of the USB mic and headphones.
    To discover what index, run the driver and select option 3.
    """

    def __init__(self):
        """
        Initialize the AudioManager instance and configure default audio settings.
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
        self.CHUNK = 32  # Affects latency for monitoring
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100

        self.audio = pyaudio.PyAudio()
        self.input_device_index = 1  # THIS VALUE CAN CHANGE
        self.output_device_index = 2  # THIS VALUE CAN CHANGE

        self.input_stream = None
        self.output_stream = None

        # Initialize the encryptor with default key paths
        self.encryptor = CryptoManager(
            aes_file="/keys/aes.txt",
            rsa_public_file="/keys/public_key.pem",
            rsa_private_file="/keys/private_key.pem",
            hybrid_file="/keys/hybrid.txt",
            hybrid_public_file="/keys/hybrid_public.pem",
            hybrid_private_file="/keys/hybrid_private.pem"
        )

    def find_devices(self):
        """Display all available audio input and output devices."""
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            print(f"Index {i}: {device_info['name']}")

    def _open_streams(self):
        """Open the audio input and output streams."""
        # Configure and open the input stream
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
            print(f"Encountered exception with input stream: {e}")
        # Configure and open the output stream
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
            print(f"Encountered exception with output stream: {e}")

    def _close_streams(self):
        """Close the audio input and output streams."""
        # Close input steam if it is open
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
        # Close input steam if it is open
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()

    def monitor_audio(self):
        """Continuously monitor and play audio from the microphone."""
        print("Monitoring audio... Press Ctrl+C to stop.")
        self._open_streams()
        try:
            while True:
                data = self.input_stream.read(self.CHUNK, exception_on_overflow=False)
                self.output_stream.write(data)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
        finally:
            self._close_streams()

    def record_audio(self, output_file=AUDIO_FILE, monitoring=False):
        """Record audio from the microphone and save it to a WAV file."""
        # Get the parent directory of the current script
        parent_dir = get_proj_root()
        # Create the target folder path in the parent directory
        output_dir = os.path.join(parent_dir, PATH)
        # Construct the full path for the output file
        output_file_path = os.path.join(output_dir, os.path.basename(output_file))
        # Ensure that the path exists, and if doesn't is created.
        ensure_path(str(output_dir))

        try:
            print("Recording... Press Ctrl+C to stop.")
            self._open_streams()
            frames = []     # List to store recorded frames
            try:
                while True:
                    # Capture audio data from the input stream
                    data = self.input_stream.read(self.CHUNK, exception_on_overflow=False)
                    frames.append(data)
                    # Playback the captured data
                    if monitoring:
                        self.output_stream.write(data)
            except KeyboardInterrupt:
                print("\nRecording stopped.")
                # Save recorded audio to a WAV file
                with wave.open(output_file, "wb") as wf:
                    wf.setnchannels(self.CHANNELS)
                    wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                    wf.setframerate(self.RATE)
                    wf.writeframes(b"".join(frames))
                print(f"Audio saved to {output_file}")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self._close_streams()

    def record_encrypted_audio(self, output_file=ENCRYPTED_AUDIO_STREAM_FILE, monitoring=False):
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
        output_file_path = os.path.join(output_dir, os.path.basename(output_file))
        # Ensure that the path exists, and if doesn't is created.
        ensure_path(str(output_dir))

        try:
            print("Recording... Press Ctrl+C to stop.")
            self._open_streams()
            frames = []
            try:
                while True:
                    data = self.input_stream.read(self.CHUNK, exception_on_overflow=False)
                    encrypted_data = self.encryptor.aes_encrypt(data)
                    frames.append(encrypted_data)
                    if monitoring:
                        self.output_stream.write(data)
            except KeyboardInterrupt:
                print("\nRecording stopped.")
                with wave.open(output_file, "wb") as wf:
                    wf.setnchannels(self.CHANNELS)
                    wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                    wf.setframerate(self.RATE)
                    wf.writeframes(b"".join(frames))
                print(f"Audio saved to {output_file}")
        except PermissionError:
            print(f"Permission denied: Unable to write to {output_file}")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self._close_streams()

    def encrypt_file(self, input_file=AUDIO_FILE, output_file=ENCRYPTED_AUDIO_FILE):
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
        output_file_path = os.path.join(output_dir, os.path.basename(output_file))
        # Construct the full path for the input file
        input_file_path = os.path.join(output_dir, os.path.basename(input_file))
        # Ensure that the path exists, and if doesn't is created.
        ensure_path(str(output_dir))

        # Check if the input file exists
        if not os.path.exists(input_file_path):
            print(f"Error: {input_file_path} does not exist.")
            return

        try:
            with open(input_file_path, "rb") as f:
                audio_data = f.read()

            # Encrypt the audio data
            encrypted_data = self.encryptor.aes_encrypt(audio_data)

            with open(output_file_path, "wb") as f:
                f.write(encrypted_data)

            print(f"Encrypted audio saved to {output_file}")
        except Exception as e:
            print(f"An error occurred during encryption: {e}")

    def decrypt_audio_file(self, input_file=ENCRYPTED_AUDIO_FILE, output_file=DECRYPTED_AUDIO_FILE):
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
        output_file_path = os.path.join(output_dir, os.path.basename(output_file))
        # Construct the full path for the input file
        input_file_path = os.path.join(output_dir, os.path.basename(input_file))
        # Ensure that the path exists, and if doesn't is created.
        ensure_path(str(output_dir))

        # Check if the input file exists
        if not os.path.exists(input_file_path):
            print(f"Error: {input_file_path} does not exist.")
            return

        try:
            print(f"Decrypting {input_file}...")
            # Read encrypted data from the file
            with open(input_file, "rb") as encrypted_file:
                encrypted_data = encrypted_file.read()

            # Decrypt the audio data
            decrypted_data = self.encryptor.aes_decrypt(encrypted_data)

            # Write the decrypted data to a WAV file
            with wave.open(output_file, "wb") as wf:
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                wf.setframerate(self.RATE)
                wf.writeframes(decrypted_data)

            print(f"Decrypted audio saved to {output_file}")
        except Exception as e:
            print(f"An error occurred during decryption: {e}")

    def decrypt_audio_file_chunked(self, input_file=ENCRYPTED_AUDIO_STREAM_FILE, output_file=DECRYPTED_AUDIO_STREAM_FILE):
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
        output_file_path = os.path.join(output_dir, os.path.basename(output_file))
        # Construct the full path for the input file       
        input_file_path = os.path.join(output_dir, os.path.basename(input_file))
        # Ensure that the path exists, and if doesn't is created.
        ensure_path(str(output_dir))

        # Check if the input file exists
        if not os.path.exists(input_file_path):
            print(f"Error: {input_file_path} does not exist.")
            return

        try:
            print(f"Decrypting {input_file}...")
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
                    decrypted_chunk = self.encryptor.aes_decrypt(encrypted_chunk)
                    decrypted_frames.append(decrypted_chunk)

            # Write the decrypted frames to a new WAV file
            with wave.open(output_file, "wb") as wf:
                wf.setnchannels(num_channels)
                wf.setsampwidth(sample_width)
                wf.setframerate(frame_rate)
                wf.writeframes(b"".join(decrypted_frames))

            print(f"Decrypted audio saved to {output_file}")
        except Exception as e:
            print(f"An error occurred during decryption: {e}")

    def encrypt_rsa_file(self, input_file=AUDIO_FILE, output_file=RSA_ENCRYPTED_AUDIO_FILE):
        """
        Encrypt an audio file using RSA and save the encrypted data to a new file.

        Parameters
        ----------
        input_file : str, optional
            The path to the input audio file to be encrypted
        output_file : str, optional
            The path to the output file where the encrypted audio will be saved
        """
        # Get the parent directory of the current script
        parent_dir = get_proj_root()
        output_dir = os.path.join(parent_dir, PATH)
        output_file_path = os.path.join(output_dir, os.path.basename(output_file))
        input_file_path = os.path.join(output_dir, os.path.basename(input_file))
        # Ensure paths exist
        ensure_path(str(output_dir))

        # Check if the input file exists
        if not os.path.exists(input_file_path):
            print(f"Error: Input file {input_file_path} does not exist.")
            print("Please record an audio file first using option 2 (Record audio).")
            return

        try:
            # Read the audio file
            with wave.open(input_file_path, 'rb') as wf:
                # Get audio parameters
                params = {
                    'channels': wf.getnchannels(),
                    'sampwidth': wf.getsampwidth(),
                    'framerate': wf.getframerate()
                }
                # Read audio data
                audio_data = wf.readframes(wf.getnframes())

            # Encrypt the audio data
            encrypted_data = self.encryptor.rsa_encrypt(audio_data)

            # Encrypt the audio data
            with open(output_file_path, "wb") as f:
                f.write(encrypted_data)

            print(f"RSA encrypted audio saved to {output_file}")
        except Exception as e:
            print(f"An error occurred during encryption: {e}")

    def decrypt_rsa_audio_file(self, input_file=RSA_ENCRYPTED_AUDIO_FILE, output_file=RSA_DECRYPTED_AUDIO_FILE):
        """
        Decrypt an RSA encrypted audio file and save the decrypted audio to a new file.

        Parameters
        ----------
        input_file : str, optional
            The encrypted audio file to decrypt
        output_file : str, optional
            The file to save the decrypted audio
        """
        parent_dir = get_proj_root()
        output_dir = os.path.join(parent_dir, PATH)
        output_file_path = os.path.join(output_dir, os.path.basename(output_file))
        input_file_path = os.path.join(output_dir, os.path.basename(input_file))
        # Ensure paths exist
        ensure_path(str(output_dir))

        # Check if the input file exists
        if not os.path.exists(input_file_path):
            print(f"Error: {input_file_path} does not exist.")
            return

        try:
            print(f"Decrypting {input_file}...")
            # Read encrypted data from the file
            with open(input_file_path, "rb") as encrypted_file:
                encrypted_data = encrypted_file.read()

            # Decrypt the audio data
            decrypted_data = self.encryptor.rsa_decrypt(encrypted_data)

            # Write the decrypted data to a WAV file
            with wave.open(output_file_path, "wb") as wf:
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                wf.setframerate(self.RATE)
                wf.writeframes(decrypted_data)

            print(f"Decrypted audio saved to {output_file}")
        except Exception as e:
            print(f"An error occurred during decryption: {e}")

    def encrypt_hybrid_file(self, input_file=AUDIO_FILE, output_file=HYBRID_ENCRYPTED_AUDIO_FILE):
        """
        Encrypt an audio file using hybrid RSA-AES encryption.
        """
        parent_dir = get_proj_root()
        output_dir = os.path.join(parent_dir, PATH)
        output_file_path = os.path.join(output_dir, os.path.basename(output_file))
        input_file_path = os.path.join(output_dir, os.path.basename(input_file))
        ensure_path(str(output_dir))

        if not os.path.exists(input_file_path):
            print(f"Error: Input file {input_file_path} does not exist.")
            print("Please record an audio file first using option 2 (Record audio).")
            return

        try:
            # Read the audio file
            with wave.open(input_file_path, 'rb') as wf:
                params = wf.getparams()._asdict()
                audio_data = wf.readframes(wf.getnframes())

            # Encrypt the audio data
            encrypted_data = self.encryptor.hybrid_encrypt(audio_data)

            if encrypted_data:
                # Save encrypted data
                with open(output_file_path, "wb") as f:
                    f.write(encrypted_data)
                print(f"Hybrid encrypted audio saved to {output_file}")
            else:
                print("Encryption failed")
        except Exception as e:
            print(f"An error occurred during encryption: {e}")

    def decrypt_hybrid_audio_file(self, input_file=HYBRID_ENCRYPTED_AUDIO_FILE, output_file=HYBRID_DECRYPTED_AUDIO_FILE):
        """
        Decrypt a hybrid RSA-AES encrypted audio file.
        """
        parent_dir = get_proj_root()
        output_dir = os.path.join(parent_dir, PATH)
        output_file_path = os.path.join(output_dir, os.path.basename(output_file))
        input_file_path = os.path.join(output_dir, os.path.basename(input_file))
        ensure_path(str(output_dir))

        if not os.path.exists(input_file_path):
            print(f"Error: {input_file_path} does not exist.")
            return

        try:
            print(f"Decrypting {input_file}...")
            # Read the encrypted file
            with open(input_file_path, "rb") as f:
                encrypted_data = f.read()

            # Decrypt the data
            decrypted_data = self.encryptor.hybrid_decrypt(encrypted_data)

            if decrypted_data:
                # Save the decrypted audio
                with wave.open(output_file_path, "wb") as wf:
                    wf.setnchannels(self.CHANNELS)
                    wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                    wf.setframerate(self.RATE)
                    wf.writeframes(decrypted_data)
                print(f"Decrypted audio saved to {output_file}")
            else:
                print("Decryption failed")
        except Exception as e:
            print(f"An error occurred during decryption: {e}")

    def terminate(self):
        """
        Terminate the PyAudio instance.

        This method releases all resources allocated by PyAudio to ensure proper cleanup.
        """
        # Terminate the PyAudio session
        self.audio.terminate()


if __name__ == "__main__":
    handler = AudioManager()
    print("1. Monitor audio")
    print("2. Record audio")
    print("3. Record & encrypt an audio stream")
    print("4. Discover devices")
    print("5. Encrypt an audio file")
    print("6. Decrypt an audio file")
    print("7. Decrypt an audio stream")
    print("8. RSA encrypt audio file")
    print("9. RSA decrypt audio file")
    print("10. Hybrid RSA-AES encrypt audio file")
    print("11. Hybrid RSA-AES decrypt audio file")

    choice = input("Choose an option (1-11): ").strip()

    try:
        if choice == "1":
            handler.monitor_audio()
        elif choice == "2":
            handler.record_audio()
        elif choice == "3":
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
            handler.encrypt_rsa_file()
        elif choice == "9":
            handler.decrypt_rsa_audio_file()
        elif choice == "10":
            handler.encrypt_hybrid_file()
        elif choice == "11":
            handler.decrypt_hybrid_audio_file()
        else:
            print("Invalid choice.")
    finally:
        handler.terminate()