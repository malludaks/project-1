from flask import Flask, jsonify, request, make_response
import datetime
import base64
import uuid
import jwt
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

app = Flask(__name__)

# Global storage for keys (mock database)
KEYS = {}

# Helper function to generate RSA key pair
def generate_rsa_key_pair(kid):
    from cryptography.hazmat.primitives.asymmetric import rsa
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
    public_key = private_key.public_key()
    
    # Serialize keys
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    # Save to KEYS dictionary with expiration time
    KEYS[kid] = {
        'private_key': private_pem,
        'public_key': public_pem,
        'expiry': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # 1-hour validity for simplicity
    }

# Helper function to remove expired keys from KEYS
def cleanup_expired_keys():
    """Remove expired keys from KEYS."""
    current_time = datetime.datetime.utcnow()
    expired_keys = [kid for kid, key_data in KEYS.items() if key_data['expiry'] <= current_time]
    for kid in expired_keys:
        del KEYS[kid]

# JWKS endpoint
@app.route('/.well-known/jwks.json', methods=['GET'])
def jwks():
    """ Serve the JWKS set containing all non-expired public keys. """
    cleanup_expired_keys()  # Ensure no expired keys are included
    keys = []
    for kid, key_data in KEYS.items():
        public_key = serialization.load_pem_public_key(key_data['public_key'], backend=default_backend())
        public_numbers = public_key.public_numbers()
        jwk = {
            'kid': kid,
            'kty': 'RSA',
            'alg': 'RS256',
            'use': 'sig',
            'n': base64.urlsafe_b64encode(public_numbers.n.to_bytes((public_numbers.n.bit_length() + 7) // 8, 'big')).decode('utf-8').rstrip("="),
            'e': base64.urlsafe_b64encode(public_numbers.e.to_bytes((public_numbers.e.bit_length() + 7) // 8, 'big')).decode('utf-8').rstrip("="),
        }
        keys.append(jwk)
    
    return jsonify({'keys': keys})

# Authentication endpoint
@app.route('/auth', methods=['POST'])
def auth():
    """ Issue JWTs with optional key compatibility debugging. """
    cleanup_expired_keys()  # Clean up any expired keys before issuing a new token
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return make_response(jsonify({'message': 'Invalid request'}), 400)

    # Generate a new kid for each JWT
    kid = str(uuid.uuid4())
    generate_rsa_key_pair(kid)

    # Determine if the token should be expired
    expired = request.args.get('expired', 'false').lower() == 'true'
    expiration_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=5) if expired else datetime.datetime.utcnow() + datetime.timedelta(minutes=30)

    # Generate JWT with either an expired or valid exp claim
    private_key = serialization.load_pem_private_key(KEYS[kid]['private_key'], password=None, backend=default_backend())
    token = jwt.encode(
        {
            'sub': data['username'],
            'iat': datetime.datetime.utcnow(),
            'exp': expiration_time,
        },
        private_key,
        algorithm='RS256',
        headers={'kid': kid}
    )

    # If the token is set to be expired, remove the key immediately from KEYS
    if expired:
        del KEYS[kid]

    return jsonify({'token': token})

# Protected endpoint
@app.route('/protected', methods=['GET'])
def protected():
    """ A protected endpoint that requires a valid JWT token to access. """
    cleanup_expired_keys()  # Clean up any expired keys before verifying a token
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return make_response(jsonify({'message': 'Missing Authorization Header'}), 401)
    
    token = auth_header.split(" ")[1]
    
    try:
        # Extract kid from JWT header
        kid = jwt.get_unverified_header(token).get('kid')
        if not kid or kid not in KEYS:
            return make_response(jsonify({'message': 'Invalid kid or key not found in JWKS'}), 401)

        # Check key expiration
        key_data = KEYS[kid]
        if key_data['expiry'] <= datetime.datetime.utcnow():
            return make_response(jsonify({'message': 'Key has expired in JWKS'}), 401)

        # Retrieve public key
        public_key = serialization.load_pem_public_key(key_data['public_key'], backend=default_backend())

        # Decode the token with the valid public key
        decoded = jwt.decode(token, public_key, algorithms=['RS256'])
        return jsonify({'message': 'Access granted', 'user': decoded['sub']})
    
    except jwt.ExpiredSignatureError:
        return make_response(jsonify({'message': 'Token has expired'}), 401)
    except jwt.InvalidTokenError as e:
        print(f"DEBUG: Invalid token error: {e}")
        return make_response(jsonify({'message': f'Invalid token: {e}'}), 401)

# Run the Flask application
if __name__ == '__main__':
    app.run(port=8080)
