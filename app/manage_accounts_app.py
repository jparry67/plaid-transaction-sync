from flask import Flask
import threading
import time

app = Flask(__name__)

@app.route('/')
def setup_account():
    return '<h1>Plaid Account Setup</h1><p>Manage Plaid Account Setup</p>'

@app.route('/setup')
def setup_account_setup():
    return '<h1>Plaid Account Setup</h1><p>Account setup page</p>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4343, debug=True)
