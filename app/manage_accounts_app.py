"""Plaid account management app."""

from flask import Flask, jsonify

from plaid_client import create_link_token

app = Flask(__name__)


# ---------- root page ----------
@app.route("/")
def setup_account():
    return """
<!DOCTYPE html>
<html>
<head>
  <title>Plaid Linked Accounts</title>
  <script src="https://cdn.plaid.com/link/v2/stable/link-initialize.js"></script>
  <style>
    body { font-family: sans-serif; max-width: 600px; margin: 40px auto; padding: 0 20px; }
    button { padding: 12px 24px; font-size: 16px; cursor: pointer; }
    #status { margin-top: 16px; }
    .error { color: red; }
  </style>
</head>
<body>
  <h1>Plaid Linked Accounts</h1>
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
          onSuccess: (public_token, metadata) => {
            console.log('onSuccess', public_token);
            metadata.accounts.forEach((account) => {
              console.log(account.id, account.mask, account.name, account.subtype);
            });
            status.textContent = 'Account linked successfully!';
            status.style.color = 'green'; 
          },
          onLoad: null,
          onExit: (err, metadata) => {
            status.className = 'error';
            status.textContent = 'Exited before linking accounts.';
            console.log('onExit', err, metadata);
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4343, debug=True)
