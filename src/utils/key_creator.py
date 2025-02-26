"""
Senior Project : Hardware Encryption Device
Team 312
File : key_creator.py
Description: Utility for creating hybrid encryption keys using existing AES and RSA keys.
"""

import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from pathlib import Path
from src.utils.utils import get_proj_root

class KeyCreator:
    def __init__(self):
        """Initialize KeyCreator with project keys directory."""
        self.keys_dir = Path(get_proj_root()) / "keys"
        self.keys_dir.mkdir(exist_ok=True)

    def verify_base_keys_exist(self):
        """Verify that the required base keys exist."""
        required_files = ["aes.txt", "public_key.pem", "private_key.pem"]
        missing_files = [f for f in required_files 
                        if not (self.keys_dir / f).exists()]
        
        if missing_files:
            raise FileNotFoundError(
                f"Missing required key files: {', '.join(missing_files)}\n"
                f"Please ensure all required keys are in: {self.keys_dir}"
            )
        return True

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
            print("Hybrid keys already exist. Use force=True to overwrite.")
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

            print("Hybrid encryption keys created successfully:")
            print(f"- Hybrid private key: {hybrid_private_path}")
            print(f"- Hybrid public key: {hybrid_public_path}")
            print(f"- Encrypted AES key: {hybrid_encrypted_aes_path}")

        except Exception as e:
            print(f"Error creating hybrid keys: {e}")
            raise

if __name__ == "__main__":
    creator = KeyCreator()
    try:
        creator.verify_base_keys_exist()
        creator.create_hybrid_keys(force=True)
        print("Hybrid key creation completed successfully.")
    except Exception as e:
        print(f"Error: {e}")