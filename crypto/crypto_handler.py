"""
Senior Project : Hardware Encryption Device
Team 312
File : crypto_handler.py
Description: This is the cryptography driver for the project. Encyption and decryption is handled
    through this driver class.
"""


""" AES INFO :
The AES mode being used in the CryptoHandler class is CFB (Cipher Feedback) mode.

Characteristics of CFB Mode:
    Stream Cipher Emulation:
        CFB mode turns a block cipher like AES into a stream cipher.
        This is useful for encrypting data of arbitrary length, such as audio streams.
    Chaining:
        CFB uses feedback from previous encryption to influence the next block.
        It ensures that identical plaintext blocks produce different ciphertext blocks (assuming a unique IV).
    No Padding Needed:
        Since CFB works on data streams, no padding is required for the plaintext.
    Initialization Vector (IV):
        A unique IV is crucial for ensuring security.
        In the class, a random 16-byte IV is generated (os.urandom(16)) and used.
    Error Propagation:
        Errors in the ciphertext will propagate for the duration of one block size, affecting both encryption and decryption.

Why CFB for Audio?
    CFB mode is suitable for audio streaming because:
        It allows encryption and decryption of partial blocks, making it efficient for real-time processing.
        The lack of padding simplifies the processing pipeline for continuous audio streams.

Other modes:
    GCM (provides integrity/authentication)
    CTR (better parallelism and performance).

"""


from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os


class CryptoHandler:
    """
    Handles AES encryption and decryption of audio streams using a key and IV from a file.

    Attributes
    ----------
    key : bytes
        The AES key for encryption and decryption.
    iv : bytes
        The initialization vector (IV) for encryption and decryption.
    cipher : Cipher
        The AES cipher for encryption and decryption.
    """
    def __init__(self, key_file="key_iv.txt"):
        """
        Initialize the CryptoHandler instance.

        Parameters
        ----------
        key_file : str, optional
            Path to the file containing the AES key and IV.
        """
        self.key_file = key_file
        self.key, self.iv = self._load_or_generate_key_iv()
        self.cipher = Cipher(algorithms.AES(self.key), modes.CFB(self.iv))

    def _load_or_generate_key_iv(self):
        """
        Load the AES key and IV from a file, or generate and save them if the file does not exist.

        Returns
        -------
        tuple
            A tuple containing the AES key (bytes) and IV (bytes).
        """
        if os.path.exists(self.key_file):
            with open(self.key_file, "r") as f:
                key = bytes.fromhex(f.readline().strip())
                iv = bytes.fromhex(f.readline().strip())
                print("Key and IV loaded from file.")
        else:
            key = os.urandom(32)  # AES-256 key
            iv = os.urandom(16)  # IV
            with open(self.key_file, "w") as f:
                f.write(key.hex() + "\n")
                f.write(iv.hex() + "\n")
            print("Key and IV generated and saved to file.")
        return key, iv

    def encrypt(self, data):
        """
        Encrypt the given audio data.

        Parameters
        ----------
        data : bytes
            The audio data to encrypt.

        Returns
        -------
        bytes
            Encrypted audio data.
        """
        encryptor = self.cipher.encryptor()
        return encryptor.update(data) + encryptor.finalize()

    def decrypt(self, data):
        """
        Decrypt the given encrypted audio data.

        Parameters
        ----------
        data : bytes
            The encrypted audio data to decrypt.

        Returns
        -------
        bytes
            Decrypted audio data.
        """
        decryptor = self.cipher.decryptor()
        return decryptor.update(data) + decryptor.finalize()


if __name__ == "__main__":
    print('Crypto Handler Program...')
    crypto = CryptoHandler()