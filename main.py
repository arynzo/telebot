from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '✅ Home Route is Working!'

@app.route('/send')
def send():
    return '📨 Send Route is Working!'
