from src.utils.utils import *

from src.managers.crypto_manager import CryptoManager

def main():
    audio_file = Path("./tests/rsaTest/recorded_audio.wav")

    with audio_file.open("rb") as f:
        audio_data = f.read()

    crypto = CryptoManager()

    encrypted = crypto.encrypt(audio_data)

    decrypted = crypto.decrypt(encrypted)

    if decrypted == audio_data:
        print("Decryption successful, decrypted file matches original")
    else:
        print("Decryption does not match original")

if __name__ == "__main__":
    main()
