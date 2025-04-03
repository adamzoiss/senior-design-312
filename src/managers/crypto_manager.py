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
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

from src.utils.utils import *
from src.utils.constants import PACKET_ENCRYPTION, DATA_ENCRYPTION
from src.logging.logger import *


class CryptoManager:
    """
    Handles encryption and decryption using three different methods:
    1. AES-CFB for stream encryption
    2. RSA for public key encryption
    3. Hybrid RSA-AES for combining the benefits of both

    Attributes
    ----------
    key : bytes
        The AES key for encryption and decryption.
    iv : bytes
        The initialization vector (IV) for encryption and decryption.
    cipher : Cipher
        The AES cipher for encryption and decryption.
    """

    def __init__(
        self,
        key_file="/keys/aes.txt",
        public_key_file="/keys/public_key.pem",
        private_key_file="/keys/private_key.pem",
        hybrid_file="/keys/hybrid.txt",
        hybrid_public_file="/keys/hybrid_public.pem",
        hybrid_private_file="/keys/hybrid_private.pem",
    ):
        """
        Initialize the CryptoManager instance.

        Parameters
        ----------
        key_file : str, optional
            Path to the file containing the AES key and IV.
        """
        # Set up logging
        self.logger: logging = Logger(
            "CryptoManager",
            console_level=logging.INFO,
            console_logging=EN_CONSOLE_LOGGING,
        )

        # Setting up the RSA keys
        self.key_file = str(get_proj_root()) + key_file
        self.private_key_file = str(get_proj_root()) + private_key_file
        self.public_key_file = str(get_proj_root()) + public_key_file
        self.hybrid_file = str(get_proj_root()) + hybrid_file
        self.hybrid_public_file = str(get_proj_root()) + hybrid_public_file
        self.hybrid_private_file = str(get_proj_root()) + hybrid_private_file

        # Setting up the AES key and IV
        self.key, self.iv = self._load_key_iv()
        self.public_key, self.private_key = self._load_rsa_keys()
        self.hybrid_public_key, self.hybrid_private_key = self._load_hybrid_keys()
        self.hybrid_aes_key, self.hybrid_iv = self._load_hybrid_aes_key()
        
        self.cipher = Cipher(algorithms.AES(self.key), modes.CFB(self.iv))
        self.hybrid_cipher = Cipher(algorithms.AES(self.hybrid_aes_key), modes.CFB(self.hybrid_iv))

        # Dictates if Encyption is enabled or not
        self.penc_en = PACKET_ENCRYPTION
        self.denc_en = DATA_ENCRYPTION

        self.logger.info("CryptoManager initialized")

    def _load_key_iv(self):
        """
        Load the AES key and IV from a file.

        Returns
        -------
        tuple
            A tuple containing the AES key (bytes) and IV (bytes).
        """
        try:
            with open(self.key_file, "r") as f:
                key = bytes.fromhex(f.readline().strip())
                iv = bytes.fromhex(f.readline().strip())
                self.logger.debug("Key and IV loaded from file.")
                return key, iv
        except Exception as e:
            self.logger.error(f"Exception thrown: {e}\nExiting program...")
            sys.exit()

    def _load_rsa_keys(self):
        """
        Load the RSA public and private keys from files.

        Returns
        -------
        tuple
            A tuple containing the RSA public key and private key.
        """
        try:
            with open(self.public_key_file, "rb") as f:
                public_key = serialization.load_pem_public_key(f.read())
            with open(self.private_key_file, "rb") as f:
                private_key = serialization.load_pem_private_key(
                    f.read(), password=None
                )
            self.logger.debug("RSA keys loaded from files.")
            return public_key, private_key
        except Exception as e:
            self.logger.error(f"Exception thrown: {e}\nExiting program...")
            sys.exit()

    def _load_hybrid_keys(self):
        """
        Load the hybrid RSA public and private keys from files.

        Returns
        -------
        tuple
            A tuple containing the hybrid RSA public key and private key.
        """
        try:
            with open(self.hybrid_public_file, "rb") as f:
                public_key = serialization.load_pem_public_key(f.read())
            with open(self.hybrid_private_file, "rb") as f:
                private_key = serialization.load_pem_private_key(
                    f.read(), password=None
                )
            self.logger.debug("Hybrid RSA keys loaded from files.")
            return public_key, private_key
        except Exception as e:
            self.logger.error(f"Exception thrown: {e}\nExiting program...")
            sys.exit()

    def _load_hybrid_aes_key(self):
        """
        Load and decrypt the hybrid AES key from file.

        Returns
        -------
        tuple
            A tuple containing the hybrid AES key and IV.
        """
        try:
            with open(self.hybrid_file, "rb") as f:
                encrypted_data = f.read()
            
            decrypted_data = self.hybrid_private_key.decrypt(
                encrypted_data,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            aes_key = decrypted_data[:32]
            iv = decrypted_data[32:]
            
            self.logger.debug("Hybrid AES key loaded and decrypted.")
            return aes_key, iv
        except Exception as e:
            self.logger.error(f"Exception thrown: {e}\nExiting program...")
            sys.exit()

    def encrypt(self, data):
        """
        Encrypt the given audio data using AES-CFB.

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
        Decrypt the given encrypted audio data using AES-CFB.

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

    def rsa_encrypt(self, data):
        """
        Encrypt data using RSA. Handles data chunking for large files.
        
        Parameters
        ----------
        data : bytes
            The data to encrypt.
            
        Returns
        -------
        bytes
            Encrypted data.
        """
        try:
            chunk_size = 446  # Maximum size for RSA-4096 with OAEP padding
            chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
            
            encrypted_chunks = []
            for chunk in chunks:
                encrypted_chunk = self.public_key.encrypt(
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
            self.logger.error(f"RSA encryption error: {e}")
            return None

    def rsa_decrypt(self, encrypted_data):
        """
        Decrypt RSA encrypted data. Handles chunked data.
        
        Parameters
        ----------
        encrypted_data : bytes
            The encrypted data to decrypt.
            
        Returns
        -------
        bytes
            Decrypted data.
        """
        try:
            chunk_size = 512  # RSA-4096 encrypted chunk size
            chunks = [encrypted_data[i:i + chunk_size] 
                     for i in range(0, len(encrypted_data), chunk_size)]
            
            decrypted_chunks = []
            for chunk in chunks:
                decrypted_chunk = self.private_key.decrypt(
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
            self.logger.error(f"RSA decryption error: {e}")
            return None

    def hybrid_encrypt(self, data):
        """
        Encrypt data using hybrid encryption (RSA + AES).
        
        Parameters
        ----------
        data : bytes
            The data to encrypt.
            
        Returns
        -------
        bytes
            Encrypted data.
        """
        try:
            encryptor = self.hybrid_cipher.encryptor()
            return encryptor.update(data) + encryptor.finalize()
        except Exception as e:
            self.logger.error(f"Hybrid encryption error: {e}")
            return None

    def hybrid_decrypt(self, encrypted_data):
        """
        Decrypt data using hybrid encryption (RSA + AES).
        
        Parameters
        ----------
        encrypted_data : bytes
            The encrypted data to decrypt.
            
        Returns
        -------
        bytes
            Decrypted data.
        """
        try:
            decryptor = self.hybrid_cipher.decryptor()
            return decryptor.update(encrypted_data) + decryptor.finalize()
        except Exception as e:
            self.logger.error(f"Hybrid decryption error: {e}")
            return None


if __name__ == "__main__":
    crypto = CryptoManager()
