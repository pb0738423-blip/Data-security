import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEY_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "encryption.key"
)


def get_or_create_key() -> bytes:
    # Vercel: use an environment variable
    env_key = os.environ.get("ENCRYPTION_KEY")

    if env_key:
        return base64.b64decode(env_key)

    # Local development: use the local key file
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as file:
            return file.read()

    key = AESGCM.generate_key(bit_length=256)

    with open(KEY_FILE, "wb") as file:
        file.write(key)

    return key


def encrypt_bytes(data: bytes) -> tuple[bytes, bytes]:
    key = get_or_create_key()
    nonce = os.urandom(12)
    encrypted = AESGCM(key).encrypt(nonce, data, None)
    return nonce, encrypted


def decrypt_bytes(nonce: bytes, encrypted: bytes) -> bytes:
    key = get_or_create_key()
    return AESGCM(key).decrypt(nonce, encrypted, None)


def encode_bytes(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def decode_bytes(data: str) -> bytes:
    return base64.b64decode(data.encode("utf-8"))
