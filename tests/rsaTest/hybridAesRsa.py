# I had to do pip install pydub simpleaudio and pip install playsound

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Generate RSA keys
private_key = rsa.generate_private_key(
    public_exponent=65537, key_size=4096, backend=default_backend()
)
public_key = private_key.public_key()

# Save private key
with open("private_key.pem", "wb") as f:
    f.write(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )

# Save public key
with open("public_key.pem", "wb") as f:
    f.write(
        public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )

import os
import wave
import time
from pydub import AudioSegment
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
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

    # Record audio
    recording = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=2,
        dtype="int16",
    )
    sd.wait()  # Wait until recording is finished
    print("Recording finished!")

    # Save as WAV file
    temp_filename = "recorded_audio.wav"
    wavfile.write(temp_filename, sample_rate, recording)

    return temp_filename


def encrypt_audio_hybrid(file_path, public_key_path):
    try:
        # Load the public key
        with open(public_key_path, "rb") as f:
            public_key = serialization.load_pem_public_key(
                f.read(), backend=default_backend()
            )

        # Generate AES key
        aes_key = os.urandom(32)

        # Generate a random IV for GCM mode
        iv = os.urandom(12)  # GCM mode typically uses a 12-byte IV

        # Encrypt AES key with RSA
        encrypted_key = public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        # Read the audio file
        with wave.open(file_path, "rb") as wave_file:
            params = wave_file.getparams()
            audio_data = wave_file.readframes(wave_file.getnframes())

        # Encrypt audio data with AES-GCM
        cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv))
        encryptor = cipher.encryptor()
        encrypted_audio = encryptor.update(audio_data) + encryptor.finalize()

        # Save the encrypted data
        with open("encrypted_audio.bin", "wb") as f:
            # Save the IV
            f.write(iv)
            # Save the GCM tag
            f.write(encryptor.tag)
            # Save the encrypted AES key
            f.write(len(encrypted_key).to_bytes(4, "big"))
            f.write(encrypted_key)
            # Save audio parameters
            params_str = f"{params.nchannels},{params.sampwidth},{params.framerate},{params.nframes}".encode()
            f.write(len(params_str).to_bytes(4, "big"))
            f.write(params_str)
            # Save encrypted audio
            f.write(encrypted_audio)

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


def decrypt_audio_hybrid(encrypted_audio_path, private_key_path):
    try:
        # Load the private key
        with open(private_key_path, "rb") as f:
            private_key = serialization.load_pem_private_key(
                f.read(), password=None, backend=default_backend()
            )

        # Read the encrypted data
        with open(encrypted_audio_path, "rb") as f:
            # Read IV and tag
            iv = f.read(12)  # 12-byte IV for GCM
            tag = f.read(16)  # 16-byte authentication tag
            # Read encrypted AES key
            key_len = int.from_bytes(f.read(4), "big")
            encrypted_key = f.read(key_len)
            # Read audio parameters
            params_len = int.from_bytes(f.read(4), "big")
            params = f.read(params_len).decode().split(",")
            nchannels, sampwidth, framerate, nframes = map(int, params)
            # Read encrypted audio
            encrypted_audio = f.read()

        # Decrypt the AES key
        aes_key = private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        # Decrypt the audio data
        cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv, tag))
        decryptor = cipher.decryptor()
        decrypted_audio = (
            decryptor.update(encrypted_audio) + decryptor.finalize()
        )

        # Save as WAV
        with wave.open("decrypted_audio.wav", "wb") as wave_file:
            wave_file.setnchannels(nchannels)
            wave_file.setsampwidth(sampwidth)
            wave_file.setframerate(framerate)
            wave_file.writeframes(decrypted_audio)

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

    if encrypt_audio_hybrid(audio_file_path, "public_key.pem"):
        print("Encryption completed successfully")

        # Play the encrypted data (will sound like noise)
        print("\nPlaying encrypted audio (should sound like noise)...")
        try:
            with wave.open("temp_encrypted.wav", "wb") as wave_file:
                wave_file.setnchannels(2)
                wave_file.setsampwidth(2)
                wave_file.setframerate(44100)

                # Read encrypted data and ensure it's a valid length
                with open("encrypted_audio.bin", "rb") as f:
                    # Skip header information
                    f.read(12)  # IV
                    f.read(16)  # tag
                    key_len = int.from_bytes(f.read(4), "big")
                    f.read(key_len)  # encrypted key
                    params_len = int.from_bytes(f.read(4), "big")
                    f.read(params_len)  # params
                    encrypted_data = f.read()

                    # Ensure we have valid audio data length
                    if len(encrypted_data) % 2 != 0:
                        encrypted_data = encrypted_data[:-1]

                    # Normalize the entire encrypted data
                    normalized_data = bytes([x % 128 for x in encrypted_data])
                    # Write the entire normalized data
                    wave_file.writeframes(normalized_data)

            print("Playing encrypted audio...")
            # Create AudioSegment for volume control
            encrypted_sound = AudioSegment.from_wav("temp_encrypted.wav")
            # Adjust volume (you can modify this value if needed)
            encrypted_sound = encrypted_sound + 5  # Increased by 5 dB
            encrypted_sound.export("temp_encrypted_loud.wav", format="wav")

            wave_obj = sa.WaveObject.from_wave_file("temp_encrypted_loud.wav")
            play_obj = wave_obj.play()
            play_obj.wait_done()
            time.sleep(1)

        except Exception as e:
            print(f"Error playing encrypted audio: {e}")
            print("Continuing with decryption...")

        # Clean up temporary files
        for temp_file in ["temp_encrypted.wav", "temp_encrypted_loud.wav"]:
            if os.path.exists(temp_file):
                os.remove(temp_file)

        print("\nNow decrypting...")
        time.sleep(1)

        if decrypt_audio_hybrid("encrypted_audio.bin", "private_key.pem"):
            print("Decryption completed successfully")
            print("\nPlaying decrypted audio...")
            try:
                wave_obj = sa.WaveObject.from_wave_file("decrypted_audio.wav")
                play_obj = wave_obj.play()
                play_obj.wait_done()
            except Exception as e:
                print(f"Error playing decrypted audio: {e}")

except Exception as e:
    print(f"An error occurred: {e}")
    traceback.print_exc()

finally:
    # Clean up temporary files
    for temp_file in [
        "recorded_audio.wav",
        "temp_encrypted.wav",
        "temp_encrypted_loud.wav",
    ]:
        if os.path.exists(temp_file):
            os.remove(temp_file)
