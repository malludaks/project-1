from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import datetime

# Store the keys in a global dictionary
KEYS = {}

def generate_rsa_key_pair(kid, expiry_minutes=30):
    """Generate RSA key pair and store in KEYS dictionary."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    public_key = private_key.public_key()
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    expiry_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=expiry_minutes)

    KEYS[kid] = {
        'private_key': private_pem,
        'public_key': public_pem,
        'expiry': expiry_time,
    }

    return private_pem, public_pem
    # Debugging logs
    print(f"Generated Key Pair for kid: {kid}")
    print(f"Public Key: {public_pem.decode()}")
    print(f"Private Key: {private_pem.decode()}")
