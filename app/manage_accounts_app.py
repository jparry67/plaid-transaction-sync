"""Plaid account management app."""

from flask import Flask, request, jsonify

from plaid_client import create_link_token, exchange_public_token
from accounts_store import add_account

app = Flask(__name__)


# ---------- root page ----------
@app.route("/")
def setup_account():
    return """
<!DOCTYPE html>
<html>
<head>
  <title>Linked Accounts</title>
  <script src="https://cdn.plaid.com/link/v2/stable/link-initialize.js"></script>
  <style>
    body { font-family: sans-serif; max-width: 600px; margin: 40px auto; padding: 0 20px; }
    button { padding: 12px 24px; font-size: 16px; cursor: pointer; }
    #status { margin-top: 16px; }
    .success {color: green; }
    .error { color: red; }
  </style>
</head>
<body>
  <h1>Linked Accounts</h1>
  <p>Link your bank account to sync transactions.</p>
  <button id="open-link">Add account</button>
  <div id="status"></div>

  <script>
    document.getElementById('open-link').addEventListener('click', async () => {
      const status = document.getElementById('status');
      status.textContent = 'Linking accounts…';
      status.className = '';

      try {
        const res = await fetch('/api/create-link-token', { method: 'POST' });
        const { link_token } = await res.json();
        const handler = Plaid.create({
          token: link_token,
          onSuccess: async (public_token, metadata) => {
            try {
              const accountsData = {public_token, accounts: metadata.accounts};
              const addAccountResponse = await fetch('api/save-accounts', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(accountsData)});
              if (addAccountResponse.ok) {
                status.textContent = `${metadata.accounts.map((account) => account.name).join(', ')} linked successfully!`;
                status.className = 'success'; 
              } else {
                status.className = 'error';
                status.textContent = 'Failed to save account data. HTTP error status: ' + addAccountResponse.status;
              }
            } catch (err) {
              status.className = 'error';
              status.textContent = 'Failed to save account data: ' + err.message;
            }
          },
          onLoad: null,
          onExit: (err, metadata) => {
            status.className = 'error';
            status.textContent = 'Exited before linking accounts.';
          },
          onEvent: null,
        });
        handler.open();
      } catch (err) {
        status.className = 'error';
        status.textContent = 'Error: ' + err.message;
      }
    });
  </script>
</body>
</html>
    """


# ---------- API: create a Plaid Link token ----------
@app.route("/api/create-link-token", methods=["POST"])
def create_link_token_route():
    return jsonify(create_link_token())


@app.route("/api/save-accounts", methods=["POST"])
def save_account():
    try:
        data = request.get_json()
        public_token = data['public_token']
        accounts = data['accounts']
    except:
        return jsonify({"error": "Missing required fields or invalid JSON"}), 400
    
    try:
        access_token, item_id = exchange_public_token(public_token)
    except Exception as e:
        print(f"Failed to exchange token: {e}")
        return jsonify({"error": str(e)}), 500

    for account in accounts:
        account_data = {
            "access_token": access_token,
            "item_id": item_id,
            "account_id": account.get("id"),
            "name": account.get("name"),
            "mask": account.get("mask"),
            "subtype": account.get("subtype"),
        }
        add_account(account_data)

    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4343, debug=True)
