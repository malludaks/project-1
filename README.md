#   JWKS Server

## Project Overview
This project is a simple implementation of a JWKS (JSON Web Key Set) server  built in Python using Flask. It serves public keys for verifying JSON Web Tokens (JWTs) and includes features like RSA key generation key expiry  and JWT signing.

# Key Features

- ** JWKS ENDPOINT**: `/well-known/jwks.json` — Returns the public keys in JWKS format.
- **AUTO ENDPOINT**: `/auth` — Issues JWTs with options for expired or unexpired tokens.

- ```bash
pip install -r requirements.txt
python server.py

To run the Gradebot test client: python gradebot.py
Coverage run -m unittest discover
coverage report
