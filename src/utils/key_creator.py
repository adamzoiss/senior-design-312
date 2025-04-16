"""
Senior Project : Hardware Encryption Device
Team 312
File : key_creator.py
Description: Utility for creating hybrid encryption keys using existing AES and RSA keys.
"""

import shutil
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from pathlib import Path
from src.utils.utils import get_proj_root
from src.logging.logger import *
import os


class KeyCreator:
    def __init__(self):
        """Initialize KeyCreator with project keys directory."""
        self.keys_dir = Path(get_proj_root()) / "keys"
        self.keys_dir.mkdir(exist_ok=True)
        
        # Set up logging
        self.logger: logging = Logger(
            "KeyCreator",
            console_level=logging.INFO,
            console_logging=EN_CONSOLE_LOGGING,
        )

        # Initialize keys during creation
        try:
            self.verify_base_keys_exist()
        except Exception as e:
            self.logger.error(f"Failed to initialize keys: {e}")
            raise

    def verify_base_keys_exist(self, missing = True):
        """
        Search USB drives and copy required key files to the Keys folder.
        If no USB is found, check if keys exist in the system.
        After getting keys from either source, create hybrid keys.

        Parameters
        ----------
        missing : bool
            Determines if any files are missing, throws error if it goes unchanged

        Returns
        -------
        None
            Returns None if successful, raises FileNotFoundError if files are missing
        """        
        from string import ascii_uppercase
        drive_options = [Path(f"{letter}:\\") for letter in ascii_uppercase]    #cycle through connected USB devices, store them in drive_options

        required_files = ["aes.txt", "public_key.pem", "private_key.pem"]
        hybrid_files = ["hybrid_private.pem", "hybrid_public.pem", "hybrid.txt"]

        # First check USB drives
        for drive in drive_options:     #cycle through all USB devices
            missing_files = [f for f in required_files if not (drive / f).exists()]     #check if any required files are missing
            if not missing_files:
                missing = False
                for file in required_files:     #if no required files missing, make copies and send to the Keys folder
                    src = drive / file
                    dest  = self.keys_dir / file
                    shutil.copy2(src, dest)
                self.logger.info("Successfully copied key files from USB")
                # Create hybrid keys after getting keys from USB
                self.create_hybrid_keys(force=True)
                return None
        
        # If no USB keys found, check system keys
        system_keys_exist = all((self.keys_dir / f).exists() for f in required_files)
        if system_keys_exist:
            self.logger.info("No USB keys found, using existing system keys")
            # Check if hybrid keys exist
            hybrid_keys_exist = all((self.keys_dir / f).exists() for f in hybrid_files)
            if not hybrid_keys_exist:
                self.logger.info("Creating hybrid keys from system keys")
                self.create_hybrid_keys(force=True)
            return None
        
        if missing:
            raise FileNotFoundError(
                f"Missing required key files: {', '.join(required_files)}\n"
                f"Please ensure all required keys are in your USB drive or system"
            )
        return None

    def create_hybrid_keys(self, force=False):
        """
        Create hybrid encryption keys using existing AES key.
        Creates new RSA key pair and encrypts AES key with the public key.
        
        Parameters
        ----------
        force : bool
            If True, overwrites existing hybrid keys
        """
        hybrid_private_path = self.keys_dir / "hybrid_private.pem"
        hybrid_public_path = self.keys_dir / "hybrid_public.pem"
        hybrid_encrypted_aes_path = self.keys_dir / "hybrid.txt"
        
        # Check if hybrid keys already exist
        if not force and all(p.exists() for p in [hybrid_private_path, hybrid_public_path, hybrid_encrypted_aes_path]):
            self.logger.info("Hybrid keys already exist. Use force=True to overwrite.")
            return

        try:
            # Read existing AES key and IV
            with open(self.keys_dir / "aes.txt", "r") as f:
                aes_key = bytes.fromhex(f.readline().strip())
                iv = bytes.fromhex(f.readline().strip())

            # Generate new RSA key pair for hybrid encryption
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096
            )
            public_key = private_key.public_key()
            
            self.logger.info("Creating hybrid keys")
            
            # Save hybrid RSA private key
            with open(hybrid_private_path, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))

            # Save hybrid RSA public key
            with open(hybrid_public_path, "wb") as f:
                f.write(public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ))

            # Encrypt AES key and IV with hybrid RSA public key
            encrypted_data = public_key.encrypt(
                aes_key + iv,  # Combine AES key and IV
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            # Save encrypted AES key and IV
            with open(hybrid_encrypted_aes_path, "wb") as f:
                f.write(encrypted_data)

            self.logger.info("Hybrid encryption keys created successfully:")
            self.logger.info(f"- Hybrid private key: {hybrid_private_path}")
            self.logger.info(f"- Hybrid public key: {hybrid_public_path}")
            self.logger.info(f"- Encrypted AES key: {hybrid_encrypted_aes_path}")

            # Verify hybrid keys were created successfully
            if not all(p.exists() for p in [hybrid_private_path, hybrid_public_path, hybrid_encrypted_aes_path]):
                raise FileNotFoundError("Failed to create one or more hybrid key files")

        except FileNotFoundError as e:
            self.logger.error(f"Required keys not found: {e}")
            raise FileNotFoundError("Required keys must exist to create hybrid keys")
        except Exception as e:
            self.logger.error(f"Error creating hybrid keys: {e}")
            raise


if __name__ == "__main__":
    creator = KeyCreator()
    try:
        print("Key verification and hybrid key creation completed successfully.")
    except Exception as e:
        print(f"Error: {e}") 