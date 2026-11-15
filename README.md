# plaid-transaction-sync
python scripts to pull financial transactions periodically through plaid

## Setup

### Generate an encryption key

Plaid access tokens are stored encrypted. You need to generate a key and place it in `.env`.

```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy the output into a new `.env` file at the project root:

```
ENCRYPTION_KEY=Abc123...xyz
```

### Run

```bash
docker compose up --build
```
