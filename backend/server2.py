from flask import Flask, request 
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
app.run(host="0.0.0.0", port=5000, debug=True)
@app.route("/api", methods=["GET", "POST"])
def index():
    return "Hello World!"

