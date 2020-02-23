from flask import Flask, jsonify, request
from rooms import rooms_api
from games import games_api
from flask_cors import CORS

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)
CORS(app)

app.register_blueprint(rooms_api, url_prefix='/rooms')
app.register_blueprint(games_api, url_prefix='/games')

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run()

