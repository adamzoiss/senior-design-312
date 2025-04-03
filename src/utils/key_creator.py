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

    def verify_base_keys_exist(self, missing = True):
        """
        Search USB drives and copy required key files to the Keys folder.
        If no USB is found, check if keys exist in the system.

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
                return None
        
        # If no USB keys found, check system keys
        system_keys_exist = all((self.keys_dir / f).exists() for f in required_files)
        if system_keys_exist:
            self.logger.info("No USB keys found, using existing system keys")
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
            # First try to use existing system keys
            try:
                # Read existing AES key and IV
                with open(self.keys_dir / "aes.txt", "r") as f:
                    aes_key = bytes.fromhex(f.readline().strip())
                    iv = bytes.fromhex(f.readline().strip())
                
                # Read existing RSA keys
                with open(self.keys_dir / "public_key.pem", "rb") as f:
                    public_key = serialization.load_pem_public_key(f.read())
                with open(self.keys_dir / "private_key.pem", "rb") as f:
                    private_key = serialization.load_pem_private_key(f.read(), password=None)
                
                self.logger.info("Using existing system keys for hybrid key creation")
                
            except FileNotFoundError:
                # If system keys don't exist, generate new ones
                self.logger.info("Generating new keys for hybrid encryption")
                # Generate new RSA key pair for hybrid encryption
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=4096
                )
                public_key = private_key.public_key()
                
                # Generate new AES key and IV
                aes_key = os.urandom(32)  # 256-bit AES key
                iv = os.urandom(16)       # 128-bit IV
                
                # Save the new AES key and IV
                with open(self.keys_dir / "aes.txt", "w") as f:
                    f.write(f"{aes_key.hex()}\n{iv.hex()}\n")
                
                # Save the new RSA keys
                with open(self.keys_dir / "public_key.pem", "wb") as f:
                    f.write(public_key.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    ))
                with open(self.keys_dir / "private_key.pem", "wb") as f:
                    f.write(private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption()
                    ))

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

        except Exception as e:
            self.logger.error(f"Error creating hybrid keys: {e}")
            raise


if __name__ == "__main__":
    creator = KeyCreator()
    try:
        creator.verify_base_keys_exist()
        creator.create_hybrid_keys(force=True)
        print("Hybrid key creation completed successfully.")
    except Exception as e:
        print(f"Error: {e}") 