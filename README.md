# J W K S   S E R V E R  P R O J E C T

## Project Overview
This project is a simple implementation of a JWKS (JSON Web Key Set) server  built in Python using Flask. It serves public keys for verifying JSON Web Tokens (JWTs) and includes features like RSA key generation key expiry  and JWT signing.

# Key Features

- **J W K S   E N D P O I N T**: `/well-known/jwks.json` — Returns the public keys in JWKS format.
- **A U T H   E N D P O I N T**: `/auth` — Issues JWTs with options for expired or unexpired tokens.

- ```bash
pip install -r requirements.txt
python server.py

To run the Gradebot test client: python gradebot.py
