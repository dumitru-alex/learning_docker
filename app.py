# Simple python app using Flask to expose an HTTP web server on localhost on port 5000.
# (5000 is the default port for flask)

# pre-req: pip install flask

# After you run it, you can access it on http://localhost:5000/
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run(host="0.0.0.0") 

