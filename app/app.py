"""Plaid account management app."""

import os
from flask import Flask, request, jsonify

from plaid_client import create_link_token, exchange_public_token
from accounts import add_account, get_account_summaries, remove_account, clear_accounts
from transactions_sync import sync_all, sync_account, get_sync_history

app = Flask(__name__)


def _template_path(name):
    return os.path.join(os.path.dirname(__file__), '..', 'templates', name)


# ---------- Root page (serves /, /accounts, /sync) ----------
@app.route("/")
@app.route("/accounts")
@app.route("/sync")
def page():
    return open(_template_path('index.html')).read()


# ---------- Sync API ----------
@app.route("/api/sync/run", methods=["POST"])
def run_sync():
    data = request.get_json(silent=True) or {}
    account_id = data.get("account_id")
    if account_id:
        sync_account(account_id)
        return jsonify({"message": "sync started", "account_id": account_id})
    sync_all()
    return jsonify({"message": "sync all started"})


@app.route("/api/sync/history")
def sync_history():
    return jsonify(get_sync_history())


# ---------- API: create a Plaid Link token ----------
@app.route("/api/accounts/link-token", methods=["POST"])
def create_link_token_route():
    return jsonify(create_link_token())


@app.route("/api/accounts", methods=["GET"])
def list_accounts():
    summary = get_account_summaries()
    return jsonify(summary)


@app.route("/api/accounts", methods=["DELETE"])
def delete_accounts():
    account_id = request.args.get("account_id")
    if account_id:
        remove_account(account_id)
    else:
        clear_accounts()
    return "", 204


@app.route("/api/accounts/save", methods=["POST"])
def save_account():
    try:
        data = request.get_json()
        public_token = data['public_token']
        accounts = data['accounts']
        institution = data.get('institution')
    except Exception:
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
            "institution": institution,
            "name": account.get("name"),
            "mask": account.get("mask"),
            "subtype": account.get("subtype"),
        }
        add_account(account_data)

    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4343, debug=True)
