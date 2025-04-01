from src.utils.utils import *
from src.managers.crypto_manager import CryptoManager
from pathlib import Path
import time

def main():

    # testing AES encryption and decryption speed
    root = get_proj_root
    audio_file = Path("./tests/src/audio/48k_960.wav")

    with audio_file.open("rb") as f:
        audio_data = f.read()

    print("Input: 48k_960.wav")

    crypto = CryptoManager()

    #time the encryption
    start_time = time.perf_counter()
    encrypted = crypto.encrypt(audio_data)
    end_time = time.perf_counter()
    print(f"Encryption time: {end_time - start_time:.10f} seconds")

    #time decryption
    start_time = time.perf_counter()
    decrypted = crypto.decrypt(encrypted)
    end_time = time.perf_counter()
    print(f"Decryption time: {end_time - start_time:.10f} seconds")
    
    #verify if decrypted output matches original input
    if decrypted == audio_data:
        print("Decryption successful, decrypted file matches original")
    else:
        print("Decryption does not match original")

if __name__ == "__main__":
    main()
