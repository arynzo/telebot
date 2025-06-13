from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '✅ Home Route is Working!'

@app.route('/send')
def send():
    return '📨 Send Route is Working!'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3434)
