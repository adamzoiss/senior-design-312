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
from src.logging.logging_config import *


class CryptoManager:
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

    def __init__(
        self,
        key_file="/keys/aes.txt",
        public_key_file="/keys/public_key.pem",
        private_key_file="/keys/private_key.pem",
    ):
        """
        Initialize the CryptoManager instance.

        Parameters
        ----------
        key_file : str, optional
            Path to the file containing the AES key and IV.
        """
        # Set up logging
        self.logger: logging = setup_logger("CryptoManager")

        self.key_file = str(get_proj_root()) + key_file
        self.private_key_file = str(get_proj_root()) + private_key_file
        self.public_key_file = str(get_proj_root()) + public_key_file

        self.key, self.iv = self._load_key_iv()
        self.public_key, self.private_key = self._load_rsa_keys()
        self.cipher = Cipher(algorithms.AES(self.key), modes.CFB(self.iv))

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

    print("Crypto Manager Program...")
    crypto = CryptoManager()
