import datetime
import uuid
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Dictionary to store all keys along with their expiry times
KEYS = {}

def generate_rsa_key_pair(kid, expiry_minutes=30):
    """
    Generate RSA key pair (private and public) for a given Key ID (kid).
    Key expiry is set to 30 minutes by default.
    
    :param kid: The unique Key ID
    :param expiry_minutes: Time after which the key expires
    :return: Private and public keys in PEM format
    """
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # Generate public key
    public_key = private_key.public_key()
    
    # Convert keys to PEM format (used to transmit data securely)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    # Set expiry time for the key
    expiry_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=expiry_minutes)
    
    # Store the keys and their metadata in the KEYS dictionary
    KEYS[kid] = {
        'private_key': private_pem,
        'public_key': public_pem,
        'expiry': expiry_time,
    }
    
    return private_pem, public_pem
