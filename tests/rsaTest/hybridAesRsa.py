from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import os
import wave
import time
from pydub import AudioSegment
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import numpy as np
import scipy.io.wavfile as wavfile
import traceback
import pyaudio

# Generate RSA keys
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=4096,
    backend=default_backend()
)
public_key = private_key.public_key()

# Save private key
with open("private_key.pem", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

# Save public key
with open("public_key.pem", "wb") as f:
    f.write(public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ))

def record_audio(duration=3, sample_rate=44100):
    print(f"\nRecording will start in 3 seconds...")
    time.sleep(3)
    print("Recording...")
    
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    
    p = pyaudio.PyAudio()
    
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=CHUNK)
    
    frames = []
    
    # Record for specified duration
    for i in range(0, int(sample_rate / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)
    
    print("Recording finished!")
    
    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # Save the recorded data as a WAV file
    temp_filename = "recorded_audio.wav"
    wf = wave.open(temp_filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()
    
    return temp_filename

def play_audio(filename):
    # Helper function to play audio files
    CHUNK = 1024
    
    wf = wave.open(filename, 'rb')
    p = pyaudio.PyAudio()
    
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    
    data = wf.readframes(CHUNK)
    while data:
        stream.write(data)
        data = wf.readframes(CHUNK)
    
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf.close()

def encrypt_audio_hybrid(file_path, public_key_path):
    try:
        # Load the public key
        with open(public_key_path, "rb") as f:
            public_key = serialization.load_pem_public_key(f.read(), backend=default_backend())

        # Generate AES key
        aes_key = os.urandom(32)
        
        # Generate a random IV for GCM mode
        iv = os.urandom(12)
        
        # Encrypt AES key with RSA
        encrypted_key = public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Read the audio file
        with wave.open(file_path, 'rb') as wave_file:
            params = wave_file.getparams()
            audio_data = wave_file.readframes(wave_file.getnframes())

        # Encrypt audio data with AES-GCM
        cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv))
        encryptor = cipher.encryptor()
        encrypted_audio = encryptor.update(audio_data) + encryptor.finalize()
        
        # Save the encrypted data
        with open("encrypted_audio.bin", "wb") as f:
            f.write(iv)
            f.write(encryptor.tag)
            f.write(len(encrypted_key).to_bytes(4, 'big'))
            f.write(encrypted_key)
            params_str = f"{params.nchannels},{params.sampwidth},{params.framerate},{params.nframes}".encode()
            f.write(len(params_str).to_bytes(4, 'big'))
            f.write(params_str)
            f.write(encrypted_audio)

        print("\nPlaying original audio...")
        play_audio(file_path)
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
            private_key = serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())

        # Read the encrypted data
        with open(encrypted_audio_path, "rb") as f:
            iv = f.read(12)
            tag = f.read(16)
            key_len = int.from_bytes(f.read(4), 'big')
            encrypted_key = f.read(key_len)
            params_len = int.from_bytes(f.read(4), 'big')
            params = f.read(params_len).decode().split(',')
            nchannels, sampwidth, framerate, nframes = map(int, params)
            encrypted_audio = f.read()

        # Decrypt the AES key
        aes_key = private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Decrypt the audio data
        cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv, tag))
        decryptor = cipher.decryptor()
        decrypted_audio = decryptor.update(encrypted_audio) + decryptor.finalize()

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
    print("This program will record your voice, encrypt it, play the encrypted version, and then decrypt it.")
    audio_file_path = record_audio(duration=3)
    
    if encrypt_audio_hybrid(audio_file_path, "public_key.pem"):
        print("Encryption completed successfully")
        
        print("\nPlaying encrypted audio (should sound like noise)...")
        with wave.open("temp_encrypted.wav", "wb") as wave_file:
            wave_file.setnchannels(2)
            wave_file.setsampwidth(2)
            wave_file.setframerate(44100)
            
            with open("encrypted_audio.bin", "rb") as f:
                f.read(12)  # IV
                f.read(16)  # tag
                key_len = int.from_bytes(f.read(4), 'big')
                f.read(key_len)  # encrypted key
                params_len = int.from_bytes(f.read(4), 'big')
                f.read(params_len)  # params
                encrypted_data = f.read()
                
                if len(encrypted_data) % 2 != 0:
                    encrypted_data = encrypted_data[:-1]
                
                normalized_data = bytes([x % 128 for x in encrypted_data])
                wave_file.writeframes(normalized_data)

        try:
            print("Playing encrypted audio...")
            play_audio("temp_encrypted.wav")
            time.sleep(1)
            
        except Exception as e:
            print(f"Error playing encrypted audio: {e}")
            print("Continuing with decryption...")
        
        if os.path.exists("temp_encrypted.wav"):
            os.remove("temp_encrypted.wav")
        
        print("\nNow decrypting...")
        time.sleep(1)
        
        if decrypt_audio_hybrid("encrypted_audio.bin", "private_key.pem"):
            print("Decryption completed successfully")
            print("\nPlaying decrypted audio...")
            try:
                play_audio("decrypted_audio.wav")
            except Exception as e:
                print(f"Error playing decrypted audio: {e}")

except Exception as e:
    print(f"An error occurred: {e}")
    traceback.print_exc()

finally:
    # Clean up temporary files
    for temp_file in ["recorded_audio.wav", "temp_encrypted.wav"]:
        if os.path.exists(temp_file):
            os.remove(temp_file)    