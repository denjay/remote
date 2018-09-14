from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/")
def hello():
    return "成功"


app.run(port=8765, host="0.0.0.0", debug=True)
