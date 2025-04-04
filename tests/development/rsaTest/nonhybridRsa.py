from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Generate RSA keys
private_key = rsa.generate_private_key(
    public_exponent=65537, key_size=4096, backend=default_backend()
)
public_key = private_key.public_key()

# Save private key
private_key_file = "tests/rsaTest/private_key.pem"
with open(private_key_file, "wb") as f:
    f.write(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )

# Save public key
private_key_path = "tests/rsaTest/public_key.pem"
with open(private_key_path, "wb") as f:
    f.write(
        public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )

import os
import base64
import secrets
import wave
import time
from pydub import AudioSegment
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import simpleaudio as sa
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
import traceback


def record_audio(duration=3, sample_rate=44100):
    print(f"\nRecording will start in 3 seconds...")
    time.sleep(3)
    print("Recording...")

    recording = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="int16",
    )
    sd.wait()
    print("Recording finished!")

    temp_filename = "tests/rsaTest/recorded_audio.wav"
    wavfile.write(temp_filename, sample_rate, recording)

    return temp_filename


def encrypt_audio(file_path, public_key_path):
    try:
        # Load the public key
        with open(public_key_path, "rb") as f:
            public_key = serialization.load_pem_public_key(
                f.read(), backend=default_backend()
            )

        # Read the audio file
        with wave.open(file_path, "rb") as wave_file:
            # Get audio parameters
            nchannels = wave_file.getnchannels()
            sampwidth = wave_file.getsampwidth()
            framerate = wave_file.getframerate()

            # Read audio data
            audio_data = wave_file.readframes(wave_file.getnframes())

        # Convert to numpy array for better handling
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        audio_bytes = audio_array.tobytes()

        # Create header with audio parameters
        header = (
            f"{nchannels},{sampwidth},{framerate},{len(audio_array)}".encode()
        )
        header_len = len(header).to_bytes(4, "big")

        # Combine header and audio data
        data_to_encrypt = header_len + header + audio_bytes

        # Split into chunks and encrypt
        # Reduce chunk size to account for length prefix (2 bytes)
        chunk_size = 444  # 446 - 2 bytes for length prefix
        chunks = [
            data_to_encrypt[i : i + chunk_size]
            for i in range(0, len(data_to_encrypt), chunk_size)
        ]

        encrypted_chunks = []
        total_chunks = len(chunks)
        for i, chunk in enumerate(chunks, 1):
            print(f"Encrypting chunk {i}/{total_chunks}")

            # Add length prefix to chunk
            chunk_length = len(chunk).to_bytes(2, "big")
            chunk_with_length = chunk_length + chunk

            # No need for additional padding as OAEP padding will handle it
            encrypted_chunk = public_key.encrypt(
                chunk_with_length,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )
            encrypted_chunks.append(encrypted_chunk)

        # Combine all encrypted chunks
        encrypted_data = b"".join(encrypted_chunks)

        # Save encrypted data
        with open("tests/rsaTest/encrypted_audio.bin", "wb") as f:
            f.write(encrypted_data)

        print("\nPlaying original audio...")
        wave_obj = sa.WaveObject.from_wave_file(file_path)
        play_obj = wave_obj.play()
        play_obj.wait_done()
        time.sleep(1)

        return True

    except Exception as e:
        print(f"Encryption error: {e}")
        traceback.print_exc()
        return False


def decrypt_audio(encrypted_audio_path, private_key_path):
    try:
        # Load the private key
        with open(private_key_path, "rb") as f:
            private_key = serialization.load_pem_private_key(
                f.read(), password=None, backend=default_backend()
            )

        # Read encrypted data
        with open(encrypted_audio_path, "rb") as f:
            encrypted_data = f.read()

        # Split into chunks and decrypt
        chunk_size = 512  # RSA-4096 encrypted chunk size
        encrypted_chunks = [
            encrypted_data[i : i + chunk_size]
            for i in range(0, len(encrypted_data), chunk_size)
        ]

        decrypted_chunks = []
        total_chunks = len(encrypted_chunks)
        for i, chunk in enumerate(encrypted_chunks, 1):
            print(f"Decrypting chunk {i}/{total_chunks}")

            # Decrypt the chunk
            decrypted_chunk = private_key.decrypt(
                chunk,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None,
                ),
            )

            # Extract original length and data
            chunk_length = int.from_bytes(decrypted_chunk[:2], "big")
            actual_data = decrypted_chunk[2 : 2 + chunk_length]
            decrypted_chunks.append(actual_data)

        # Combine all decrypted chunks
        decrypted_data = b"".join(decrypted_chunks)

        # Extract header
        header_len = int.from_bytes(decrypted_data[:4], "big")
        header = decrypted_data[4 : 4 + header_len].decode().split(",")
        nchannels, sampwidth, framerate, nsamples = map(int, header)

        # Extract audio data
        audio_bytes = decrypted_data[4 + header_len :]

        # Convert to numpy array
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16)

        # Ensure correct number of samples
        audio_array = audio_array[:nsamples]

        # Save as WAV
        with wave.open("tests/rsaTest/decrypted_audio.wav", "wb") as wave_file:
            wave_file.setnchannels(nchannels)
            wave_file.setsampwidth(sampwidth)
            wave_file.setframerate(framerate)
            wave_file.writeframes(audio_array.tobytes())

        return True

    except Exception as e:
        print(f"Decryption error: {e}")
        traceback.print_exc()
        return False


# Main execution
try:
    # Record the audio
    print(
        "This program will record your voice, encrypt it, play the encrypted version, and then decrypt it."
    )
    audio_file_path = record_audio(duration=3)  # Records for 3 seconds

    if encrypt_audio(audio_file_path, private_key_path):
        print("Encryption completed successfully")

        # Play the encrypted data (will sound like noise)
        print("\nPlaying encrypted audio (should sound like noise)...")
        with wave.open("tests/rsaTest/temp_encrypted.wav", "wb") as wave_file:
            wave_file.setnchannels(1)
            wave_file.setsampwidth(2)
            wave_file.setframerate(44100)

            # Read encrypted data and ensure it's a valid length
            with open("encrypted_audio.bin", "rb") as f:
                encrypted_data = f.read()
                # Ensure the data length is even
                if len(encrypted_data) % 2 != 0:
                    encrypted_data = encrypted_data[:-1]
                wave_file.writeframes(
                    encrypted_data[: len(encrypted_data) // 4]
                )

        try:
            # Play at reduced volume
            print("Playing encrypted audio at reduced volume...")
            wave_obj = sa.WaveObject.from_wave_file(
                "tests/rsaTest/temp_encrypted.wav"
            )
            play_obj = wave_obj.play()
            play_obj.wait_done()
            time.sleep(1)
        except Exception as e:
            print(f"Error playing encrypted audio: {e}")

        # Clean up temporary file
        if os.path.exists("tests/rsaTest/temp_encrypted.wav"):
            os.remove("tests/rsaTest/temp_encrypted.wav")

        print("\nNow decrypting...")
        time.sleep(1)

        if decrypt_audio("encrypted_audio.bin", private_key_file):
            print("Decryption completed successfully")
            print("\nPlaying decrypted audio...")
            try:
                wave_obj = sa.WaveObject.from_wave_file(
                    "tests/rsaTest/decrypted_audio.wav"
                )
                play_obj = wave_obj.play()
                play_obj.wait_done()
            except Exception as e:
                print(f"Error playing decrypted audio: {e}")

finally:
    # Clean up the recorded audio file
    if os.path.exists("tests/rsaTest/recorded_audio.wav"):
        os.remove("tests/rsaTest/recorded_audio.wav")
