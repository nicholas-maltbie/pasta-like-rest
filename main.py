from flask import Flask, jsonify, request
from rooms import rooms_api
from games import games_api
from flask_cors import CORS
from firebase_admin import credentials, initialize_app
import os

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize Firestore DB
cred = credentials.Certificate('secrets/firebase-key.json')
default_app = initialize_app(cred)

cors = CORS(app, resources={r"/*": {"origins": "*"}}, send_wildcard=True)

app.register_blueprint(rooms_api, url_prefix='/rooms')
app.register_blueprint(games_api, url_prefix='/games')

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(threaded=True, host='127.0.0.1', debug=True)

