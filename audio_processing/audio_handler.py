"""
Senior Project : Hardware Encryption Device
Team 312
File : audio_handler.py
Description: This is the audio driver for the project. By itself it is able to record and monitor
    audio from a usb mic/headphone set. It is also able to encrypt and decrypt.
    The audio file or stream itself may be encrypted and decrypted. This provides a lot of
    flexibility down the line.

"""


import pyaudio
import wave
import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from crypto.crypto_handler import AudioEncryptor

class AudioHandler:
    """
    Driver that handles the audio input and output.
    The user must specify the index of the USB mic and headphones.
    To discover what index, run the driver and select option 3.

    Attributes
    ----------
    CHUNK : uint
        Number of audio frames per buffer. (Lower means less latency)
    FORMAT : pyaudio.paInt16
        Format of audio data (16-bit audio in this case).
    CHANNELS : uint
        Number of audio channels (1 for mono).
    RATE : uint
        Sampling rate in Hz.
    
    audio : pyaudio.PyAudio()
        PyAudio instance for managing audio streams.
    input_device_index : int or None
        Index of the input device.
    output_device_index : int or None
        Index of the output device.
    
    input_stream : pyaudio.Stream or None
        Stream object for audio input.
    output_stream : pyaudio.Stream or None
        Stream object for audio output.
    """
    def __init__(self):
        """
        Initialize the AudioHandler instance and find the input/output devices.
        """
        self.CHUNK = 32 # Affects latency for monitoring
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100

        self.audio = pyaudio.PyAudio()
        self.input_device_index = 1 # THIS VALUE CAN CHANGE
        self.output_device_index = 2 # THIS VALUE CAN CHANGE

        self.input_stream = None
        self.output_stream = None

        # Initialize the encryptor
        self.encryptor = AudioEncryptor()

    def find_devices(self):
        """
        Find the input and output devices connected to the system.
        """
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            print(f"Index {i}: {device_info['name']}")

    def _open_streams(self):
        """
        Open the input and output audio streams.

        This method initializes the streams for capturing and playing audio.
        """
        self.input_stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            input_device_index=self.input_device_index,
            frames_per_buffer=self.CHUNK,
        )

        self.output_stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            output=True,
            output_device_index=self.output_device_index,
            frames_per_buffer=self.CHUNK,
        )

    def _close_streams(self):
        """
        Close the input and output audio streams.

        This method ensures that resources are properly released.
        """
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()

    def monitor_audio(self):
        """
        Continuously monitor and play audio from the microphone.

        This method plays the audio captured from the microphone through the output device.

        Raises
        ------
        KeyboardInterrupt
            Stops monitoring when Ctrl+C is pressed.
        """
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

    def record_audio(self, output_file="recorded_audio.wav"):
        if os.path.exists(output_file):
            overwrite = input(f"{output_file} exists. Overwrite? (y/n): ").strip().lower()
            if overwrite != 'y':
                print("Recording canceled.")
                return

        try:
            print("Recording... Press Ctrl+C to stop.")
            self._open_streams()
            frames = []
            try:
                while True:
                    data = self.input_stream.read(self.CHUNK, exception_on_overflow=False)
                    frames.append(data)
                    self.output_stream.write(data)
            except KeyboardInterrupt:
                print("\nRecording stopped.")
                with wave.open(output_file, 'wb') as wf:
                    wf.setnchannels(self.CHANNELS)
                    wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                    wf.setframerate(self.RATE)
                    wf.writeframes(b''.join(frames))
                print(f"Audio saved to {output_file}")
        except PermissionError:
            print(f"Permission denied: Unable to write to {output_file}")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self._close_streams()

    def record_encrypted_audio(self, output_file="recorded_audio_encrypted.wav"):
        
        if os.path.exists(output_file):
            overwrite = input(f"{output_file} exists. Overwrite? (y/n): ").strip().lower()
            if overwrite != 'y':
                print("Recording canceled.")
                return

        try:
            print("Recording... Press Ctrl+C to stop.")
            self._open_streams()
            frames = []
            try:
                while True:
                    data = self.input_stream.read(self.CHUNK, exception_on_overflow=False)
                    encrypted_data = self.encryptor.encrypt(data)
                    frames.append(encrypted_data)
                    self.output_stream.write(data)
            except KeyboardInterrupt:
                print("\nRecording stopped.")
                with wave.open(output_file, 'wb') as wf:
                    wf.setnchannels(self.CHANNELS)
                    wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                    wf.setframerate(self.RATE)
                    wf.writeframes(b''.join(frames))
                print(f"Audio saved to {output_file}")
        except PermissionError:
            print(f"Permission denied: Unable to write to {output_file}")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self._close_streams()

    def decrypt_audio_file(self, input_file="recorded_audio_encrypted.wav", output_file="recorded_audio_decrypted.wav"):
        """
        Decrypt an encrypted audio file and save the decrypted audio to a new file.

        Parameters
        ----------
        input_file : str, optional
            The encrypted audio file to decrypt (default is "recorded_audio_encrypted.wav").
        output_file : str, optional
            The file to save the decrypted audio (default is "recorded_audio_decrypted.wav").
        """
        if not os.path.exists(input_file):
            print(f"Error: {input_file} does not exist.")
            return

        if os.path.exists(output_file):
            overwrite = input(f"{output_file} exists. Overwrite? (y/n): ").strip().lower()
            if overwrite != 'y':
                print("Decryption canceled.")
                return

        try:
            print(f"Decrypting {input_file}...")
            with open(input_file, 'rb') as encrypted_file:
                encrypted_data = encrypted_file.read()

            decrypted_data = self.encryptor.decrypt(encrypted_data)

            # Write the decrypted data to a WAV file
            with wave.open(output_file, 'wb') as wf:
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                wf.setframerate(self.RATE)
                wf.writeframes(decrypted_data)

            print(f"Decrypted audio saved to {output_file}")
        except Exception as e:
            print(f"An error occurred during decryption: {e}")

    def decrypt_audio_file_chunked(self, input_file="recorded_audio_encrypted.wav", output_file="recorded_audio_decrypted.wav"):
        """
        Decrypt an encrypted audio file (chunked frames) and save the decrypted audio to a new file.

        Parameters
        ----------
        input_file : str, optional
            The encrypted audio file to decrypt (default is "recorded_audio_encrypted.wav").
        output_file : str, optional
            The file to save the decrypted audio (default is "recorded_audio_decrypted.wav").
        """
        if not os.path.exists(input_file):
            print(f"Error: {input_file} does not exist.")
            return

        if os.path.exists(output_file):
            overwrite = input(f"{output_file} exists. Overwrite? (y/n): ").strip().lower()
            if overwrite != 'y':
                print("Decryption canceled.")
                return

        try:
            print(f"Decrypting {input_file}...")
            decrypted_frames = []

            # Open the encrypted audio file
            with wave.open(input_file, 'rb') as wf:
                # Get parameters from the encrypted file
                num_channels = wf.getnchannels()
                sample_width = wf.getsampwidth()
                frame_rate = wf.getframerate()
                num_frames = wf.getnframes()

                # Read and decrypt frames chunk by chunk
                for _ in range(0, num_frames, self.CHUNK):
                    encrypted_chunk = wf.readframes(self.CHUNK)
                    decrypted_chunk = self.encryptor.decrypt(encrypted_chunk)
                    decrypted_frames.append(decrypted_chunk)

            # Write the decrypted frames to a new WAV file
            with wave.open(output_file, 'wb') as wf:
                wf.setnchannels(num_channels)
                wf.setsampwidth(sample_width)
                wf.setframerate(frame_rate)
                wf.writeframes(b''.join(decrypted_frames))

            print(f"Decrypted audio saved to {output_file}")
        except Exception as e:
            print(f"An error occurred during decryption: {e}")




    def terminate(self):
        """
        Terminate the PyAudio instance.

        This method releases all resources allocated by PyAudio.
        """
        self.audio.terminate()


if __name__ == "__main__":
    handler = AudioHandler()
    print("1. Monitor audio")
    print("2. Record audio")
    print("3. Discover device")
    print("4. Monitor encrypted audio")
    print("5. Encrypt an audio file")
    print("6. Decrypt an audio file")
    print("7. Record encrypted file")

    choice = input("Choose an option (1/2/3/4/5/6): ").strip()

    try:
        if choice == "1":
            handler.monitor_audio()
        elif choice == "2":
            handler.record_audio()
        elif choice == "3":
            handler.find_devices()
        elif choice == "4":
            handler.monitor_audio_encrypted()
        elif choice == "5":
            input_file = input("Enter the input audio file (e.g., 'input.wav'): ").strip()
            output_file = input("Enter the output encrypted file (e.g., 'encrypted_audio.bin'): ").strip()

            with open(input_file, "rb") as f:
                audio_data = f.read()

            encryptor = AudioEncryptor()
            encrypted_data = encryptor.encrypt(audio_data)

            with open(output_file, "wb") as f:
                f.write(encrypted_data)

            print(f"Encrypted audio saved to {output_file}")

        elif choice == "6":
            encrypted_file = input("Enter the encrypted audio file (e.g., 'encrypted_audio.bin'): ").strip()
            output_file = input("Enter the output decrypted file (e.g., 'decrypted_audio.wav'): ").strip()

            with open(encrypted_file, "rb") as f:
                encrypted_data = f.read()

            encryptor = AudioEncryptor()
            decrypted_data = encryptor.decrypt(encrypted_data)

            with open(output_file, "wb") as f:
                f.write(decrypted_data)

            print(f"Decrypted audio saved to {output_file}")
        elif choice == "7":
            handler.record_encrypted_audio()
        elif choice == "8":
            handler.decrypt_audio_file_chunked()

        else:
            print("Invalid choice.")
    finally:
        handler.terminate()
