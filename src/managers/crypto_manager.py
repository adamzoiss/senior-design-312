"""
Senior Project : Hardware Encryption Device
Team 312
File : crypto_manager.py
Description: This is the cryptography driver for the project. Encyption and decryption is handled
    through this driver class.
"""

""" AES INFO :
The AES mode being used in the CryptoManager class is CFB (Cipher Feedback) mode.

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

import sys
import numpy as np
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from src.utils.utils import get_proj_root
from src.utils.key_creator import KeyCreator

class CryptoManager:
    """
    Handles encryption and decryption using three different methods:
    1. AES-CFB for stream encryption
    2. RSA for public key encryption
    3. Hybrid RSA-AES for combining the benefits of both

    Attributes
    ----------
    Various keys and IVs loaded from the key_creator utility
    """

    def __init__(
        self,
        aes_file="/keys/aes.txt",
        rsa_public_file="/keys/public_key.pem",
        rsa_private_file="/keys/private_key.pem",
        hybrid_file="/keys/hybrid.txt",
        hybrid_public_file="/keys/hybrid_public.pem",
        hybrid_private_file="/keys/hybrid_private.pem"
    ):
        """
        Initialize the CryptoManager instance.

        Parameters
        ----------
        key_file : str, optional
            Path to the file containing the keys
        """
        root = get_proj_root()
        self.aes_file = root / aes_file.lstrip("/")
        self.rsa_public_file = root / rsa_public_file.lstrip("/")
        self.rsa_private_file = root / rsa_private_file.lstrip("/")
        self.hybrid_file = root / hybrid_file.lstrip("/")
        self.hybrid_public_file = root / hybrid_public_file.lstrip("/")
        self.hybrid_private_file = root / hybrid_private_file.lstrip("/")

        # Create hybrid keys if they don't exist
        creator = KeyCreator()
        try:
            creator.verify_base_keys_exist()
            creator.create_hybrid_keys()
        except Exception as e:
            print(f"Error with key creation: {e}")
            sys.exit(1)

        # Load all keys
        self._initialize_encryption_systems()

    def _initialize_encryption_systems(self):
        """Initialize all encryption systems with their respective keys."""
        try:
            # Load AES keys
            with open(self.aes_file, "r") as f:
                self.aes_key = bytes.fromhex(f.readline().strip())
                self.aes_iv = bytes.fromhex(f.readline().strip())
            self.aes_cipher = Cipher(algorithms.AES(self.aes_key), modes.CFB(self.aes_iv))

            # Load RSA keys
            with open(self.rsa_public_file, "rb") as f:
                self.rsa_public_key = serialization.load_pem_public_key(f.read())
            with open(self.rsa_private_file, "rb") as f:
                self.rsa_private_key = serialization.load_pem_private_key(f.read(), password=None)

            # Load Hybrid keys
            with open(self.hybrid_public_file, "rb") as f:
                self.hybrid_public_key = serialization.load_pem_public_key(f.read())
            with open(self.hybrid_private_file, "rb") as f:
                self.hybrid_private_key = serialization.load_pem_private_key(f.read(), password=None)
            
            # Load and decrypt hybrid AES key
            with open(self.hybrid_file, "rb") as f:
                encrypted_hybrid_keys = f.read()
            decrypted_hybrid_keys = self.hybrid_private_key.decrypt(
                encrypted_hybrid_keys,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            self.hybrid_aes_key = decrypted_hybrid_keys[:32]
            self.hybrid_iv = decrypted_hybrid_keys[32:]
            
            print("All encryption systems initialized successfully.")
        except Exception as e:
            print(f"Error initializing encryption systems: {e}")
            sys.exit(1)

    ############### AES-CFB Methods ###############
    
    def aes_encrypt(self, data):
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
        encryptor = self.aes_cipher.encryptor()
        return encryptor.update(data) + encryptor.finalize()

    def aes_decrypt(self, data):
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
        decryptor = self.aes_cipher.decryptor()
        return decryptor.update(data) + decryptor.finalize()

    ############### RSA Methods ###############

    def rsa_encrypt(self, data):
        """
        Encrypt data using RSA. Handles data chunking for large files.
        """
        try:
            chunk_size = 446  # Maximum size for RSA-4096 with OAEP padding
            chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
            
            encrypted_chunks = []
            for chunk in chunks:
                encrypted_chunk = self.rsa_public_key.encrypt(
                    chunk,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                encrypted_chunks.append(encrypted_chunk)

            return b''.join(encrypted_chunks)
        except Exception as e:
            print(f"RSA encryption error: {e}")
            return None

    def rsa_decrypt(self, encrypted_data):
        """
        Decrypt RSA encrypted data. Handles chunked data.
        """
        try:
            chunk_size = 512  # RSA-4096 encrypted chunk size
            chunks = [encrypted_data[i:i + chunk_size] 
                     for i in range(0, len(encrypted_data), chunk_size)]
            
            decrypted_chunks = []
            for chunk in chunks:
                decrypted_chunk = self.rsa_private_key.decrypt(
                    chunk,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                decrypted_chunks.append(decrypted_chunk)

            return b''.join(decrypted_chunks)
        except Exception as e:
            print(f"RSA decryption error: {e}")
            return None

    ############### Hybrid Methods ###############

    def hybrid_encrypt(self, data):
        """
        Encrypt data using hybrid encryption (RSA + AES).
        """
        try:
            # Use pre-generated hybrid AES key to encrypt the data
            cipher = Cipher(algorithms.AES(self.hybrid_aes_key), modes.CFB(self.hybrid_iv))
            encryptor = cipher.encryptor()
            encrypted_data = encryptor.update(data) + encryptor.finalize()
            
            return encrypted_data
        except Exception as e:
            print(f"Hybrid encryption error: {e}")
            return None

    def hybrid_decrypt(self, encrypted_data):
        """
        Decrypt data using hybrid encryption (RSA + AES).
        """
        try:
            # Use pre-generated hybrid AES key to decrypt the data
            cipher = Cipher(algorithms.AES(self.hybrid_aes_key), modes.CFB(self.hybrid_iv))
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
            
            return decrypted_data
        except Exception as e:
            print(f"Hybrid decryption error: {e}")
            return None

if __name__ == "__main__":
    # Example usage
    print("Crypto Manager Program...")
    crypto = CryptoManager()
    