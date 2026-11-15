"""
Lightweight encryption helper.

Usage:
from app.encryption import encrypt, decrypt

encrypted = encrypt(token)
decrypted = decrypt(encrypted)
"""

from cryptography.fernet import Fernet
from dotenv import load_dotenv

import base64
import hashlib
import os

load_dotenv()

_KEY = os.getenv("ENCRYPTION_KEY")
if _KEY is None:
    raise RuntimeError(
        "ENCRYPTION_KEY is not set. "
        "Plaid access tokens will not be encrypted. "
        "Add it to your .env file or export it."
    )

_FERNET = Fernet(
    base64.urlsafe_b64encode(hashlib.sha256(_KEY.encode()).digest())
)


def encrypt(text: str) -> str:
    """Encrypt a plaintext string and return the ciphertext."""
    encrypted_bytes = _FERNET.encrypt(text.encode("utf-8"))
    return encrypted_bytes.decode("ascii")


def decrypt(token: str) -> str:
    """Decrypt a ciphertext string back to plaintext."""
    decrypted_bytes = _FERNET.decrypt(token.encode("ascii"))
    return decrypted_bytes.decode("utf-8")
