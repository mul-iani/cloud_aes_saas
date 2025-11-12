from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

# Ambil key dari environment atau buat baru jika tidak ada
AES_KEY = os.getenv("AES_KEY")

if AES_KEY is None:
    # Jika tidak ada key di .env, buat key acak 32 byte
    key = os.urandom(32)
else:
    # Pastikan panjang key valid (16, 24, 32 byte)
    key_bytes = AES_KEY.encode()
    if len(key_bytes) not in [16, 24, 32]:
        print(f"[WARNING] Panjang AES_KEY tidak valid ({len(key_bytes)}). "
              "Menggunakan key acak 32-byte sebagai gantinya.")
        key = os.urandom(32)
    else:
        key = key_bytes

def encrypt_data(data: bytes) -> bytes:
    """Enkripsi data dengan AES-256 (mode CFB)."""
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted = iv + encryptor.update(data) + encryptor.finalize()
    return encrypted

def decrypt_data(encrypted: bytes) -> bytes:
    """Dekripsi data terenkripsi dengan AES-256 (mode CFB)."""
    iv = encrypted[:16]
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(encrypted[16:]) + decryptor.finalize()
    return decrypted
