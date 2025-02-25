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
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

from src.utils.utils import *


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
        self.key_file = str(get_proj_root()) + key_file
        self.private_key_file = str(get_proj_root()) + private_key_file
        self.public_key_file = str(get_proj_root()) + public_key_file

        self.key, self.iv = self._load_key_iv()
        self.public_key, self.private_key = self._load_rsa_keys()
        self.cipher = Cipher(algorithms.AES(self.key), modes.CFB(self.iv))

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
                print("Key and IV loaded from file.")
                return key, iv
        except Exception as e:
            print(f"Exception thrown: {e}\nExiting program...")
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
            print("RSA keys loaded from files.")
            return public_key, private_key
        except Exception as e:
            print(f"Exception thrown: {e}\nExiting program...")
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
    

    ################## Adding stuff for RSA ######################
    def rsa_encrypt_file(self, audio_data, params):
        """
        Encrypt audio file data using RSA.

        Parameters
        ----------
        audio_data : bytes
            The audio data to encrypt
        params : dict
            Dictionary containing audio parameters (channels, sampwidth, framerate)

        Returns
        -------
        bytes
            Encrypted audio data with header information
        """
        try:
            # Convert to numpy array for better handling
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            audio_bytes = audio_array.tobytes()
            
            # Create header with audio parameters
            header = f"{params['channels']},{params['sampwidth']},{params['framerate']},{len(audio_array)}".encode()
            header_len = len(header).to_bytes(4, 'big')

            # Combine header and audio data
            data_to_encrypt = header_len + header + audio_bytes

            # Split into chunks and encrypt
            chunk_size = 444  # 446 - 2 bytes for length prefix
            chunks = [data_to_encrypt[i:i + chunk_size] 
                    for i in range(0, len(data_to_encrypt), chunk_size)]
            
            encrypted_chunks = []
            for chunk in chunks:
                chunk_length = len(chunk).to_bytes(2, 'big')
                chunk_with_length = chunk_length + chunk
                
                encrypted_chunk = self.public_key.encrypt(
                    chunk_with_length,
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
            return audio_data

    def rsa_decrypt_file(self, encrypted_data):
        """
        Decrypt RSA encrypted audio file data.

        Parameters
        ----------
        encrypted_data : bytes
            The encrypted audio data to decrypt.

        Returns
        -------
        tuple
            (decrypted_data, audio_params) where audio_params contains channels, sampwidth, framerate
        """
        try:
            # Split into chunks and decrypt
            chunk_size = 512  # RSA-4096 encrypted chunk size
            encrypted_chunks = [encrypted_data[i:i + chunk_size] 
                            for i in range(0, len(encrypted_data), chunk_size)]
            
            decrypted_chunks = []
            for chunk in encrypted_chunks:
                decrypted_chunk = self.private_key.decrypt(
                    chunk,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                
                chunk_length = int.from_bytes(decrypted_chunk[:2], 'big')
                actual_data = decrypted_chunk[2:2+chunk_length]
                decrypted_chunks.append(actual_data)

            # Combine all decrypted chunks
            decrypted_data = b''.join(decrypted_chunks)

            # Extract header
            header_len = int.from_bytes(decrypted_data[:4], 'big')
            header = decrypted_data[4:4+header_len].decode().split(',')
            channels, sampwidth, framerate, nsamples = map(int, header)

            # Extract audio data
            audio_bytes = decrypted_data[4+header_len:]

            # Convert to numpy array
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
            
            # Ensure correct number of samples
            audio_array = audio_array[:nsamples]
            
            audio_params = {
                'channels': channels,
                'sampwidth': sampwidth,
                'framerate': framerate
            }
            
            return audio_array.tobytes(), audio_params

        except Exception as e:
            print(f"RSA decryption error: {e}")
            return encrypted_data, None

    ################### Hybrid AES and RSA Implementation ################
    def hybrid_encrypt_file(self, audio_data, params):
        """
        Encrypt audio data using hybrid RSA-AES-CFB encryption.
        
        Parameters
        ----------
        audio_data : bytes
            The audio data to encrypt
        params : dict
            Dictionary containing audio parameters
            
        Returns
        -------
        bytes
            Encrypted audio data with all necessary components
        """
        try:
            # Generate AES key and IV
            aes_key = os.urandom(32)
            iv = os.urandom(16)  # CFB uses 16 bytes IV
            
            # Encrypt AES key with RSA
            encrypted_key = self.public_key.encrypt(
                aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            # Encrypt audio data with AES-CFB
            cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
            encryptor = cipher.encryptor()
            encrypted_audio = encryptor.update(audio_data) + encryptor.finalize()
            
            # Save all components
            result = (
                iv +  # 16 bytes for CFB
                len(encrypted_key).to_bytes(4, 'big') +
                encrypted_key +
                encrypted_audio
            )
            
            return result

        except Exception as e:
            print(f"Encryption error: {e}")
            return None

    def hybrid_decrypt_file(self, encrypted_data):
        """
        Decrypt hybrid RSA-AES-CFB encrypted audio data.
        
        Parameters
        ----------
        encrypted_data : bytes
            The encrypted data to decrypt
            
        Returns
        -------
        bytes
            Decrypted audio data
        """
        try:
            # Read the components
            iv = encrypted_data[:16]
            key_len = int.from_bytes(encrypted_data[16:20], 'big')
            encrypted_key = encrypted_data[20:20+key_len]
            encrypted_audio = encrypted_data[20+key_len:]

            # Decrypt the AES key
            aes_key = self.private_key.decrypt(
                encrypted_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            # Decrypt the audio data using AES-CFB
            cipher = Cipher(algorithms.AES(aes_key), modes.CFB(iv))
            decryptor = cipher.decryptor()
            decrypted_audio = decryptor.update(encrypted_audio) + decryptor.finalize()

            return decrypted_audio

        except Exception as e:
            print(f"Decryption error: {e}")
        return None

if __name__ == "__main__":

    print("Crypto Manager Program...")
    crypto = CryptoManager()
